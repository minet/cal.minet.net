<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Hero / Header Section -->
    <div class="bg-white shadow sticky top-0 z-30">
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center">
        <div class="flex items-center">
          <img v-if="!isAuthenticated" src="/CalendINT_text.svg" alt="Calend'INT" class="hidden md:block h-16 w-auto mr-6" />
          <div>
            <DocsHint path="/decouvrir-evenements" search="Découvrir les événements">
              <h1 class="text-3xl font-bold tracking-tight text-gray-900">À venir</h1>
            </DocsHint>
            <p class="mt-2 text-sm text-gray-500">Découvrez les prochains événements.</p>
          </div>
        </div>
        
        <!-- Desktop Actions -->
        <div class="mt-4 sm:mt-0 flex items-center space-x-4">
          <router-link to="/dashboard" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
            <CalendarIcon class="h-5 w-5 mr-2" />
            Accéder au calendrier
          </router-link>
          
          <template v-if="isAuthenticated">
            <router-link to="/profile" class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
              <UserIcon class="h-5 w-5 mr-2 text-gray-400" />
              Mon Profil
            </router-link>
          </template>
          <template v-else>
             <router-link to="/login" class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
              <ArrowRightOnRectangleIcon class="h-5 w-5 mr-2 text-gray-400" />
              Se connecter
            </router-link>
          </template>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      
      <!-- Featured Events Section -->
      <div v-if="featuredEvents.length > 0" class="mb-12">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <FeaturedEventCard
            v-for="event in featuredEvents"
            :key="event.id"
            :event="event"
          />
        </div>
      </div>

      <!-- Events List Grouped -->
      <div v-if="allEvents.length === 0 && !loading" class="text-center py-20">
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Aucun événement à venir</h3>
        <p class="mt-1 text-sm text-gray-500">Revenez plus tard pour voir les nouveautés !</p>
      </div>

      <div v-else>
        <template v-for="(group, index) in groupedEvents" :key="index">
            <div class="mb-8 relative">
                <div class="sticky top-20 z-10 bg-gray-50/95 backdrop-blur py-2 mb-4 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                        <CalendarIcon class="h-5 w-5 mr-2 text-indigo-600"/>
                        {{ group.label }}
                    </h2>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,18rem)] gap-6 justify-start">
                    <EventCard
                        v-for="event in group.events"
                        :key="event.id"
                        :event="event"
                    />
                </div>
            </div>
        </template>
      </div>

      <!-- Loading State / Spinner -->
      <div v-if="loading" class="flex justify-center items-center py-10">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
      </div>
      
      <!-- End of List -->
      <div v-if="!hasMore && allEvents.length > 0 && !loading" class="py-10 text-center text-gray-400 text-sm">
        Vous avez tout vu !
      </div>
    </main>

    <!-- Mobile FAB -->
    <div class="fixed bottom-6 right-6 sm:hidden z-40">
      <router-link to="/dashboard" class="flex items-center justify-center h-14 w-14 rounded-full bg-indigo-600 text-white shadow-lg focus:outline-none hover:bg-indigo-500 transition-colors">
        <CalendarIcon class="h-6 w-6" />
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import type { EventRead } from '@/api/types'
import EventCard from '../components/EventCard.vue'
import FeaturedEventCard from '../components/FeaturedEventCard.vue'
import { useAuth } from '../composables/useAuth'
import { CalendarIcon, UserIcon, ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline'
import { formatLocalDate } from '../utils/dateUtils'

const { initialize, setToken, isAuthenticated } = useAuth()
const router = useRouter()
const allEvents = ref<EventRead[]>([])
const featuredEvents = ref<EventRead[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 12
const hasMore = ref(true)

// Fetch events function
const fetchEvents = async () => {
    if (loading.value || !hasMore.value) return

    try {
        loading.value = true
        const response = await api.events.list_events({
            page: page.value,
            size: pageSize,
            upcoming: true,
        })

        const newEvents = response.items
        const total = response.total
        
        // Append new events (filtering duplicates just in case)
        const existingIds = new Set(allEvents.value.map(e => e.id))
        const uniqueNewEvents = newEvents.filter(e => !existingIds.has(e.id))
        allEvents.value = [...allEvents.value, ...uniqueNewEvents]
        
        // Check if we have more pages
        if (allEvents.value.length >= total || newEvents.length < pageSize) {
            hasMore.value = false
        } else {
            page.value++ // Prepare next page
        }

    } catch (error) {
        console.error('Error fetching events:', error)
    } finally {
        loading.value = false
    }
}

const fetchFeatured = async () => {
    try {
        const response = await api.events.list_events({
            featured: true,
            size: 5,
            upcoming: true,
        })
        featuredEvents.value = response.items
    } catch (error) {
        console.error("Failed to load featured events", error)
    }
}

// Grouping Logic
const groupedEvents = computed(() => {
    const groups: { label: string; events: EventRead[] }[] = []
    const now = new Date()
    // Reset time part for accurate day comparison
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const dayAfterTomorrow = new Date(today)
    dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 2)
    const threeDaysLimit = new Date(today)
    threeDaysLimit.setDate(threeDaysLimit.getDate() + 3)
    
    // 3 Weeks + Today Limit (21 days)
    const threeWeeksLimit = new Date(today)
    threeWeeksLimit.setDate(threeWeeksLimit.getDate() + 21)

    // Helper to check same day
    const isSameDay = (d1: Date, d2: Date): boolean => {
        return d1.getFullYear() === d2.getFullYear() &&
               d1.getMonth() === d2.getMonth() &&
               d1.getDate() === d2.getDate()
    }

    // Helper to get Week Label
    const getWeekLabel = (d: Date): string => {
        // Find Monday of the week
        const day = d.getDay() || 7 // Get current day number, converting Sun (0) to 7
        if (day !== 1) d.setHours(-24 * (day - 1)) // Set to Monday
        // Re-format
        const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long' }
        return `Semaine du ${d.toLocaleDateString('fr-FR', options)}`
    }

    // Helper to get Month Label
    const getMonthLabel = (d: Date): string => {
        const options: Intl.DateTimeFormatOptions = { month: 'long', year: 'numeric' }
        const label = d.toLocaleDateString('fr-FR', options)
        return `Mois de ${label}` // e.g. "Mois de février 2026"
    }

    const eventsCopy = [...allEvents.value]
    // Sort just in case backend didn't (though it does)
    eventsCopy.sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())

    let currentGroup: { label: string; events: EventRead[] } | null = null

    eventsCopy.forEach(event => {
        const eventDate = new Date(event.start_time)
        // Reset time for comparison
        const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate())
        
        let label = ''

        if (eventDay < threeDaysLimit) {
            // It's in the next 3 days
            if (isSameDay(eventDay, today)) {
                label = "Aujourd'hui"
            } else if (isSameDay(eventDay, tomorrow)) {
                label = "Demain"
            } else if (isSameDay(eventDay, dayAfterTomorrow)) {
                // Day name (e.g. "Mercredi")
                label = eventDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
                label = label.charAt(0).toUpperCase() + label.slice(1) // Capitalize
            } else {
                // Should't happen given the if condition but fallback
                label = eventDate.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
            }
        } else if (eventDay < threeWeeksLimit) {
            // It's later but within 3 weeks -> Group by Week
            label = getWeekLabel(new Date(eventDay)) // Pass copy to avoid mutation
        } else {
            // After 3 weeks -> Group by Month
            label = getMonthLabel(new Date(eventDay))
        }

        if (!currentGroup || currentGroup.label !== label) {
            currentGroup = { label: label, events: [] }
            groups.push(currentGroup)
        }
        currentGroup.events.push(event)
    })

    return groups
})


const handleScroll = () => {
  const scrollPosition = window.innerHeight + window.scrollY
  const documentHeight = document.documentElement.offsetHeight
  
  if (scrollPosition >= documentHeight - 200) { // Increased buffer
    fetchEvents()
  }
}

onMounted(async () => {
  // Check for OIDC callback token in URL
  const urlParams = new URLSearchParams(window.location.search)
  const authToken = urlParams.get('token')
  
  if (authToken) {
    await setToken(authToken)
    window.history.replaceState({}, document.title, '/')
    const redirectUrl = localStorage.getItem('auth_redirect_url')
    if (redirectUrl) {
      localStorage.removeItem('auth_redirect_url')
      router.push(redirectUrl)
      return
    }
  }

  await initialize()
  fetchFeatured()
  // Initial fetch
  fetchEvents()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
