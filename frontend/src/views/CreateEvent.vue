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
              <OrganizationSelector
                v-model="form.organization_id"
                :organizations="userOrganizations"
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
                    
                    <OrganizationSelector
                        v-model="form.guest_organization_ids"
                        :organizations="allOrganizations"
                        :multiple="true"
                        label=""
                        emptyMessage="Aucune organisation disponible"
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
              <div class="col-span-full bg-gray-50 p-4 rounded-lg">
                <h3 class="text-sm font-medium text-gray-900 mb-4">Date et Heure</h3>

                <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-3 items-end">
                  <!-- Date -->
                  <div>
                    <label for="date" class="block text-sm font-medium leading-6 text-gray-900">Date</label>
                    <div class="mt-2">
                      <input 
                        type="date" 
                        id="date" 
                        required
                        v-model="timeForm.date"
                        @change="updateTimeFromComponents"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                      />
                    </div>
                  </div>

                  <!-- Time -->
                  <div>
                    <label for="time" class="block text-sm font-medium leading-6 text-gray-900">Heure de début</label>
                    <div class="mt-2">
                      <input 
                        type="time" 
                        id="time" 
                        required
                        v-model="timeForm.time"
                        @change="updateTimeFromComponents"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                      />
                    </div>
                  </div>

                  <!-- Duration -->
                  <div>
                    <label class="block text-sm font-medium leading-6 text-gray-900">Durée</label>
                    <div class="mt-2 flex space-x-2">
                      <div class="relative rounded-md shadow-sm">
                        <input 
                          type="number" 
                          v-model.number="timeForm.durationHours"
                          @change="updateTimeFromComponents"
                          min="0"
                          class="block w-full rounded-md border-0 py-1.5 pr-8 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                          placeholder="0" 
                        />
                        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                          <span class="text-gray-500 sm:text-sm">h</span>
                        </div>
                      </div>
                      <div class="relative rounded-md shadow-sm">
                        <input 
                          type="number" 
                          v-model.number="timeForm.durationMinutes"
                          @change="updateTimeFromComponents"
                          min="0"
                          max="59"
                          class="block w-full rounded-md border-0 py-1.5 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                          placeholder="0" 
                        />
                        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                          <span class="text-gray-500 sm:text-sm">min</span>
                        </div>
                      </div>
                    </div>
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

              <!-- Visibility Selector -->
              <div class="col-span-full">
                <VisibilitySelector
                  v-model:visibility="form.visibility"
                  v-model:group-id="form.group_id"

                  v-model:hide-details="form.hide_details"
                  :organization-id="form.organization_id"
                />
              </div>

              <!-- Show on Weekly Schedule Toggle -->
              <div class="col-span-full" v-if="form.visibility === 'public_approved'">
                <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="flex items-center justify-between">
                    <div class="flex-1">
                      <h4 class="text-sm font-medium text-gray-900">Afficher sur l'emploi du temps global</h4>
                      <p class="text-xs text-gray-500 mt-1">
                        Si activé, cet événement apparaîtra sur l'emploi du temps de tous les utilisateurs qui ont activé l'option "Afficher les événements globaux", même s'ils ne sont pas abonnés à votre organisation.
                      </p>
                    </div>
                    <button
                      type="button"
                      @click="form.show_on_schedule = !form.show_on_schedule"
                      :class="[
                        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2',
                        form.show_on_schedule ? 'bg-indigo-600' : 'bg-gray-200'
                      ]"
                    >
                      <span :class="[
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                        form.show_on_schedule ? 'translate-x-5' : 'translate-x-0'
                      ]" />
                    </button>
                  </div>
                </div>
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
                    class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                  />
                </div>
                <div class="sm:col-span-6">
                  <input 
                    v-model="link.url"
                    type="url"
                    placeholder="https://..."
                    class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
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

        <div class="mt-6 flex items-center justify-end gap-x-6">
          <router-link to="/" class="text-sm font-semibold leading-6 text-gray-900">Annuler</router-link>
          <button 
            type="submit" 
            :disabled="loading || !form.organization_id"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
          >
            {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { useAuth } from '../composables/useAuth'
import { localToUtc } from '../utils/dateUtils'
import OrganizationSelector from '../components/OrganizationSelector.vue'
import ImageUpload from '../components/ImageUpload.vue'
import CollapsibleCard from '../components/CollapsibleCard.vue'
import VisibilitySelector from '../components/VisibilitySelector.vue'
import TagSelector from '../components/TagSelector.vue'
import { PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const { user } = useAuth()

const form = ref({
  organization_id: '',
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  location: '',
  location_url: '',
  poster_url: '',
  visibility: 'public_pending',

  hide_details: false,
  group_id: null,
  tag_ids: [],
  show_on_schedule: false,
  links: [],
  guest_organization_ids: []
})

const userOrganizations = ref([])
const error = ref('')
const loading = ref(false)
const allOrganizations = ref([])
const isGuestOrgsOpen = ref(false)

const timeForm = ref({
  date: '',
  time: '',
  durationHours: 0,
  durationMinutes: 0
})

// Helper to format date for datetime-local input
const formatDateTimeLocal = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const updateTimeFromComponents = () => {
  if (!timeForm.value.date || !timeForm.value.time) return
  
  const startDateTime = new Date(`${timeForm.value.date}T${timeForm.value.time}`)
  form.value.start_time = formatDateTimeLocal(startDateTime)
  
  const durationMs = (timeForm.value.durationHours * 60 * 60 * 1000) + (timeForm.value.durationMinutes * 60 * 1000)
  const endDateTime = new Date(startDateTime.getTime() + durationMs)
  form.value.end_time = formatDateTimeLocal(endDateTime)
}

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
      organization_id: form.value.organization_id,
      visibility: form.value.visibility,
      group_id: form.value.group_id,
      tag_ids: form.value.tag_ids,
      show_on_schedule: form.value.show_on_schedule,
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
  
  // Initialize time with defaults (next hour, duration 1h)
  const now = new Date()
  now.setMinutes(0)
  now.setSeconds(0)
  now.setMilliseconds(0)
  now.setHours(now.getHours() + 1)
  
  timeForm.value.date = formatDateTimeLocal(now).split('T')[0]
  timeForm.value.time = formatDateTimeLocal(now).split('T')[1]
  timeForm.value.durationHours = 1
  timeForm.value.durationMinutes = 0
  
  updateTimeFromComponents()
})
</script>
