<template>
  <div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 sm:gap-0">
        <DocsHint path="/decouvrir-evenements" search="Découvrir les événements">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Événements</h1>
        </DocsHint>
        <DocsHint path="/creer-un-evenement" search="Créer un événement">
          <router-link v-if="canCreateEvent" to="/events/create" class="w-full sm:w-auto text-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Ajouter un événement</router-link>
        </DocsHint>
      </div>
    </header>

    <!-- Filters -->
    <div class="bg-white shadow-sm rounded-lg p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Recherche</label>
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher un événement..."
            class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          />
        </div>
        <div>
          <Dropdown
            v-model="selectedOrganization"
            label="Organisation"
            :options="[
              { value: null, label: 'Toutes les organisations' },
              ...organizations.map(org => ({ value: org.id, label: org.name }))
            ]"
          />
        </div>
        <div class="flex items-end">
          <button 
            @click="clearFilters"
            class="w-full rounded-md bg-gray-200 px-3 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-300 mb-1"
          >
            Réinitialiser
          </button>
        </div>
      </div>
    </div>

    <!-- Events List -->
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>
      
      <div v-else-if="events.length === 0" class="text-center py-12">
        <p class="text-sm text-gray-500">Aucun événement trouvé</p>
      </div>

      <ul v-else role="list" class="divide-y divide-gray-100">
        <li v-for="event in events" :key="event.id">
          <router-link 
            :to="`/events/${event.id}`"
            class="flex flex-col sm:flex-row justify-between gap-x-6 py-5 px-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex min-w-0 gap-x-4">
              <div class="min-w-0 flex-auto">
                <p class="text-sm font-semibold leading-6 text-gray-900">
                  {{ event.title }}
                </p>
                <div class="mt-1 flex items-center gap-x-2 text-xs leading-5 text-gray-500">
                  <p class="truncate">{{ formatLocalDate(event.start_time) }}</p>
                  <svg v-if="event.location" viewBox="0 0 2 2" class="h-0.5 w-0.5 fill-current"><circle cx="1" cy="1" r="1" /></svg>
                  <p v-if="event.location" class="truncate">{{ event.location }}</p>
                </div>
              </div>
            </div>
            <div class="mt-2 sm:mt-0 flex flex-row sm:flex-col items-center sm:items-end gap-2 sm:gap-0 shrink-0">
              <p class="text-sm leading-6 text-gray-900">{{ event.organization?.name || 'N/A' }}</p>
              <span v-if="event.is_draft" class="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">Brouillon</span>
              <span v-else class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Publié</span>
            </div>
          </router-link>
        </li>
      </ul>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Page {{ currentPage }} sur {{ totalPages }}
        </div>
        <div class="flex space-x-2">
          <button 
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 rounded-md bg-gray-200 text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
          >
            Précédent
          </button>
          <button 
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-1 rounded-md bg-gray-200 text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
          >
            Suivant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { formatLocalDate } from '../utils/dateUtils'
import Dropdown from '../components/Dropdown.vue'
import { api } from '@/api'
import type { EventRead, OrganizationRead, MembershipWithOrganization } from '@/api/types'
import { useAuth } from '../composables/useAuth'

const events = ref<EventRead[]>([])
const organizations = ref<OrganizationRead[]>([])
const userMemberships = ref<MembershipWithOrganization[]>([])
const { isSuperAdmin } = useAuth()
const loading = ref(true)
const searchQuery = ref('')
const selectedOrganization = ref<string | null>(null)
const currentPage = ref(1)
const itemsPerPage = 20
const totalPages = ref(0)

// Check if user can create events
const canCreateEvent = computed(() => {
  if (isSuperAdmin.value) return true
  return userMemberships.value.some(m =>
    m.role === 'org_admin' || m.role === 'org_member'
  )
})

const loadEvents = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      size: itemsPerPage,
      upcoming: true,
      search: searchQuery.value || undefined,
      organization_id: selectedOrganization.value || undefined
    }
    
    const response = await api.events.list_events(params)
    events.value = response.items
    totalPages.value = response.pages
    
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loading.value = false
  }
}

// Watchers
watch([searchQuery, selectedOrganization], () => {
  currentPage.value = 1
  loadEvents()
})

watch(currentPage, () => {
  loadEvents()
})

const loadOrganizations = async () => {
  try {
    organizations.value = await api.organizations.list_organizations()
  } catch (error) {
    console.error('Failed to load organizations:', error)
  }
}

const loadUserMemberships = async () => {
    try {
        userMemberships.value = await api.users.get_user_memberships()
    } catch (error) {
        // If not authenticated, or error, just set empty
        console.debug('Failed to load memberships (probably not logged in):', error)
        userMemberships.value = []
    }
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedOrganization.value = null
}

onMounted(async () => {
  await loadUserMemberships()
  await loadEvents()
  await loadOrganizations()
})
</script>
