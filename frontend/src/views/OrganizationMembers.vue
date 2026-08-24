<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <DocsHint path="/gerer-les-membres" search="Gestion des membres">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Gestion des membres</h1>
        </DocsHint>
        <p class="mt-2 text-sm text-gray-600">{{ organization?.name }}</p>
      </div>
    </header>

    <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
      <p class="text-sm text-red-800">{{ error }}</p>
    </div>

    <!-- Role Explanation -->
    <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-semibold text-blue-800">Comprendre les rôles</h3>
          <div class="mt-2 text-sm text-blue-700">
            <ul role="list" class="list-disc space-y-1 pl-5">
              <li>
                <span class="font-medium">Lecteur :</span> Accès en lecture seule aux événements (y compris privés/internes).
                <br><span class="text-blue-600 italic">Exemple : Un membre du bureau curieux mais qui n'a pas de raison de créer des événements.</span>
              </li>
              <li>
                <span class="font-medium">Editeur :</span> Peut créer et proposer des événements.
                <br><span class="text-blue-600 italic">Exemple : Un membre du pôle communication qui peut être amené à créer des événements.</span>
              </li>
              <li>
                <span class="font-medium">Administrateur :</span> Gestion totale (membres, paramètres, validation d'événements).
                <br><span class="text-blue-600 italic">Exemple : Le président, responsable communication ou responsable campagne.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Roster confidentiality -->
    <div v-if="canEdit" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900">Confidentialité de la liste des membres</h2>
      <p class="mt-1 text-sm text-gray-500">
        Masquer toute la liste aux étudiants des années sélectionnées. Les membres de l'organisation,
        ses administrateurs et les superadministrateurs conservent toujours un accès complet.
      </p>
      <div class="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <button
          v-for="year in studentYears"
          :key="year"
          type="button"
          role="switch"
          :aria-checked="organizationHiddenFromYears.includes(year)"
          :disabled="visibilitySaving !== null"
          class="flex items-center justify-between rounded-md border px-3 py-2 text-sm font-medium transition-colors disabled:opacity-50"
          :class="organizationHiddenFromYears.includes(year)
            ? 'border-amber-400 bg-amber-50 text-amber-800'
            : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'"
          @click="toggleOrganizationVisibility(year)"
        >
          <span>{{ year }}{{ year === 1 ? 're' : 'e' }} année</span>
          <span
            class="relative inline-flex h-5 w-9 flex-shrink-0 rounded-full transition-colors"
            :class="organizationHiddenFromYears.includes(year) ? 'bg-amber-500' : 'bg-gray-300'"
          >
            <span
              class="inline-block h-4 w-4 translate-y-0.5 rounded-full bg-white shadow transition-transform"
              :class="organizationHiddenFromYears.includes(year) ? 'translate-x-[18px]' : 'translate-x-0.5'"
            />
          </span>
        </button>
      </div>
    </div>

    <!-- Add Member Form -->
    <div v-if="canEdit" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Ajouter un membre</h2>
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 min-w-0">
          <UserSearchSelector
            placeholder="Rechercher un utilisateur par nom ou email..."
            @select="onUserSelect"
          />
        </div>
        <div class="w-full sm:w-48">
          <input 
            v-model="newMemberTitle" 
            type="text" 
            placeholder="Poste (ex: Président)" 
            class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          />
        </div>
        <Dropdown
          v-model="newMemberRole"
          :options="[
            { value: Role.ORG_VIEWER, label: 'Lecteur' },
            { value: Role.ORG_MEMBER, label: 'Éditeur' },
            { value: Role.ORG_ADMIN, label: 'Administrateur' }
          ]"
        />
      </div>
      <p class="mt-2 text-xs text-gray-500">
        Note : La personne doit s'être connectée au moins une fois pour apparaître dans la liste.
      </p>
    </div>

    <!-- Members List -->
    <div id="org-members-list" class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div v-if="loadingMembers" class="text-center py-12">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <div v-else-if="members.length === 0" class="text-center py-12">
        <p class="text-sm text-gray-500">Aucun membre</p>
      </div>

      <ul v-else class="divide-y divide-gray-200">
        <li
          v-for="(member, index) in members"
          :key="member.id"
          :id="`member-row-${member.id}`"
          class="p-4 sm:p-6 transition-colors"
          :class="{'bg-gray-50 ring-2 ring-indigo-500 ring-inset': dragIndex === index}"
          :draggable="canEdit"
          @dragstart="canEdit && onDragStart(index, $event)"
          @dragover.prevent
          @drop="canEdit && onDrop(index)"
          @dragend="dragIndex = null"
        >
          <div class="flex flex-col sm:flex-row sm:items-center justify-between">
            <div class="flex items-center space-x-3">
              <!-- Desktop Drag Handle -->
              <div v-if="canEdit" class="hidden sm:block cursor-grab hover:text-indigo-600 text-gray-400 touch-none flex-shrink-0" title="Maintenir pour réorganiser">
                <Bars3Icon class="h-5 w-5" />
              </div>
              <!-- Mobile Up/Down Arrows -->
              <div v-if="canEdit" class="flex flex-col sm:hidden flex-shrink-0 mr-2 -ml-2">
                 <button
                  @click.stop="moveMember(index, -1)"
                  :disabled="index === 0"
                  class="p-1 text-gray-400 hover:text-indigo-600 disabled:opacity-30 disabled:hover:text-gray-400"
                  title="Monter"
                 >
                    <ChevronUpIcon class="h-5 w-5" />
                 </button>
                 <button
                  @click.stop="moveMember(index, 1)"
                  :disabled="index === members.length - 1"
                  class="p-1 text-gray-400 hover:text-indigo-600 disabled:opacity-30 disabled:hover:text-gray-400"
                  title="Descendre"
                 >
                    <ChevronDownIcon class="h-5 w-5" />
                 </button>
              </div>
              <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                <img v-if="member.profile_picture_file || member.profile_picture_url" :src="(resolveMediaUrl(member.profile_picture_file, 64) ?? member.profile_picture_url) ?? undefined" :alt="getFullName(member)" class="h-full w-full object-cover" />
                <span v-else class="text-gray-600 font-medium text-sm">
                  {{ getInitials(getFullName(member)) }}
                </span>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ getFullName(member) }}
                  <span v-if="member.user_id === currentUserId" class="text-xs text-indigo-600 font-normal">(vous)</span>
                </p>
                <p class="text-xs text-gray-500">{{ member.email }}</p>
              </div>
            </div>

            <div class="mt-2 sm:mt-0 flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full sm:w-auto">
              <template v-if="canEdit">
                <input
                  :value="member.title"
                  @change="updateMemberTitle(member, ($event.target as HTMLInputElement).value)"
                  type="text"
                  placeholder="Poste"
                  class="block w-full sm:w-32 rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
                <Dropdown
                  :model-value="member.role"
                  @update:model-value="updateMemberRole(member, $event)"
                  :options="[
                    { value: Role.ORG_VIEWER, label: 'Lecteur' },
                    { value: Role.ORG_MEMBER, label: 'Éditeur' },
                    { value: Role.ORG_ADMIN, label: 'Administrateur' }
                  ]"
                />

                <button
                  v-if="hasHelloAsso"
                  @click="togglePaymentPermission(member)"
                  :title="member.can_manage_payment_forms ? 'Retirer la permission de gestion des paiements' : 'Accorder la permission de gestion des paiements'"
                  class="flex items-center gap-1 text-xs px-2 py-1 rounded-md border transition-colors"
                  :class="member.can_manage_payment_forms
                    ? 'border-green-400 text-green-700 bg-green-50 hover:bg-green-100'
                    : 'border-gray-300 text-gray-400 bg-white hover:bg-gray-50'"
                >
                  <CreditCardIcon class="h-4 w-4" />
                  <span class="hidden lg:inline">Paiements</span>
                </button>

                <button
                  @click="removeMember(member)"
                  class="text-red-600 hover:text-red-700"
                  title="Retirer ce membre"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </template>
              <template v-else>
                <span v-if="member.title" class="text-sm text-gray-700">{{ member.title }}</span>
                <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset"
                  :class="getRoleBadgeClass(member.role)">
                  {{ getRoleLabel(member.role) }}
                </span>
              </template>

              <button
                v-if="member.user_id === currentUserId"
                @click="openTransferModal(member)"
                class="flex items-center gap-1 text-xs px-2 py-1 rounded-md border border-indigo-300 text-indigo-700 bg-indigo-50 hover:bg-indigo-100 transition-colors"
                title="Transférer ce poste à un·e remplaçant·e"
              >
                <ArrowRightCircleIcon class="h-4 w-4" />
                <span>Transférer mon poste</span>
              </button>
              <button
                v-else-if="canEdit"
                @click="openTransferModal(member)"
                class="flex items-center gap-1 text-xs px-2 py-1 rounded-md border border-gray-300 text-gray-600 bg-white hover:bg-gray-50 transition-colors"
                title="Assigner un·e remplaçant·e pour ce poste"
              >
                <ArrowRightCircleIcon class="h-4 w-4" />
                <span class="hidden lg:inline">Passation</span>
              </button>
            </div>
          </div>
          <div v-if="canEdit" class="mt-3 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-3 sm:ml-8">
            <span class="text-xs text-gray-500">Masquer ce membre aux :</span>
            <button
              v-for="year in studentYears"
              :key="year"
              type="button"
              :aria-pressed="member.hidden_from_years.includes(year)"
              :disabled="visibilitySaving !== null"
              class="rounded-full border px-2.5 py-1 text-xs font-medium transition-colors disabled:opacity-50"
              :class="member.hidden_from_years.includes(year)
                ? 'border-amber-400 bg-amber-50 text-amber-800'
                : 'border-gray-300 bg-white text-gray-500 hover:bg-gray-50'"
              @click="toggleMemberVisibility(member, year)"
            >
              {{ year }}{{ year === 1 ? 're' : 'e' }} année
            </button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Transfer Modal -->
    <TransitionRoot as="template" :show="showTransferModal">
      <Dialog as="div" class="relative z-50" @close="closeTransferModal">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>
        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative w-full max-w-lg transform rounded-lg bg-white p-6 shadow-xl transition-all text-left">
                <DialogTitle as="h3" class="text-base font-semibold text-gray-900">
                  Transférer le poste{{ transferTargetMember?.title ? ` « ${transferTargetMember.title} »` : '' }}
                </DialogTitle>
                <p class="mt-1 text-sm text-gray-500">
                  Actuellement occupé par {{ transferTargetMember ? getFullName(transferTargetMember) : '' }}.
                  Choisissez un ou plusieurs remplaçant·e·s ; le rôle ({{ transferTargetMember ? getRoleLabel(transferTargetMember.role) : '' }})
                  est conservé à l'identique, seul l'intitulé du poste peut être ajusté (ex. masculiniser/féminiser).
                </p>

                <div class="mt-4 space-y-3">
                  <div v-for="(row, i) in transferRows" :key="row.user.id" class="flex items-center gap-2 bg-gray-50 rounded-md p-2">
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ row.user.full_name || row.user.email }}</p>
                      <input
                        v-model="row.title"
                        type="text"
                        placeholder="Intitulé du poste"
                        class="mt-1 block w-full rounded-md border-0 px-2 py-1 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                      />
                    </div>
                    <button @click="transferRows.splice(i, 1)" class="text-gray-400 hover:text-red-600" title="Retirer">
                      <XMarkIcon class="h-5 w-5" />
                    </button>
                  </div>

                  <UserSearchSelector
                    placeholder="Rechercher un·e remplaçant·e..."
                    :filter="(u: { id: string }) => !members.some(m => m.user_id === u.id) && !transferRows.some(r => r.user.id === u.id)"
                    @select="addTransferRow"
                  />
                  <p class="text-xs text-gray-400">Vous pouvez ajouter un·e ou plusieurs remplaçant·e·s. Une personne déjà membre de l'organisation ne peut pas être choisie ici : modifiez directement son adhésion depuis la liste.</p>
                </div>

                <div v-if="transferError" class="mt-4 rounded-md bg-red-50 p-3">
                  <p class="text-sm text-red-800">{{ transferError }}</p>
                </div>

                <div class="mt-6 flex justify-end gap-3">
                  <button type="button" @click="closeTransferModal"
                    class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    Annuler
                  </button>
                  <button type="button" @click="submitTransfer" :disabled="transferSubmitting"
                    :class="transferRows.length === 0
                      ? 'rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 disabled:opacity-50'
                      : 'rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50'">
                    {{ transferSubmitting ? 'Envoi...' : (transferRows.length === 0 ? transferDeleteLabel : 'Confirmer le transfert') }}
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { TrashIcon, Bars3Icon, ChevronUpIcon, ChevronDownIcon, CreditCardIcon, ArrowRightCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import UserSearchSelector from '../components/UserSearchSelector.vue'
import Dropdown from '../components/Dropdown.vue'
import { api } from '@/api'
import type { OrganizationRead, OrgMember, LDAPUserRead } from '@/api/types'
import { Role } from '@/api/types'
import { resolveMediaUrl } from '../utils/media.js'

// Backend returns short English codes for action messages; translate them here.
const MESSAGE_TRANSLATIONS: Record<string, string> = {
  membership_transferred: 'Poste transféré avec succès',
  membership_removed: 'Poste supprimé',
  request_sent: 'Demande envoyée',
}
const translateMessage = (code: string) => MESSAGE_TRANSLATIONS[code] || code

// Same idea for error codes returned in the "detail" field.
const ERROR_TRANSLATIONS: Record<string, string> = {
  successor_already_member: "Cette personne est déjà membre de l'organisation. Pour lui attribuer ce poste, modifiez directement son adhésion depuis la liste des membres (réservé aux administrateur·rice·s).",
}
const translateError = (detail: string | undefined, fallback: string) => {
  if (!detail) return fallback
  return ERROR_TRANSLATIONS[detail] || detail
}

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const organization = ref<OrganizationRead | null>(null)
const members = ref<OrgMember[]>([])
const selectedUser = ref<LDAPUserRead | null>(null)
const newMemberRole = ref<Role>(Role.ORG_MEMBER)
const newMemberTitle = ref('')
const loading = ref(false)
const loadingMembers = ref(false)
const error = ref('')
const canEdit = ref(false)
const studentYears = [1, 2, 3]
const organizationHiddenFromYears = ref<number[]>([])
const visibilitySaving = ref<string | null>(null)

const currentUserId = computed(() => user.value?.id)
const hasHelloAsso = ref(false)

const dragIndex = ref<number | null>(null)

const onDragStart = (index: number, event: DragEvent) => {
  dragIndex.value = index
  event.dataTransfer!.effectAllowed = 'move'
}

const onDrop = async (dropIndex: number) => {
  if (dragIndex.value === null || dragIndex.value === dropIndex) return
  
  const originalMembers = [...members.value]
  const draggedItem = members.value.splice(dragIndex.value, 1)[0]
  members.value.splice(dropIndex, 0, draggedItem)
  dragIndex.value = null
  
  await saveOrder(originalMembers)
}

const moveMember = async (index: number, direction: number) => {
  if (index + direction < 0 || index + direction >= members.value.length) return
  
  const originalMembers = [...members.value]
  const newIndex = index + direction
  
  // Swap elements
  const temp = members.value[index]
  members.value[index] = members.value[newIndex]
  members.value[newIndex] = temp
  
  await saveOrder(originalMembers)
}

const saveOrder = async (originalMembers: OrgMember[]) => {
  try {
    const membershipIds = members.value.map(m => m.id)
    await api.organizations.reorder_organization_members(route.params.id as string, membershipIds)
  } catch (err) {
    console.error('Failed to save order:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de sauvegarder le nouvel ordre'
    members.value = originalMembers
    await loadMembers()
  }
}

const getFullName = (member: OrgMember) => {
  if (member.full_name) {
    return member.full_name
  }
  return member.email || 'Inconnu'
}

const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(/\s+/)
    .map((word: string) => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

const getRoleLabel = (role: string): string => {
  const labels: Record<string, string> = {
    org_admin: 'Administrateur',
    org_member: 'Éditeur',
    org_viewer: 'Lecteur',
  }
  return labels[role] ?? role
}

const getRoleBadgeClass = (role: string): string => {
  const classes: Record<string, string> = {
    org_admin: 'bg-blue-50 text-blue-700 ring-blue-700/10',
    org_member: 'bg-green-50 text-green-700 ring-green-600/20',
    org_viewer: 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  }
  return classes[role] ?? 'bg-gray-50 text-gray-700 ring-gray-600/20'
}

const loadOrganization = async () => {
  try {
    organization.value = await api.organizations.get_organization(route.params.id as string)
    await checkHelloAsso(organization.value)
  } catch (err) {
    console.error('Failed to load organization:', err)
    error.value = 'Impossible de charger l\'organisation'
  }
}

const checkCanEdit = async () => {
  try {
    const res = await api.organizations.can_edit_organization(route.params.id as string)
    canEdit.value = res.can_edit
  } catch (err) {
    console.error('Failed to check edit permission:', err)
  }
}

const checkHelloAsso = async (org: OrganizationRead) => {
  try {
    // Check the org itself, and its parent if it has one
    const ids = [org.id]
    if (org.parent_id) ids.push(org.parent_id)
    const results = await Promise.all(ids.map(id => api.helloasso.helloasso_status(id).catch(() => ({ connected: false }))))
    hasHelloAsso.value = results.some(r => r.connected)
  } catch {
    hasHelloAsso.value = false
  }
}

const loadMembers = async () => {
  loadingMembers.value = true
  try {
    members.value = await api.organizations.get_organization_members(route.params.id as string)
  } catch (err) {
    console.error('Failed to load members:', err)
    error.value = 'Impossible de charger les membres'
  } finally {
    loadingMembers.value = false
  }
}

const loadMemberVisibility = async () => {
  try {
    const settings = await api.organizations.get_member_visibility(route.params.id as string)
    organizationHiddenFromYears.value = settings.hidden_from_years
  } catch (err) {
    console.error('Failed to load member visibility settings:', err)
    error.value = 'Impossible de charger les paramètres de confidentialité'
  }
}

const toggledYears = (years: number[], year: number): number[] =>
  years.includes(year)
    ? years.filter(item => item !== year)
    : [...years, year].sort()

const toggleOrganizationVisibility = async (year: number) => {
  visibilitySaving.value = 'organization'
  error.value = ''
  try {
    const settings = await api.organizations.update_member_visibility(
      route.params.id as string,
      toggledYears(organizationHiddenFromYears.value, year),
    )
    organizationHiddenFromYears.value = settings.hidden_from_years
  } catch (err) {
    console.error('Failed to update member visibility settings:', err)
    error.value = 'Impossible de modifier les paramètres de confidentialité'
  } finally {
    visibilitySaving.value = null
  }
}

const toggleMemberVisibility = async (member: OrgMember, year: number) => {
  visibilitySaving.value = member.id
  error.value = ''
  try {
    const settings = await api.organizations.update_membership_visibility(
      route.params.id as string,
      member.id,
      toggledYears(member.hidden_from_years, year),
    )
    member.hidden_from_years = settings.hidden_from_years
  } catch (err) {
    console.error('Failed to update membership visibility settings:', err)
    error.value = 'Impossible de modifier la confidentialité de ce membre'
  } finally {
    visibilitySaving.value = null
  }
}

const onUserSelect = async (user: LDAPUserRead) => {
  selectedUser.value = user
  await addMember()
}

const addMember = async () => {
  if (!selectedUser.value) return
  
  loading.value = true
  error.value = ''

  try {
    await api.organizations.add_organization_member(
      route.params.id as string,
      selectedUser.value.email,
      newMemberRole.value,
      newMemberTitle.value || undefined
    )
    
    selectedUser.value = null
    newMemberRole.value = Role.ORG_MEMBER
    newMemberTitle.value = ''
    await loadMembers()
  } catch (err) {
    console.error('Failed to add member:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible d\'ajouter le membre'
  } finally {
    loading.value = false
  }
}

const updateMemberRole = async (member: OrgMember, newRole: Role) => {
  try {
    await api.organizations.update_member_role(route.params.id as string, member.id, { role: newRole })
    await loadMembers()
  } catch (err) {
    console.error('Failed to update role:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de modifier le rôle'
  }
}

const updateMemberTitle = async (member: OrgMember, newTitle: string) => {
  try {
    await api.organizations.update_member_role(route.params.id as string, member.id, { title: newTitle || undefined })
    await loadMembers()
  } catch (err) {
    console.error('Failed to update title:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de modifier le poste'
  }
}

const togglePaymentPermission = async (member: OrgMember) => {
  try {
    await api.organizations.update_member_role(route.params.id as string, member.id, { can_manage_payment_forms: !member.can_manage_payment_forms })
    await loadMembers()
  } catch (err) {
    console.error('Failed to update payment permission:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de modifier la permission de paiement'
  }
}

const removeMember = async (member: OrgMember) => {
  if (!confirm(`Êtes-vous sûr de vouloir retirer ${member.full_name || member.email} ?`)) {
    return
  }

  try {
    await api.organizations.remove_organization_member(route.params.id as string, member.id)
    await loadMembers()
  } catch (err) {
    console.error('Failed to remove member:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de retirer le membre'
  }
}

// ─── Transfer (passation) ────────────────────────────────────────────────

interface TransferSuccessorRow {
  user: { id: string; email: string; full_name: string | null }
  title: string
}

const showTransferModal = ref(false)
const transferTargetMember = ref<OrgMember | null>(null)
const transferRows = ref<TransferSuccessorRow[]>([])
const transferSubmitting = ref(false)
const transferError = ref('')

const openTransferModal = (member: OrgMember) => {
  transferTargetMember.value = member
  transferRows.value = []
  transferError.value = ''
  showTransferModal.value = true
}

const closeTransferModal = () => {
  showTransferModal.value = false
  transferTargetMember.value = null
  transferRows.value = []
  transferError.value = ''
}

const addTransferRow = (selected: { id: string; email: string; full_name: string | null }) => {
  if (transferRows.value.some(r => r.user.id === selected.id)) return
  if (members.value.some(m => m.user_id === selected.id)) return
  transferRows.value.push({
    user: selected,
    title: transferTargetMember.value?.title || '',
  })
}

const transferDeleteLabel = computed(() =>
  transferTargetMember.value?.user_id === currentUserId.value ? 'Supprimer mon poste' : 'Supprimer ce poste'
)

const submitTransfer = async () => {
  if (!transferTargetMember.value) return

  if (transferRows.value.length === 0) {
    const isSelf = transferTargetMember.value.user_id === currentUserId.value
    const warning = isSelf
      ? "Vous n'avez choisi aucun·e remplaçant·e : votre poste va être supprimé sans être transmis à personne. Cette action est irréversible. Continuer ?"
      : `Aucun·e remplaçant·e choisi·e : le poste de ${getFullName(transferTargetMember.value)} va être supprimé sans être transmis à personne. Cette action est irréversible. Continuer ?`
    if (!confirm(warning)) return
  }

  transferSubmitting.value = true
  transferError.value = ''
  try {
    const successors = transferRows.value.map(r => ({
      user_id: r.user.id,
      title: r.title || undefined,
    }))
    const res = await api.organizations.transfer_membership(
      route.params.id as string,
      transferTargetMember.value.id,
      successors,
    )
    closeTransferModal()
    await loadMembers()
    alert(translateMessage(res.message))
  } catch (err) {
    console.error('Failed to transfer membership:', err)
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    transferError.value = translateError(detail, 'Impossible de transférer ce poste')
  } finally {
    transferSubmitting.value = false
  }
}

// Prefill the transfer modal when arriving from a "request-transfer" e-mail link
// (?transfer_membership=<id>&transfer_to=<user_id>), or scroll to a specific row when
// arriving from the superadmin mandate-reminder e-mail (#mandate).
const applyDeepLinks = async () => {
  const membershipId = route.query.transfer_membership as string | undefined
  const transferToUserId = route.query.transfer_to as string | undefined

  if (membershipId && transferToUserId) {
    const targetMember = members.value.find(m => m.id === membershipId)
    if (targetMember) {
      try {
        const requester = await api.users.get_user_profile(transferToUserId)
        openTransferModal(targetMember)
        addTransferRow({ id: requester.id, email: requester.email, full_name: requester.full_name })
      } catch (err) {
        console.error('Failed to load transfer requester profile:', err)
      }
    }
    // Clean up the URL so a page refresh doesn't reopen the modal
    router.replace({ query: {} })
  } else if (route.hash === '#mandate') {
    await nextTick()
    document.getElementById('org-members-list')?.scrollIntoView({ behavior: 'smooth' })
  }
}

onMounted(async () => {
  loadOrganization()
  await checkCanEdit()
  if (canEdit.value) await loadMemberVisibility()
  await loadMembers()
  await applyDeepLinks()
})
</script>
