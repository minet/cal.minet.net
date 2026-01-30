<template>
  <div class="max-w-6xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 sm:gap-0">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Mes événements</h1>
          <p class="mt-2 text-sm text-gray-600">Gérez les événements de vos organisations</p>
        </div>
        <router-link 
          to="/events/create"
          class="w-full sm:w-auto justify-center inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-500 transition-colors"
        >
          <PlusIcon class="h-5 w-5" />
          Nouvel événement
        </router-link>
      </div>
    </header>

    <!-- Filters -->
    <div class="bg-white shadow-sm rounded-lg p-4 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">Organisation</label>
          <select 
            v-model="selectedOrg"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Toutes les organisations</option>
            <option v-for="org in organizations" :key="org.id" :value="org.id">
              {{ org.name }}
            </option>
          </select>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            @click="selectedStatus = filter.value"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
              selectedStatus === filter.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="filteredEvents.length === 0" class="bg-white shadow-sm rounded-lg p-12 text-center">
      <CalendarDaysIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-4 text-lg font-medium text-gray-900">Aucun événement</h3>
      <p class="mt-2 text-sm text-gray-500">
        {{ selectedStatus ? 'Aucun événement avec ce statut' : 'Vous n\'avez pas encore créé d\'événements' }}
      </p>
      <router-link 
        to="/events/create"
        class="mt-4 inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-500 text-sm font-medium"
      >
        <PlusIcon class="h-4 w-4" />
        Créer un événement
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div 
        v-for="event in filteredEvents" 
        :key="event.id"
        class="bg-white shadow-sm rounded-lg overflow-hidden hover:shadow-md transition-shadow"
      >
        <router-link :to="`/events/${event.id}`" class="block p-6">
          <div class="flex flex-col sm:flex-row items-start justify-between">
            <div class="flex-1 w-full">
              <div class="flex items-center gap-3 mb-2">
                <div 
                  v-if="event.organization?.logo_url"
                  class="h-10 w-10 rounded-full flex items-center justify-center overflow-hidden"
                  :style="{ backgroundColor: event.organization.color_secondary || '#f3f4f6' }"
                >
                  <img 
                    :src="event.organization.logo_url"
                    :alt="event.organization.name"
                    class="h-full w-full object-cover"
                  />
                </div>
                <div 
                  v-else
                  class="h-10 w-10 rounded-full flex items-center justify-center font-semibold"
                  :style="{ 
                    backgroundColor: event.organization?.color_secondary || '#f3f4f6',
                    color: event.organization?.color_primary || '#4f46e5'
                  }"
                >
                  {{ event.organization?.name?.charAt(0) || '?' }}
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">{{ event.title }}</h3>
                  <p class="text-sm text-gray-500">{{ event.organization?.name }}</p>
                </div>
              </div>

              <div class="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
                <div class="flex items-center gap-1">
                  <CalendarIcon class="h-4 w-4" />
                  <span>{{ formatDate(event.start_time) }}</span>
                </div>
                <div v-if="event.location" class="flex items-center gap-1">
                  <MapPinIcon class="h-4 w-4" />
                  <span>{{ event.location }}</span>
                </div>
              </div>

              <!-- Rejection message -->
              <div v-if="event.visibility === 'public_rejected' && event.rejection_message" class="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
                <p class="text-sm text-red-700">
                  <span class="font-medium">Motif du refus :</span> {{ event.rejection_message }}
                </p>
              </div>
            </div>

            <div class="mt-4 sm:mt-0 ml-0 sm:ml-4 flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-start w-full sm:w-auto gap-2">
              <!-- Status Badge -->
              <span :class="getStatusClasses(event.visibility)">
                {{ getStatusLabel(event.visibility) }}
              </span>
              
              <!-- Quick actions -->
              <div class="flex gap-2">
                <router-link 
                  :to="`/events/${event.id}/edit`"
                  class="p-2 text-gray-400 hover:text-indigo-600 transition-colors"
                  @click.stop
                >
                  <PencilIcon class="h-5 w-5" />
                </router-link>
                <button 
                  v-if="event.visibility === 'draft' || event.visibility === 'public_rejected'"
                  @click.prevent="submitForApproval(event)"
                  class="p-2 text-gray-400 hover:text-emerald-600 transition-colors"
                  title="Soumettre pour approbation"
                >
                  <PaperAirplaneIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  CalendarIcon, 
  MapPinIcon, 
  PlusIcon,
  PencilIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'
import { CalendarDaysIcon } from '@heroicons/vue/24/solid'
import api from '../utils/api'

const events = ref([])
const organizations = ref([])
const loading = ref(true)
const selectedOrg = ref('')
const selectedStatus = ref('')

const statusFilters = [
  { label: 'Tous', value: '' },
  { label: 'Brouillons', value: 'draft' },
  { label: 'En attente', value: 'public_pending' },
  { label: 'Approuvés', value: 'public_approved' },
  { label: 'Refusés', value: 'public_rejected' }
]

const filteredEvents = computed(() => {
  return events.value.filter(event => {
    if (selectedOrg.value && event.organization?.id !== selectedOrg.value) {
      return false
    }
    if (selectedStatus.value && event.visibility !== selectedStatus.value) {
      return false
    }
    return true
  })
  .filter(event => new Date(event.end_time || event.start_time) >= new Date())
  .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
})

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClasses = (visibility) => {
  const base = 'px-3 py-1 text-xs font-medium rounded-full'
  switch (visibility) {
    case 'draft':
      return `${base} bg-amber-100 text-amber-800`
    case 'private':
      return `${base} bg-violet-100 text-violet-800`
    case 'public_pending':
      return `${base} bg-blue-100 text-blue-800`
    case 'public_approved':
      return `${base} bg-emerald-100 text-emerald-800`
    case 'public_rejected':
      return `${base} bg-red-100 text-red-800`
    default:
      return `${base} bg-gray-100 text-gray-800`
  }
}

const getStatusLabel = (visibility) => {
  switch (visibility) {
    case 'draft': return 'Brouillon'
    case 'private': return 'Privé'
    case 'public_pending': return 'En attente'
    case 'public_approved': return 'Approuvé'
    case 'public_rejected': return 'Refusé'
    default: return visibility
  }
}

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await api.get('/events/my-events')
    events.value = response.data
    
    // Extract unique organizations
    const orgsMap = new Map()
    events.value.forEach(event => {
      if (event.organization) {
        orgsMap.set(event.organization.id, event.organization)
      }
    })
    organizations.value = Array.from(orgsMap.values())
  } catch (err) {
    console.error('Failed to load events:', err)
  } finally {
    loading.value = false
  }
}

const submitForApproval = async (event) => {
  try {
    await api.post(`/events/${event.id}/submit-for-approval`)
    event.visibility = 'public_pending'
    event.rejection_message = null
  } catch (err) {
    console.error('Failed to submit for approval:', err)
    alert(err.response?.data?.detail || 'Échec de la soumission')
  }
}

onMounted(() => {
  loadEvents()
})
</script>
