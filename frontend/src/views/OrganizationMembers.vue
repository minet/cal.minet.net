<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Gestion des membres</h1>
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

    <!-- Add Member Form -->
    <div class="bg-white shadow-sm rounded-lg p-6 mb-6">
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
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
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
          class="p-4 sm:p-6 transition-colors"
          :class="{'bg-gray-50 ring-2 ring-indigo-500 ring-inset': dragIndex === index}"
          draggable="true"
          @dragstart="onDragStart(index, $event)"
          @dragover.prevent
          @drop="onDrop(index)"
          @dragend="dragIndex = null"
        >
          <div class="flex flex-col sm:flex-row sm:items-center justify-between">
            <div class="flex items-center space-x-3">
              <!-- Desktop Drag Handle -->
              <div class="hidden sm:block cursor-grab hover:text-indigo-600 text-gray-400 touch-none flex-shrink-0" title="Maintenir pour réorganiser">
                <Bars3Icon class="h-5 w-5" />
              </div>
              <!-- Mobile Up/Down Arrows -->
              <div class="flex flex-col sm:hidden flex-shrink-0 mr-2 -ml-2">
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
                </p>
                <p class="text-xs text-gray-500">{{ member.email }}</p>
              </div>
            </div>

            <div class="mt-2 sm:mt-0 flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full sm:w-auto">
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
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { TrashIcon, Bars3Icon, ChevronUpIcon, ChevronDownIcon, CreditCardIcon } from '@heroicons/vue/24/outline'
import UserSearchSelector from '../components/UserSearchSelector.vue'
import Dropdown from '../components/Dropdown.vue'
import { api } from '@/api'
import type { OrganizationRead, OrgMember, LDAPUserRead } from '@/api/types'
import { Role } from '@/api/types'
import { resolveMediaUrl } from '../utils/media.js'

const route = useRoute()
const { user } = useAuth()
const organization = ref<OrganizationRead | null>(null)
const members = ref<OrgMember[]>([])
const selectedUser = ref<LDAPUserRead | null>(null)
const newMemberRole = ref<Role>(Role.ORG_MEMBER)
const newMemberTitle = ref('')
const loading = ref(false)
const loadingMembers = ref(false)
const error = ref('')

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



const loadOrganization = async () => {
  try {
    organization.value = await api.organizations.get_organization(route.params.id as string)
    await checkHelloAsso(organization.value)
  } catch (err) {
    console.error('Failed to load organization:', err)
    error.value = 'Impossible de charger l\'organisation'
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

onMounted(() => {
  loadOrganization()
  loadMembers()
})
</script>
