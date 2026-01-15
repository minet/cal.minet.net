<template>
  <div class="max-w-6xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Demandes d'approbation</h1>
        <p class="mt-2 text-sm text-gray-600">Événements en attente de validation</p>
      </div>
    </header>

    <div class="mb-6 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          @click="currentTab = 'pending'"
          :class="[
            currentTab === 'pending'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium'
          ]"
        >
          En attente
          <span
            v-if="pendingEvents.length > 0"
            :class="[
              currentTab === 'pending' ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-900',
              'ml-3 hidden rounded-full py-0.5 px-2.5 text-xs font-medium md:inline-block'
            ]"
          >
            {{ pendingEvents.length }}
          </span>
        </button>
        <button
          @click="currentTab = 'processed'"
          :class="[
            currentTab === 'processed'
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium'
          ]"
        >
          Traité
        </button>
      </nav>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- PENDING TAB -->
    <div v-else-if="currentTab === 'pending'">
      <div v-if="pendingEvents.length === 0" class="bg-white shadow-sm rounded-lg p-12 text-center">
        <CheckBadgeIcon class="mx-auto h-12 w-12 text-emerald-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">Aucune demande en attente</h3>
        <p class="mt-2 text-sm text-gray-500">Tous les événements ont été traités</p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="event in pendingEvents" 
          :key="event.id"
          class="bg-white shadow-sm rounded-lg overflow-hidden transition hover:shadow-md"
        >
          <router-link :to="`/events/${event.id}`" class="block p-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <img 
                    v-if="event.organization?.logo_url"
                    :src="event.organization.logo_url"
                    :alt="event.organization.name"
                    class="h-10 w-10 rounded-full object-cover"
                  />
                  <div 
                    v-else
                    class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold"
                  >
                    {{ event.organization?.name?.charAt(0) || '?' }}
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ event.title }}</h3>
                    <p class="text-sm text-gray-500">{{ event.organization?.name }}</p>
                  </div>
                </div>
                
                <p v-if="event.description" class="text-gray-600 text-sm mt-2 line-clamp-2">
                  {{ event.description }}
                </p>

                <div class="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
                  <div class="flex items-center gap-1">
                    <CalendarIcon class="h-4 w-4" />
                    <span>{{ formatDate(event.start_time) }}</span>
                  </div>
                  <div v-if="event.location" class="flex items-center gap-1">
                    <MapPinIcon class="h-4 w-4" />
                    <span>{{ event.location }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <UserIcon class="h-4 w-4" />
                    <span>{{ event.created_by?.full_name || event.created_by?.email }}</span>
                  </div>
                </div>
              </div>

              <div class="flex flex-col sm:flex-row gap-2 mt-4 sm:mt-0 sm:ml-4 w-full sm:w-auto" @click.prevent.stop>
                <button
                  @click="approveEvent(event)"
                  :disabled="processingId === event.id"
                  class="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium text-white bg-emerald-500 hover:bg-emerald-600 rounded-lg transition-colors disabled:opacity-50"
                >
                  <CheckIcon class="h-4 w-4" />
                  Approuver
                </button>
                <button
                  @click="openRejectModal(event)"
                  :disabled="processingId === event.id"
                  class="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50"
                >
                  <XMarkIcon class="h-4 w-4" />
                  Refuser
                </button>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <!-- PROCESSED TAB -->
    <div v-else-if="currentTab === 'processed'">
      <div v-if="processedEvents.length === 0" class="bg-white shadow-sm rounded-lg p-12 text-center">
        <ClipboardDocumentCheckIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">Aucun historique</h3>
        <p class="mt-2 text-sm text-gray-500">Les événements traités apparaîtront ici</p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="event in processedEvents" 
          :key="event.id"
          class="bg-white shadow-sm rounded-lg overflow-hidden transition hover:shadow-md"
        >
          <router-link :to="`/events/${event.id}`" class="block p-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <img 
                    v-if="event.organization?.logo_url"
                    :src="event.organization.logo_url"
                    :alt="event.organization.name"
                    class="h-10 w-10 rounded-full object-cover"
                  />
                  <div 
                    v-else
                    class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold"
                  >
                    {{ event.organization?.name?.charAt(0) || '?' }}
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ event.title }}</h3>
                    <p class="text-sm text-gray-500">{{ event.organization?.name }}</p>
                  </div>
                  <span 
                    :class="[
                      event.visibility === 'public_approved' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800',
                      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'
                    ]"
                  >
                    {{ event.visibility === 'public_approved' ? 'Approuvé' : 'Refusé' }}
                  </span>
                </div>
                
                <p v-if="event.rejection_message" class="text-red-600 text-sm mt-2 bg-red-50 p-2 rounded">
                  <span class="font-medium">Motif :</span> {{ event.rejection_message }}
                </p>

                <div class="mt-4 flex flex-wrap gap-4 text-sm text-gray-500">
                  <div class="flex items-center gap-1">
                    <CalendarIcon class="h-4 w-4" />
                    <span>{{ formatDate(event.start_time) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <UserIcon class="h-4 w-4" />
                    <span>{{ event.created_by?.full_name || event.created_by?.email }}</span>
                  </div>
                </div>
              </div>

              <div class="flex flex-col sm:flex-row gap-2 mt-4 sm:mt-0 sm:ml-4 w-full sm:w-auto" @click.prevent.stop>
                <button
                  @click="resetStatus(event)"
                  :disabled="processingId === event.id"
                  class="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
                >
                  <ArrowPathIcon class="h-4 w-4" />
                  Annuler
                </button>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="closeRejectModal"></div>
        <div class="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Refuser l'événement</h3>
          <p class="text-sm text-gray-600 mb-4">
            Expliquez pourquoi cet événement est refusé. Ce message sera visible par l'organisateur.
          </p>
          <textarea
            v-model="rejectMessage"
            rows="3"
            placeholder="Raison du refus..."
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          ></textarea>
          <div class="mt-4 flex justify-end gap-3">
            <button
              @click="closeRejectModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              Annuler
            </button>
            <button
              @click="rejectEvent"
              :disabled="!rejectMessage.trim() || processingId"
              class="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg disabled:opacity-50"
            >
              Refuser
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { 
  CalendarIcon, 
  MapPinIcon, 
  UserIcon, 
  CheckIcon, 
  XMarkIcon,
  ClipboardDocumentCheckIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'
import { CheckBadgeIcon } from '@heroicons/vue/24/solid'
import api from '../utils/api'

const pendingEvents = ref([])
const processedEvents = ref([])
const loading = ref(true)
const processingId = ref(null)
const showRejectModal = ref(false)
const selectedEvent = ref(null)
const rejectMessage = ref('')
const currentTab = ref('pending')

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadPendingEvents = async () => {
  if (currentTab.value !== 'pending') return
  loading.value = true
  try {
    const response = await api.get('/events/pending-approvals')
    pendingEvents.value = response.data
  } catch (err) {
    console.error('Failed to load pending events:', err)
  } finally {
    loading.value = false
  }
}

const loadProcessedEvents = async () => {
  if (currentTab.value !== 'processed') return
  loading.value = true
  try {
    const response = await api.get('/events/processed-approvals')
    processedEvents.value = response.data
  } catch (err) {
    console.error('Failed to load processed events:', err)
  } finally {
    loading.value = false
  }
}

const approveEvent = async (event) => {
  processingId.value = event.id
  try {
    await api.post(`/events/${event.id}/approve`)
    pendingEvents.value = pendingEvents.value.filter(e => e.id !== event.id)
  } catch (err) {
    console.error('Failed to approve event:', err)
    alert(err.response?.data?.detail || 'Échec de l\'approbation')
  } finally {
    processingId.value = null
  }
}

const openRejectModal = (event) => {
  selectedEvent.value = event
  rejectMessage.value = ''
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  selectedEvent.value = null
  rejectMessage.value = ''
}

const rejectEvent = async () => {
  if (!selectedEvent.value || !rejectMessage.value.trim()) return
  
  processingId.value = selectedEvent.value.id
  try {
    await api.post(`/events/${selectedEvent.value.id}/reject`, {
      message: rejectMessage.value.trim()
    })
    pendingEvents.value = pendingEvents.value.filter(e => e.id !== selectedEvent.value.id)
    closeRejectModal()
  } catch (err) {
    console.error('Failed to reject event:', err)
    alert(err.response?.data?.detail || 'Échec du refus')
  } finally {
    processingId.value = null
  }
}

const resetStatus = async (event) => {
  if (!confirm('Êtes-vous sûr de vouloir remettre cet événement en attente ?')) return

  processingId.value = event.id
  try {
    await api.post(`/events/${event.id}/reset-status`)
    processedEvents.value = processedEvents.value.filter(e => e.id !== event.id)
    // Optionally reload pending if we switched tabs, but simply removing from processed is enough here
  } catch (err) {
    console.error('Failed to reset status:', err)
    alert(err.response?.data?.detail || 'Échec de l\'annulation')
  } finally {
    processingId.value = null
  }
}

watch(currentTab, (newTab) => {
  if (newTab === 'pending') {
    loadPendingEvents()
  } else {
    loadProcessedEvents()
  }
})

onMounted(() => {
  loadPendingEvents()
})
</script>
