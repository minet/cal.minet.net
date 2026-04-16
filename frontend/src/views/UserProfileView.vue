<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-sm text-gray-500">Chargement...</p>
  </div>

  <div v-else-if="profileUser">
    <!-- Superadmin Administration Panel -->
    <div v-if="isSuperAdmin && !isCurrentUser" class="bg-purple-50 border border-purple-200 rounded-lg mb-6 p-4">
      <h2 class="text-lg font-semibold text-purple-900 mb-4 flex items-center">
        <ShieldCheckIcon class="h-5 w-5 mr-2" />
        Administration
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Status Toggle -->
        <div class="bg-white p-4 rounded-md shadow-sm">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Statut Superadmin</h3>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">Accès complet à la plateforme</span>
            <Switch :modelValue="profileUser.is_superadmin" @update:modelValue="toggleSuperadmin"
              :class="[profileUser.is_superadmin ? 'bg-purple-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2']">
              <span class="sr-only">Toggle superadmin</span>
              <span aria-hidden="true"
                :class="[profileUser.is_superadmin ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
            </Switch>
          </div>
        </div>

        <!-- LDAP Exempt Toggle -->
        <div class="bg-white p-4 rounded-md shadow-sm">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Utilisateur permanent</h3>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">Ne pas supprimer l'utilisateur du site web s'il n'est pas dans
              l'annuaire</span>
            <Switch :modelValue="profileUser.exempt_from_rgpd_delete" @update:modelValue="toggleLdapExempt"
              :class="[profileUser.exempt_from_rgpd_delete ? 'bg-purple-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2']">
              <span class="sr-only">Toggle LDAP exempt</span>
              <span aria-hidden="true"
                :class="[profileUser.exempt_from_rgpd_delete ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
            </Switch>
          </div>
        </div>

        <!-- Add Role -->
        <div class="bg-white p-4 rounded-md shadow-sm">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Ajouter un rôle</h3>
          <div class="space-y-3">
            <select v-model="newRoleForm.organization_id"
              class="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
              <option value="" disabled>Choisir une organisation</option>
              <option v-for="org in allOrganizations" :key="org.id" :value="org.id">{{ org.name }}</option>
            </select>
            <div class="flex space-x-2">
              <select v-model="newRoleForm.role"
                class="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
                <option value="org_member">Membre</option>
                <option value="org_admin">Admin</option>
                <option value="org_viewer">Lecteur</option>
              </select>
              <button @click="addRole" :disabled="!newRoleForm.organization_id || addingRole"
                class="inline-flex justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
                Ajouter
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="mt-6 border-t border-purple-200 pt-6">
        <h3 class="text-sm font-medium text-red-800 mb-4">Zone de danger</h3>
        <div class="flex flex-col sm:flex-row gap-4">
          <button @click="toggleBan"
            class="inline-flex justify-center items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-inset ring-red-300 hover:bg-red-50">
            <NoSymbolIcon class="h-5 w-5 mr-2" />
            {{ profileUser.is_active ? 'Bannir l\'utilisateur' : 'Débannir l\'utilisateur' }}
          </button>
          <button @click="deleteUser"
            class="inline-flex justify-center items-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500">
            <TrashIcon class="h-5 w-5 mr-2" />
            Supprimer l'utilisateur
          </button>
        </div>
      </div>
    </div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">
          {{ isCurrentUser ? 'Mon Profil' : 'Profil utilisateur' }}
        </h1>
        <div class="mt-4 sm:mt-0">
          <button v-if="isCurrentUser && !isEditing" @click="startEditing"
            class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            <PencilIcon class="h-5 w-5 mr-2" />
            Modifier
          </button>
          <div v-if="isEditing" class="flex space-x-3">
            <button @click="cancelEditing"
              class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
              Annuler
            </button>
            <button @click="saveProfile" :disabled="saving"
              class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="space-y-6">
      <!-- User Information Card -->
      <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-6 mb-6">
            <div class="relative">
              <UserAvatar :src="resolveMediaUrl(profileUser.profile_picture_file, 192) ?? profileUser.profile_picture_url ?? undefined"
                :name="profileUser.full_name || profileUser.email" size="2xl" />
              <div v-if="isEditing" class="absolute bottom-0 right-0">
                <label for="avatar-upload"
                  class="cursor-pointer inline-flex items-center rounded-full bg-white p-1.5 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                  <CameraIcon class="h-5 w-5 text-gray-500" />
                  <input id="avatar-upload" type="file" accept="image/*" class="hidden" @change="handleFileUpload" />
                </label>
              </div>
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ profileUser.full_name || 'Jamais connecté' }}</h2>
              <p class="text-sm text-gray-500">{{ profileUser.email }}</p>
            </div>
          </div>

          <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <!-- Read-only View -->
            <template v-if="!isEditing">
              <div v-if="profileUser.phone_number">
                <dt class="text-sm font-medium text-gray-500">Téléphone</dt>
                <dd class="mt-1 text-sm text-gray-900 flex items-center">
                  <PhoneIcon class="h-4 w-4 mr-2 text-gray-400" />
                  {{ profileUser.phone_number }}
                </dd>
              </div>

              <!-- Links (read-only) -->
              <div v-if="profileUser.links && profileUser.links.length > 0" class="sm:col-span-2">
                <dt class="text-sm font-medium text-gray-500 mb-1">Liens</dt>
                <dd class="mt-1 flex flex-wrap gap-3">
                  <a v-for="link in profileUser.links" :key="link.id" :href="link.url" target="_blank"
                    class="flex items-center gap-1.5 text-sm text-indigo-600 hover:text-indigo-800 hover:underline">
                    <img v-if="getSocialIcon(link.url)" :src="getSocialIcon(link.url) ?? undefined"
                      class="h-4 w-4 object-contain flex-shrink-0" />
                    <LinkIcon v-else class="h-4 w-4 flex-shrink-0" />
                    {{ link.name }}
                  </a>
                </dd>
              </div>
            </template>

            <!-- Edit View -->
            <template v-else>
              <div>
                <TextInput v-model="editForm.phone_number" label="Numéro de téléphone" type="tel"
                  placeholder="+33 6 12 34 56 78" />
              </div>

              <!-- Links editor -->
              <div class="sm:col-span-2">
                <dt class="text-sm font-medium text-gray-500 mb-2">Liens</dt>
                <div class="space-y-2">
                  <div v-for="(link, idx) in editLinks" :key="link.id || idx" class="flex items-center gap-2">
                    <input v-model="link.name" type="text" placeholder="Nom (ex: Facebook)"
                      class="block w-1/3 rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm" />
                    <input v-model="link.url" type="url" placeholder="URL (https://...)"
                      class="block flex-1 rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm" />
                    <button type="button" @click="removeEditLink(idx)" class="p-1.5 text-red-500 hover:text-red-700">
                      <XMarkIcon class="h-4 w-4" />
                    </button>
                  </div>
                  <button type="button" @click="addEditLink"
                    class="text-sm text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1">
                    <PlusIcon class="h-4 w-4" /> Ajouter un lien
                  </button>
                </div>
              </div>
            </template>

            <!-- ICS Link (Only for current user) -->
            <div v-if="isCurrentUser && !isEditing" class="sm:col-span-2 border-t border-gray-100 pt-4 mt-2">
              <dt class="text-sm font-medium text-gray-500 mb-1">Calendrier personnel (ICS)</dt>
              <dd class="mt-1">
                <AddToCalendar ref="addToCalendarRef" :url="icsUrl" />
                <p class="mt-1 text-xs text-gray-500">Synchronisez vos événements avec votre application de calendrier
                  préférée.</p>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Roles and Memberships Card -->
      <div v-if="isCurrentUser || isSuperAdmin" class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">{{ isCurrentUser ? 'Mes rôles dans les organisations' :
            'Rôles dans les organisations' }}</h2>

          <div v-if="loadingMemberships" class="text-center py-4">
            <p class="text-sm text-gray-500">Chargement...</p>
          </div>

          <div v-else-if="memberships.length === 0" class="text-center py-8">
            <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">Aucune organisation</h3>
            <p class="mt-1 text-sm text-gray-500">{{ 
            isCurrentUser ? "Vous n'êtes membre d'aucune organisation pour le moment." 
            : "Cet utilisateur n'est membre d'aucune organisation." }}
            </p>
          </div>

            <div v-else class="space-y-4">
              <OrganizationCard v-for="membership in membershipsWithOrganization" :key="membership.id"
              :organization="membership.organization" :show-type="!isCurrentUser">
              <template #side>
                <div class="ml-4 flex-shrink-0">
                  <span :class="getRoleBadgeClass(membership.role)"
                    class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset">
                    {{ getRoleLabel(membership.role) }}
                  </span>
                </div>
              </template>
            </OrganizationCard>
          </div>
        </div>
      </div>

      <!-- Subscriptions Link Card -->
      <div v-if="isCurrentUser" class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center mb-2">
            <BellIcon class="h-6 w-6 text-gray-400 mr-3" />
            <h2 class="text-lg font-medium text-gray-900">Mes Abonnements</h2>
          </div>
          <p class="text-sm text-gray-500 mb-4 max-w-2xl">
            Gérez vos abonnements aux organisations, aux tags et aux groupes. C'est ici que vous décidez quels
            événements
            apparaissent dans votre calendrier.
          </p>
          <router-link to="/subscriptions"
            class="inline-flex items-center text-sm font-semibold text-indigo-600 hover:text-indigo-500">
            Gérer mes abonnements
            <ArrowRightIcon class="ml-1 h-4 w-4" />
          </router-link>
        </div>
      </div>


      <!-- Notifications Card -->
      <div v-if="isCurrentUser" class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center mb-2">
            <BellIcon class="h-6 w-6 text-gray-400 mr-3" />
            <h2 class="text-lg font-medium text-gray-900">Notifications Push</h2>
          </div>
          <p class="text-sm text-gray-500 mb-4 max-w-2xl">
            Activez les notifications push sur cet appareil pour être averti des événements à venir.
          </p>
          <button @click="toggleNotifications" :class="[
            notificationsEnabled
              ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
              : 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500',
            'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-offset-2'
          ]">
            {{ notificationsEnabled ? 'Désactiver les notifications' : 'Activer les notifications' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-12">
    <p class="text-sm text-gray-500">Utilisateur introuvable</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import TextInput from '../components/TextInput.vue'
import UserAvatar from '../components/UserAvatar.vue'
import OrganizationCard from '../components/OrganizationCard.vue'
import AddToCalendar from '../components/AddToCalendar.vue'
import { api } from '@/api'
import type {
  MembershipWithOrganization,
  OrganizationRead,
  Role,
  UserLinkRead,
  UserRead,
  UserUpdate,
} from '@/api/types'
import { getSocialIcon } from '../utils/social'
import { Switch } from '@headlessui/vue'
import { resolveMediaUrl } from '../utils/media.js'
import {
  PencilIcon,
  PhoneIcon,
  CameraIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  BellIcon,
  TrashIcon,
  NoSymbolIcon,
  LinkIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const { user: currentUser, isSuperAdmin } = useAuth()
const profileUser = ref<UserRead | null>(null)
const memberships = ref<MembershipWithOrganization[]>([])
const loading = ref(true)
const loadingMemberships = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const allOrganizations = ref<OrganizationRead[]>([])
const addingRole = ref(false)
const securekey = ref('')

type EditableLink = {
  id: string | null
  name: string
  url: string
  order: number
}

const newRoleForm = ref<{ organization_id: string; role: Role }>({
  organization_id: '',
  role: 'org_member' as Role
})

const editForm = ref<UserUpdate>({
  profile_picture_file_id: undefined,
  phone_number: '',
  notification_delay: 15
})

const editLinks = ref<EditableLink[]>([])

const syncEditFormFromProfile = (user: UserRead) => {
  editForm.value = {
    profile_picture_file_id: user.profile_picture_file?.id || undefined,
    phone_number: user.phone_number || '',
    notification_delay: user.notification_delay || 15,
  }
}

const isCurrentUser = computed(() => {
  if (!currentUser.value || !profileUser.value) return false
  return currentUser.value.id === profileUser.value.id
})

const membershipsWithOrganization = computed(() => {
  return memberships.value.filter(
    (m): m is MembershipWithOrganization & { organization: OrganizationRead } => m.organization !== null,
  )
})

const icsUrl = computed(() => {
  return currentUser.value && securekey.value ? `${window.location.origin}/api/calendar/${securekey.value}/${currentUser.value.id}.ics` : ''
})

const loadUser = async () => {
  loading.value = true
  const routeUserId = route.params.id
  const userId = Array.isArray(routeUserId) ? routeUserId[0] : routeUserId

  try {
    profileUser.value = !userId || userId === 'me'
      ? await api.users.get_me()
      : await api.users.get_user_profile(userId)

    // Initialize edit form
    if (isCurrentUser.value && profileUser.value) {
      syncEditFormFromProfile(profileUser.value)
      // Load links
      const links = await api.users.list_my_links()
      editLinks.value = links.map(l => ({ ...l }))
    }
  } catch (error) {
    console.error('Failed to load user:', error)
  } finally {
    loading.value = false
  }
}

const loadMemberships = async () => {
  if (!isCurrentUser.value && !isSuperAdmin.value) return
  if (!profileUser.value) return

  loadingMemberships.value = true
  try {
    const userId = profileUser.value.id
    memberships.value = isCurrentUser.value
      ? await api.users.get_user_memberships()
      : await api.users.get_other_user_memberships(userId)
  } catch (error) {
    console.error('Failed to load memberships:', error)
  } finally {
    loadingMemberships.value = false
  }
}

const loadAllOrganizations = async () => {
  if (!isSuperAdmin.value) return
  try {
    allOrganizations.value = await api.organizations.list_organizations()
  } catch (error) {
    console.error('Failed to load organizations:', error)
  }
}

const toggleSuperadmin = async (newValue: boolean) => {
  if (!profileUser.value) return
  // Optimistic update
  profileUser.value.is_superadmin = newValue

  try {
    await api.users.toggle_superadmin(profileUser.value.id, newValue)
  } catch (error) {
    console.error('Failed to toggle superadmin:', error)
    // Revert on error
    profileUser.value.is_superadmin = !newValue
  }
}

const toggleLdapExempt = async (newValue: boolean) => {
  if (!profileUser.value) return
  // Optimistic update
  profileUser.value.exempt_from_rgpd_delete = newValue

  try {
    await api.users.toggle_exempt_from_rgpd_delete(profileUser.value.id, newValue)
  } catch (error) {
    console.error('Failed to toggle LDAP exempt:', error)
    // Revert on error
    profileUser.value.exempt_from_rgpd_delete = !newValue
  }
}

const addRole = async () => {
  if (!newRoleForm.value.organization_id || !profileUser.value) return

  addingRole.value = true
  try {
    await api.organizations.add_organization_member(
      newRoleForm.value.organization_id,
      profileUser.value.email,
      newRoleForm.value.role
    )
    // Refresh memberships
    await loadMemberships()
    newRoleForm.value.organization_id = ''
  } catch (error) {
    console.error('Failed to add role:', error)
    alert('Erreur lors de l\'ajout du rôle. Vérifiez que l\'utilisateur n\'est pas déjà membre.')
  } finally {
    addingRole.value = false
  }
}

const startEditing = () => {
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  // Reset form
  if (profileUser.value) {
    syncEditFormFromProfile(profileUser.value)
    editLinks.value = (profileUser.value.links || []).map((l) => ({ ...l }))
  }
}

const loadSecurekey = async () => {
  if (!isCurrentUser.value) return
  try {
    securekey.value = await api.calendar.get_securekey()
  } catch (error) {
    console.error('Failed to load securekey:', error)
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement | null
  const file = target?.files?.[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.upload.upload_image(formData)
    editForm.value.profile_picture_file_id = response.stored_file_id
  } catch (error) {
    console.error('Failed to upload image:', error)
    alert('Failed to upload image')
  }
}

const saveProfile = async () => {
  if (!profileUser.value) return
  saving.value = true
  try {
    const originalLinks = [...(profileUser.value.links || [])]
    const originalIds = new Set(originalLinks.map((l) => l.id))

    profileUser.value = await api.users.update_user_profile(editForm.value)

    // Sync links: delete removed, update existing, create new
    const currentIds = new Set(
      editLinks.value
        .map((l) => l.id)
        .filter((id): id is string => Boolean(id)),
    )

    // Delete removed
    for (const id of originalIds) {
      if (!currentIds.has(id)) {
        await api.users.delete_my_link(id)
      }
    }
    // Create or update
    for (const [idx, link] of editLinks.value.entries()) {
      if (link.id && originalIds.has(link.id)) {
        await api.users.update_my_link(link.id, { name: link.name, url: link.url, order: idx })
      } else {
        await api.users.create_my_link({ name: link.name, url: link.url, order: idx })
      }
    }

    // Reload user to get fresh links
    profileUser.value = await api.users.get_me()
    isEditing.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    saving.value = false
  }
}

const addEditLink = () => {
  editLinks.value.push({ id: null, name: '', url: '', order: editLinks.value.length })
}

const removeEditLink = (idx: number) => {
  editLinks.value.splice(idx, 1)
}



const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    'superadmin': 'Superadmin',
    'org_admin': 'Administrateur',
    'org_member': 'Éditeur',
    'org_viewer': 'Lecteur',
  }
  return labels[role] || role
}

const getRoleBadgeClass = (role: string) => {
  const classes: Record<string, string> = {
    'superadmin': 'bg-purple-50 text-purple-700 ring-purple-700/10',
    'org_admin': 'bg-blue-50 text-blue-700 ring-blue-700/10',
    'org_member': 'bg-green-50 text-green-700 ring-green-600/20',
    'org_viewer': 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  }
  return classes[role] || 'bg-gray-50 text-gray-700 ring-gray-600/20'
}

const toggleBan = async () => {
  if (!profileUser.value) return
  const action = profileUser.value.is_active ? 'bannir' : 'débannir'
  if (!confirm(`Êtes-vous sûr de vouloir ${action} cet utilisateur ?`)) return

  try {
    profileUser.value = await api.users.toggle_active(profileUser.value.id, !profileUser.value.is_active)
  } catch (error) {
    console.error('Failed to toggle ban:', error)
    alert('Une erreur est survenue.')
  }
}

const deleteUser = async () => {
  if (!profileUser.value) return
  if (!confirm('Êtes-vous sûr de vouloir supprimer définitivement cet utilisateur ? Cette action est irréversible.')) return

  try {
    await api.users.delete_user(profileUser.value.id)
    router.push('/')
  } catch (error) {
    console.error('Failed to delete user:', error)
    alert('Une erreur est survenue lors de la suppression.')
  }
}

watch(() => route.params.id, () => {
  loadUser().then(() => loadMemberships()).then(() => loadSecurekey())
})

import { askPermissionAndSubscribe, unsubscribeUserFromPush } from '../utils/push'

const notificationsEnabled = ref(false)

const checkNotificationStatus = async () => {
  if ('serviceWorker' in navigator && 'PushManager' in window) {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()
    notificationsEnabled.value = !!subscription
  }
}

const toggleNotifications = async () => {
  if (notificationsEnabled.value) {
    if (confirm("Voulez-vous vraiment désactiver les notifications push ?")) {
      const success = await unsubscribeUserFromPush()
      if (success) {
        notificationsEnabled.value = false
        alert("Notifications désactivées.")
      } else {
        alert("Erreur lors de la désactivation.")
      }
    }
  } else {
    const success = await askPermissionAndSubscribe()
    if (success) {
      notificationsEnabled.value = true
      alert("Notifications activées avec succès !")
    } else {
      alert("Impossible d'activer les notifications.")
    }
  }
}

const addToCalendarRef = ref<{ open: () => void } | null>(null)

const triggerAddCalendar = () => {
  if (route.path === '/profile/add_calendar' && addToCalendarRef.value) {
    addToCalendarRef.value.open()
  }
}

// Watch for loading completion to trigger the popup
watch(loading, (newVal) => {
  if (!newVal) {
    // Wait for next tick to ensure v-if rendering
    setTimeout(() => {
      triggerAddCalendar()
    }, 100)
  }
})

// Also watch securekey because that's what makes the component appear in some cases (icsUrl dependency)
watch(securekey, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      triggerAddCalendar()
    }, 100)
  }
})

onMounted(() => {
  loadUser().then(() => {
    loadMemberships()
    loadSecurekey()
    checkNotificationStatus()
    if (isSuperAdmin.value) {
      loadAllOrganizations()
    }
  })
})
</script>
