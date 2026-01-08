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
            <Switch
              :modelValue="profileUser.is_superadmin"
              @update:modelValue="toggleSuperadmin"
              :class="[profileUser.is_superadmin ? 'bg-purple-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2']"
            >
              <span class="sr-only">Toggle superadmin</span>
              <span aria-hidden="true" :class="[profileUser.is_superadmin ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
            </Switch>
          </div>
        </div>

        <!-- Add Role -->
        <div class="bg-white p-4 rounded-md shadow-sm">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Ajouter un rôle</h3>
          <div class="space-y-3">
            <select v-model="newRoleForm.organization_id" class="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
              <option value="" disabled>Choisir une organisation</option>
              <option v-for="org in allOrganizations" :key="org.id" :value="org.id">{{ org.name }}</option>
            </select>
            <div class="flex space-x-2">
              <select v-model="newRoleForm.role" class="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6">
                <option value="org_member">Membre</option>
                <option value="org_admin">Admin</option>
                <option value="org_viewer">Lecteur</option>
              </select>
              <button @click="addRole" :disabled="!newRoleForm.organization_id || addingRole" class="inline-flex justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
                Ajouter
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">
          {{ isCurrentUser ? 'Mon Profil' : 'Profil utilisateur' }}
        </h1>
        <button 
          v-if="isCurrentUser && !isEditing"
          @click="startEditing"
          class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
        >
          <PencilIcon class="h-5 w-5 mr-2" />
          Modifier
        </button>
        <div v-if="isEditing" class="flex space-x-3">
          <button 
            @click="cancelEditing"
            class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Annuler
          </button>
          <button 
            @click="saveProfile"
            :disabled="saving"
            class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
          >
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </div>
    </header>

    <div class="space-y-6">
      <!-- User Information Card -->
      <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-6 mb-6">
            <div class="relative">
              <UserAvatar 
                :src="editForm.profile_picture_url || profileUser.profile_picture_url" 
                :name="profileUser.full_name || profileUser.email" 
                size="2xl" 
              />
              <div v-if="isEditing" class="absolute bottom-0 right-0">
                <label for="avatar-upload" class="cursor-pointer inline-flex items-center rounded-full bg-white p-1.5 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                  <CameraIcon class="h-5 w-5 text-gray-500" />
                  <input 
                    id="avatar-upload" 
                    type="file" 
                    accept="image/*" 
                    class="hidden" 
                    @change="handleFileUpload"
                  />
                </label>
              </div>
            </div>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ profileUser.full_name || 'Sans nom' }}</h2>
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

              <div v-if="profileUser.facebook_link">
                <dt class="text-sm font-medium text-gray-500">Facebook</dt>
                <dd class="mt-1 text-sm text-gray-900 flex items-center">
                  <svg class="h-4 w-4 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.791-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                  <a :href="profileUser.facebook_link" target="_blank" class="text-indigo-600 hover:underline">Voir le profil</a>
                </dd>
              </div>
            </template>

            <!-- Edit View -->
            <template v-else>
              <div>
                <TextInput
                  v-model="editForm.phone_number"
                  label="Numéro de téléphone"
                  type="tel"
                  placeholder="+33 6 12 34 56 78"
                />
              </div>

              <div>
                <TextInput
                  v-model="editForm.facebook_link"
                  label="Lien Facebook"
                  type="url"
                  placeholder="https://facebook.com/..."
                />
              </div>
            </template>

            <!-- ICS Link (Only for current user) -->
            <div v-if="isCurrentUser && !isEditing" class="sm:col-span-2 border-t border-gray-100 pt-4 mt-2">
              <dt class="text-sm font-medium text-gray-500 mb-1">Calendrier personnel (ICS)</dt>
              <dd class="mt-1">
                <div class="flex items-center space-x-2">
                  <input 
                    :value="icsUrl"
                    readonly
                    class="block flex-1 rounded-md border-0 py-1.5 pl-3 text-gray-900 bg-gray-50 shadow-sm ring-1 ring-inset ring-gray-300 sm:text-sm sm:leading-6"
                  />
                  <button 
                    @click="copyIcsUrl"
                    class="px-3 py-2 text-sm font-semibold text-indigo-600 hover:text-indigo-700"
                  >
                    {{ copyText }}
                  </button>
                </div>
                <p class="mt-1 text-xs text-gray-500">Utilisez ce lien pour synchroniser vos événements avec votre application de calendrier</p>
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Roles and Memberships Card -->
      <div v-if="isCurrentUser || isSuperAdmin" class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-4 py-5 sm:p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">{{ isCurrentUser ? 'Mes rôles dans les organisations' : 'Rôles dans les organisations' }}</h2>
          
          <div v-if="loadingMemberships" class="text-center py-4">
            <p class="text-sm text-gray-500">Chargement...</p>
          </div>
          
          <div v-else-if="memberships.length === 0" class="text-center py-8">
            <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">Aucune organisation</h3>
            <p class="mt-1 text-sm text-gray-500">{{ isCurrentUser ? "Vous n'êtes membre d'aucune organisation pour le moment." : "Cet utilisateur n'est membre d'aucune organisation." }}</p>
          </div>
          
          <div v-else class="space-y-4">
            <OrganizationCard
              v-for="membership in memberships"
              :key="membership.id"
              :organization="membership.organization"
              :show-type="true"
            >
              <template #side>
                <div class="ml-4 flex-shrink-0">
                  <span :class="getRoleBadgeClass(membership.role)" class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset">
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
            Gérez vos abonnements aux organisations, aux tags et aux groupes. C'est ici que vous décidez quels événements apparaissent dans votre calendrier.
          </p>
          <router-link 
            to="/subscriptions"
            class="inline-flex items-center text-sm font-semibold text-indigo-600 hover:text-indigo-500"
          >
            Gérer mes abonnements
            <ArrowRightIcon class="ml-1 h-4 w-4" />
          </router-link>
        </div>
      </div>
    </div>
  </div>
  
  <div v-else class="text-center py-12">
    <p class="text-sm text-gray-500">Utilisateur introuvable</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import TextInput from '../components/TextInput.vue'
import UserAvatar from '../components/UserAvatar.vue'
import OrganizationCard from '../components/OrganizationCard.vue'
import api from '../utils/api'
import { Switch } from '@headlessui/vue'
import { 
  PencilIcon, 
  PhoneIcon, 
  CameraIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  BellIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const { user: currentUser, isSuperAdmin } = useAuth()
const profileUser = ref(null)
const memberships = ref([])
const loading = ref(true)
const loadingMemberships = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const copyText = ref('Copier')
const allOrganizations = ref([])
const addingRole = ref(false)
const securekey = ref('')
const newRoleForm = ref({
  organization_id: '',
  role: 'org_member'
})

const editForm = ref({
  profile_picture_url: '',
  facebook_link: '',
  phone_number: '',
})

const isCurrentUser = computed(() => {
  if (!currentUser.value || !profileUser.value) return false
  return currentUser.value.id === profileUser.value.id
})

const icsUrl = computed(() => {
  return currentUser.value && securekey.value ? `${window.location.origin}/api/calendar/${securekey.value}/${currentUser.value.id}.ics` : ''
})

const loadUser = async () => {
  loading.value = true
  const userId = route.params.id || 'me'
  
  try {
    const response = await api.get(`/users/${userId}`)
    profileUser.value = response.data
    
    // Initialize edit form
    if (isCurrentUser.value) {
      editForm.value = {
        profile_picture_url: profileUser.value.profile_picture_url || '',
        facebook_link: profileUser.value.facebook_link || '',
        phone_number: profileUser.value.phone_number || '',
      }
    }
  } catch (error) {
    console.error('Failed to load user:', error)
  } finally {
    loading.value = false
  }
}

const loadMemberships = async () => {
  if (!isCurrentUser.value && !isSuperAdmin.value) return
  
  loadingMemberships.value = true
  try {
    const userId = profileUser.value.id
    const endpoint = isCurrentUser.value ? '/users/me/memberships' : `/users/${userId}/memberships`
    const response = await api.get(endpoint)
    memberships.value = response.data
  } catch (error) {
    console.error('Failed to load memberships:', error)
  } finally {
    loadingMemberships.value = false
  }
}

const loadAllOrganizations = async () => {
  if (!isSuperAdmin.value) return
  try {
    const response = await api.get('/organizations/')
    allOrganizations.value = response.data
  } catch (error) {
    console.error('Failed to load organizations:', error)
  }
}

const toggleSuperadmin = async (newValue) => {
  // Optimistic update
  profileUser.value.is_superadmin = newValue
  
  try {
    await api.put(`/users/${profileUser.value.id}/superadmin?is_superadmin=${newValue}`)
  } catch (error) {
    console.error('Failed to toggle superadmin:', error)
    // Revert on error
    profileUser.value.is_superadmin = !newValue
  }
}

const addRole = async () => {
  if (!newRoleForm.value.organization_id) return
  
  addingRole.value = true
  try {
    await api.post(`/organizations/${newRoleForm.value.organization_id}/members`, {
      email: profileUser.value.email,
      role: newRoleForm.value.role
    })
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
    editForm.value = {
      profile_picture_url: profileUser.value.profile_picture_url || '',
      facebook_link: profileUser.value.facebook_link || '',
      phone_number: profileUser.value.phone_number || '',
    }
  }
}

const loadSecurekey = async () => {
  if (!isCurrentUser.value) return
  try {
    const response = await api.get('/calendar/securekey')
    securekey.value = response.data
  } catch (error) {
    console.error('Failed to load securekey:', error)
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    editForm.value.profile_picture_url = response.data.url
  } catch (error) {
    console.error('Failed to upload image:', error)
    alert('Failed to upload image')
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    const response = await api.put('/users/me', editForm.value)
    profileUser.value = response.data
    isEditing.value = false
  } catch (error) {
    console.error('Failed to update profile:', error)
  } finally {
    saving.value = false
  }
}

const copyIcsUrl = () => {
  navigator.clipboard.writeText(icsUrl.value)
  copyText.value = 'Copié!'
  setTimeout(() => {
    copyText.value = 'Copier'
  }, 2000)
}

const getRoleLabel = (role) => {
  const labels = {
    'superadmin': 'Superadmin',
    'org_admin': 'Administrateur',
    'org_member': 'Membre',
    'org_viewer': 'Lecteur',
  }
  return labels[role] || role
}

const getRoleBadgeClass = (role) => {
  const classes = {
    'superadmin': 'bg-purple-50 text-purple-700 ring-purple-700/10',
    'org_admin': 'bg-blue-50 text-blue-700 ring-blue-700/10',
    'org_member': 'bg-green-50 text-green-700 ring-green-600/20',
    'org_viewer': 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  }
  return classes[role] || 'bg-gray-50 text-gray-700 ring-gray-600/20'
}

watch(() => route.params.id, () => {
  loadUser().then(() => loadMemberships()).then(() => loadSecurekey())
})

onMounted(() => {
  loadUser().then(() => {
    loadMemberships()
    loadSecurekey()
    if (isSuperAdmin.value) {
      loadAllOrganizations()
    }
  })
})
</script>
