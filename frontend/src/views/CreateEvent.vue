<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Créer un événement</h1>
      </div>
    </header>

    <div class="bg-white shadow-sm rounded-lg p-6">
      <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>
      
      <form @submit.prevent="createEvent">
        <div class="space-y-12">
          <div class="border-b border-gray-900/10 pb-12">
            <!-- Organization Selector -->
            <div class="mb-8">
              <div v-if="isSuperAdmin" class="flex flex-col mb-4 bg-indigo-50/50 p-3 rounded-lg border border-indigo-100">
                 <div class="flex items-center justify-between">
                    <span class="text-xs font-medium text-indigo-900">Mode SuperAdmin</span>
                    <button 
                        @click="toggleSuperAdminMode"
                        type="button"
                        class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2"
                        :class="[showAllForSuperAdmin ? 'bg-indigo-600' : 'bg-gray-200']"
                    >
                        <span 
                            class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                            :class="[showAllForSuperAdmin ? 'translate-x-4' : 'translate-x-0']"
                        />
                    </button>
                 </div>
                 
                 <div v-if="showAllForSuperAdmin" class="mt-3">
                    <input
                        ref="superAdminSearchInput"
                        v-model="superAdminSearchQuery"
                        type="text"
                        placeholder="Rechercher une organisation..."
                        class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-xs sm:leading-6"
                    />
                 </div>
              </div>
              <OrganizationSelector
                v-model="form.organization_id"
                :organizations="displayedOrganizations"
                label="Choisir l'organisation"
                emptyMessage="Vous devez être membre d'au moins une organisation pour créer un événement"
              />
            </div>

            <!-- Collapsible Guest Organizations Section -->
            <div class="col-span-full mb-8">
                <CollapsibleCard 
                    title="Organisations invitées (optionnel)"
                    v-model="isGuestOrgsOpen"
                >
                    <template #summary>
                        <span v-if="form.guest_organization_ids.length > 0" class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
                            {{ form.guest_organization_ids.length }} sélectionnée(s)
                        </span>
                    </template>
                    
                    <div class="mb-3">
                         <input
                            ref="guestOrgSearchInput"
                            v-model="guestOrgSearchQuery"
                            type="text"
                            placeholder="Rechercher une organisation invitée..."
                            class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-xs sm:leading-6"
                        />
                    </div>

                    <OrganizationSelector
                        v-model="form.guest_organization_ids"
                        :organizations="displayedGuestOrganizations"
                        :multiple="true"
                        label=""
                        emptyMessage="Aucune organisation trouvée"
                    />
                </CollapsibleCard>
            </div>

            <div class="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div class="sm:col-span-4">
                <label for="title" class="block text-sm font-medium leading-6 text-gray-900">Titre de l'événement</label>
                <div class="mt-2">
                  <input 
                    type="text" 
                    name="title" 
                    id="title" 
                    required
                    v-model="form.title" 
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                    placeholder="Soirée de rentrée..." 
                  />
                </div>
              </div>

              <div class="col-span-full">
                <label for="description" class="block text-sm font-medium leading-6 text-gray-900">Description</label>
                <div class="mt-2">
                  <textarea 
                    id="description" 
                    name="description" 
                    rows="3" 
                    v-model="form.description" 
                    class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  ></textarea>
                </div>
              </div>

              <!-- Date, Time, Duration -->
              <div class="col-span-full">
                <DateTimeDurationPicker
                  v-model:start-time="form.start_time"
                  v-model:end-time="form.end_time"
                />
              </div>

              <!-- Overlapping events warning -->
              <div v-if="overlappingEvents.length > 0" class="col-span-full">
                <div class="rounded-lg bg-orange-50 border border-orange-200 p-3">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2 text-orange-700">
                      <ExclamationTriangleIcon class="h-5 w-5 shrink-0" />
                      <span class="text-sm font-medium">
                        {{ overlappingEvents.length }} événement{{ overlappingEvents.length > 1 ? 's' : '' }} simultané{{ overlappingEvents.length > 1 ? 's' : '' }}
                      </span>
                    </div>
                    <button
                      type="button"
                      @click="showOverlapModal = true"
                      class="text-xs text-orange-600 hover:text-orange-800 underline"
                    >
                      Voir
                    </button>
                  </div>
                </div>
              </div>

              <div class="sm:col-span-3">
                <label for="location" class="block text-sm font-medium leading-6 text-gray-900">Lieu (optionnel)</label>
                <div class="mt-2">
                  <input 
                    type="text" 
                    name="location" 
                    id="location" 
                    v-model="form.location" 
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                    placeholder="Foyer, Amphithéâtre..." 
                  />
                </div>
              </div>

              <div class="sm:col-span-3">
                <label for="location_url" class="block text-sm font-medium leading-6 text-gray-900">Lien du lieu (optionnel)</label>
                <div class="mt-2">
                  <input 
                    type="url" 
                    name="location_url" 
                    id="location_url" 
                    v-model="form.location_url" 
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                    placeholder="https://maps.google.com/..." 
                  />
                </div>
              </div>

              <div class="col-span-full">
                <ImageUpload v-model="form.poster_url" label="Affiche de l'événement (optionnel)" />
              </div>

              <div class="col-span-full">
                <VideoUpload v-model="form.video_url" label="Vidéo d'affiche (optionnel — affiché en autoplay dans le feed)" />
              </div>

              <!-- Visibility Selector -->
              <div class="col-span-full">
                <VisibilitySelector
                  v-model:visibility="form.visibility"
                  v-model:group-id="form.group_id"

                  v-model:hide-details="form.hide_details"
                  :organization-id="form.organization_id"
                />
              </div>

              <!-- Tags Selector -->
              <div class="col-span-full">
                <TagSelector
                  v-model="form.tag_ids"
                  :organization-id="form.organization_id"
                />
              </div>
            </div>
          </div>

          <div class="border-b border-gray-900/10 pb-12">
            <h2 class="text-base font-semibold leading-7 text-gray-900">Liens</h2>

            <div class="mt-6 space-y-4">
              <div v-for="(link, index) in form.links" :key="index" class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-12">
                <div class="sm:col-span-5">
                  <input 
                    type="text" 
                    v-model="link.name" 
                    placeholder="Nom du lien" 
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                  />
                </div>
                <div class="sm:col-span-6">
                  <input 
                    v-model="link.url"
                    type="url"
                    placeholder="https://..."
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
                <div class="sm:col-span-1 flex items-center">
                  <button 
                    @click="removeLink(index)"
                    type="button"
                    class="px-3 py-2 text-sm text-red-600 hover:text-red-700"
                  >
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>
              <button 
                @click="addLink"
                type="button"
                class="mt-2 flex items-center text-sm text-indigo-600 hover:text-indigo-700"
              >
                <PlusIcon class="h-4 w-4 mr-1" />
                Ajouter un lien
              </button>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-col-reverse sm:flex-row items-center justify-end gap-x-6 gap-y-3 sm:gap-y-0">
          <router-link to="/" class="w-full text-center sm:w-auto text-sm font-semibold leading-6 text-gray-900">Annuler</router-link>
          <button 
            type="submit" 
            :disabled="loading || !form.organization_id"
            class="w-full sm:w-auto rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
          >
            {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Overlap Modal -->
  <div v-if="showOverlapModal" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex min-h-screen items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/50" @click="showOverlapModal = false"></div>
      <div class="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Événements simultanés</h3>
          <button @click="showOverlapModal = false" class="text-gray-400 hover:text-gray-500">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        <div class="space-y-3 max-h-[60vh] overflow-y-auto">
          <div
            v-for="evt in overlappingEvents"
            :key="evt.id"
            class="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-100"
            @click="$router.push(`/events/${evt.id}`)"
          >
            <div
              class="h-10 w-10 shrink-0 rounded-full flex items-center justify-center text-white font-bold text-xs"
              :style="{ backgroundColor: evt.organization?.color_secondary || '#f3f4f6' }"
            >
              <img v-if="evt.organization?.logo_url" :src="evt.organization.logo_url" class="h-full w-full object-cover rounded-full" />
              <span v-else :style="{ color: evt.organization?.color_primary || '#4f46e5' }">{{ evt.organization?.name?.charAt(0) }}</span>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-900">{{ evt.title }}</h4>
              <p class="text-xs text-gray-500">{{ formatOverlapDate(evt.start_time) }} – {{ formatOverlapDate(evt.end_time) }}</p>
              <p class="text-xs text-orange-600 mt-0.5" v-if="evt.visibility === 'public_pending'">En attente de validation</p>
            </div>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="showOverlapModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'

import api from '../utils/api'
import { useAuth } from '../composables/useAuth'
import { localToUtc } from '../utils/dateUtils'
import OrganizationSelector from '../components/OrganizationSelector.vue'
import ImageUpload from '../components/ImageUpload.vue'
import VideoUpload from '../components/VideoUpload.vue'
import CollapsibleCard from '../components/CollapsibleCard.vue'
import VisibilitySelector from '../components/VisibilitySelector.vue'
import TagSelector from '../components/TagSelector.vue'
import { PlusIcon, XMarkIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import DateTimeDurationPicker from '../components/DateTimeDurationPicker.vue'

const router = useRouter()

const form = ref({
  organization_id: '',
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  location: '',
  location_url: '',
  poster_url: '',
  video_url: '',
  visibility: 'public_pending',

  hide_details: false,
  group_id: null,
  tag_ids: [],
  links: [],
  guest_organization_ids: []
})

const userOrganizations = ref([])
const error = ref('')
const loading = ref(false)
const allOrganizations = ref([])
const isGuestOrgsOpen = ref(false)
const { user, isSuperAdmin } = useAuth()

const overlappingEvents = ref([])
const showOverlapModal = ref(false)
let overlapCheckTimeout = null

const formatOverlapDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const checkOverlaps = async () => {
  if (!form.value.start_time || !form.value.end_time) {
    overlappingEvents.value = []
    return
  }
  try {
    const startUtc = localToUtc(form.value.start_time)
    const endUtc = localToUtc(form.value.end_time)
    const res = await api.get('/events/overlapping-check', { params: { start_time: startUtc, end_time: endUtc } })
    overlappingEvents.value = res.data
  } catch (e) {
    overlappingEvents.value = []
  }
}

const showAllForSuperAdmin = ref(false)
const superAdminSearchQuery = ref('')
const superAdminSearchInput = ref(null)

const displayedOrganizations = computed(() => {
    if (showAllForSuperAdmin.value) {
        if (!superAdminSearchQuery.value) return allOrganizations.value
        const query = superAdminSearchQuery.value.toLowerCase()
        return allOrganizations.value.filter(org => org.name.toLowerCase().includes(query))
    }
    return userOrganizations.value
})

const toggleSuperAdminMode = async () => {
    showAllForSuperAdmin.value = !showAllForSuperAdmin.value
    form.value.organization_id = ''
    
    if (showAllForSuperAdmin.value) {
        // Auto focus
        setTimeout(() => {
             superAdminSearchInput.value?.focus()
        }, 100)
    } else {
        superAdminSearchQuery.value = ''
    }
}

// Guest Orgs Search
const guestOrgSearchQuery = ref('')
const guestOrgSearchInput = ref(null)

const displayedGuestOrganizations = computed(() => {
    if (!guestOrgSearchQuery.value) return allOrganizations.value
    const query = guestOrgSearchQuery.value.toLowerCase()
    return allOrganizations.value.filter(org => org.name.toLowerCase().includes(query))
})

// Watch collapsible open to focus search
watch(isGuestOrgsOpen, (isOpen) => {
    if (isOpen) {
        setTimeout(() => {
            guestOrgSearchInput.value?.focus()
        }, 100)
    }
})

// timeForm removed as it is handled in component

// Helper to format date for datetime-local input
const formatDateTimeLocal = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// updateTimeFromComponents removed

// Watch dates to check overlapping events (debounced)
watch([() => form.value.start_time, () => form.value.end_time], () => {
  clearTimeout(overlapCheckTimeout)
  overlapCheckTimeout = setTimeout(checkOverlaps, 600)
})

// Watch for changes in organization_id to reset group_id and tag_ids
watch(() => form.value.organization_id, (newOrgId) => {
  if (!newOrgId) {
    form.value.group_id = null
    form.value.tag_ids = []
  }
})

const loadUserOrganizations = async () => {
  try {
    const response = await api.get('/users/me/memberships')
    // Filter to only show organizations where user can create events (admin or member)
    userOrganizations.value = response.data
      .filter(m => m.role === 'org_admin' || m.role === 'org_member')
      .map(m => m.organization)
      .filter(org => org !== null)

    // If user is member of only one organization, pre-select it
    if (userOrganizations.value.length === 1) {
      form.value.organization_id = userOrganizations.value[0].id
    }
  } catch (err) {
    console.error('Failed to load organizations:', err)
  }
}

const loadAllOrganizations = async () => {
    try {
        const response = await api.get('/organizations/')
        allOrganizations.value = response.data
    } catch (err) {
         console.error('Failed to load all organizations:', err)
    }
}

const addLink = () => {
  form.value.links.push({ name: '', url: '', order: form.value.links.length + 1 })
}

const removeLink = (index) => {
  form.value.links.splice(index, 1)
  // Update order for remaining links
  form.value.links.forEach((link, idx) => {
    link.order = idx + 1
  })
}

const createEvent = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const eventData = {
      title: form.value.title,
      description: form.value.description,
      start_time: localToUtc(form.value.start_time),
      end_time: localToUtc(form.value.end_time),
      location: form.value.location,
      location_url: form.value.location_url,
      poster_url: form.value.poster_url,
      video_url: form.value.video_url,
      organization_id: form.value.organization_id,
      visibility: form.value.visibility,
      group_id: form.value.group_id,
      tag_ids: form.value.tag_ids,
      hide_details: form.value.hide_details,
      links: form.value.links.filter(link => link.name && link.url),
      guest_organization_ids: form.value.guest_organization_ids
    }

    const response = await api.post('/events/', eventData)
    router.push(`/events/${response.data.id}`)
  } catch (err) {
    console.error('Failed to create event:', err)
    error.value = err.response?.data?.detail || 'Échec de la création de l\'événement'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUserOrganizations()
  loadAllOrganizations()
  
  // Check for duplicate data
  const duplicateData = history.state.duplicateEvent
  if (duplicateData) {
      // Use logic similar to EventEdit loading
      // Populate form
      form.value = {
          title: duplicateData.title,
          description: duplicateData.description,
          start_time: duplicateData.start_time,
          end_time: duplicateData.end_time,
          location: duplicateData.location,
          location_url: duplicateData.location_url,
          organization_id: duplicateData.organization_id,
          group_id: duplicateData.group_id ? duplicateData.group_id : '', // Ensure empty string if null
          visibility: 'draft', // Reset to draft
          poster_url: duplicateData.poster_url,
          video_url: duplicateData.video_url,
          tag_ids: duplicateData.tags?.map(t => t.id) || [],
          guest_organization_ids: duplicateData.guest_organizations?.map(g => g.id) || [],
          hide_details: duplicateData.hide_details,
          links: duplicateData.links && duplicateData.links.length > 0 ? duplicateData.links.map(l => ({
              url: l.url,
              label: l.label,
              type: l.type
          })) : [{ url: '', label: '', type: 'website' }]
      }
      
      if (form.value.guest_organization_ids.length > 0) {
          isGuestOrgsOpen.value = true
      }
      return
  }
  
  // Initialize time with defaults (next hour, duration 1h)
  const now = new Date()
  now.setMinutes(0)
  now.setSeconds(0)
  now.setMilliseconds(0)
  now.setHours(now.getHours() + 1)
  
  /*
  timeForm.value.date = formatDateTimeLocal(now).split('T')[0]
  timeForm.value.time = formatDateTimeLocal(now).split('T')[1]
  timeForm.value.durationHours = 1
  timeForm.value.durationMinutes = 0
  
  updateTimeFromComponents()
  */
})
</script>
