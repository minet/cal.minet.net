<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Hero / Header Section -->
    <div class="bg-white shadow sticky top-0 z-30">
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">À venir</h1>
          <p class="mt-2 text-sm text-gray-500">Découvrez les prochains événements.</p>
        </div>
        
        <!-- Desktop Actions -->
        <div class="mt-4 sm:mt-0 flex items-center space-x-4">
          <template v-if="isAuthenticated">
            <router-link to="/dashboard" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
              <CalendarIcon class="h-5 w-5 mr-2" />
              Accéder au calendrier
            </router-link>
            <router-link to="/profile" class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
              <UserIcon class="h-5 w-5 mr-2 text-gray-400" />
              Mon Profil
            </router-link>
          </template>
          <template v-else>
             <router-link to="/login" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
              <ArrowRightOnRectangleIcon class="h-5 w-5 mr-2" />
              Se connecter
            </router-link>
          </template>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="allEvents.length === 0" class="text-center py-20">
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Aucun événement à venir</h3>
        <p class="mt-1 text-sm text-gray-500">Revenez plus tard pour voir les nouveautés !</p>
      </div>

      <!-- Events Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,18rem)] gap-6 justify-center">
        <EventCard
          v-for="event in visibleEvents"
          :key="event.id"
          :event="event"
        />
      </div>

      <!-- Loading More / End of List -->
      <div v-if="visibleEvents.length < allEvents.length && !loading" class="py-10 text-center">
        <p class="text-gray-500 text-sm">Chargement...</p>
      </div>
      <div v-if="visibleEvents.length === allEvents.length && allEvents.length > 0" class="py-10 text-center text-gray-400 text-sm">
        Vous avez tout vu !
      </div>
    </main>

    <!-- Mobile FAB -->
    <div class="fixed bottom-6 right-6 sm:hidden z-40">
      <template v-if="isAuthenticated">
        <router-link to="/dashboard" class="flex items-center justify-center h-14 w-14 rounded-full bg-indigo-600 text-white shadow-lg focus:outline-none hover:bg-indigo-500 transition-colors">
          <CalendarIcon class="h-6 w-6" />
        </router-link>
      </template>
      <template v-else>
        <router-link to="/login" class="flex items-center justify-center h-14 w-14 rounded-full bg-indigo-600 text-white shadow-lg focus:outline-none hover:bg-indigo-500 transition-colors">
          <ArrowRightOnRectangleIcon class="h-6 w-6" />
        </router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import EventCard from '../components/EventCard.vue'
import { useAuth } from '../composables/useAuth'
import { CalendarIcon, UserIcon, ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline'

const { initialize, setToken, isAuthenticated } = useAuth()
const router = useRouter()
const allEvents = ref([])
const visibleEvents = ref([])
const loading = ref(true)
const page = ref(1)
const pageSize = 12

// Fetch events
const fetchEvents = async () => {
  try {
    loading.value = true
    const response = await api.get('/events/')
    
    // Filter and Sort
    const now = new Date()
    const events = response.data
      .filter(e => new Date(e.start_time) >= now) // upcoming only
      .sort((a, b) => new Date(a.start_time) - new Date(b.start_time)) // closest date first

    allEvents.value = events
    loadMore() // Initial load
  } catch (error) {
    console.error('Error fetching events:', error)
  } finally {
    loading.value = false
  }
}

// Client-side pagination / Infinite scroll logic
const loadMore = () => {
  const currentLen = visibleEvents.value.length
  const totalLen = allEvents.value.length
  
  if (currentLen >= totalLen) return

  const nextChunk = allEvents.value.slice(currentLen, currentLen + pageSize)
  visibleEvents.value = [...visibleEvents.value, ...nextChunk]
}

// Infinite Scroll handler
const handleScroll = () => {
  const scrollPosition = window.innerHeight + window.scrollY
  const documentHeight = document.documentElement.offsetHeight
  
  // Trigger loadMore when we are close to the bottom (100px buffer)
  if (scrollPosition >= documentHeight - 100) {
    loadMore()
  }
}

onMounted(async () => {
  // Check for OIDC callback token in URL
  const urlParams = new URLSearchParams(window.location.search)
  const authToken = urlParams.get('token')
  
  if (authToken) {
    await setToken(authToken)
    // Clean up URL
    window.history.replaceState({}, document.title, '/')
    
    // Check for redirect URL
    const redirectUrl = sessionStorage.getItem('auth_redirect_url')
    if (redirectUrl) {
      sessionStorage.removeItem('auth_redirect_url')
      // Use router if it's a path, or window location if it's full URL (though we stored path)
      router.push(redirectUrl)
      return // Don't fetch events if redirecting
    }
  }

  await initialize()
  fetchEvents()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
