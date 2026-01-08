<template>
  <div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Calendrier</h1>
          <div class="flex items-center space-x-2">
            <button @click="previousPeriod" class="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronLeftIcon class="h-5 w-5 text-gray-600" />
            </button>
            <span class="text-sm font-medium text-gray-700 min-w-[200px] text-center">
              {{ currentPeriodLabel }}
            </span>
            <button @click="nextPeriod" class="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronRightIcon class="h-5 w-5 text-gray-600" />
            </button>
            <button @click="goToToday" class="ml-2 px-3 py-1 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg">
              Aujourd'hui
            </button>
          </div>
        </div>
        <div class="flex space-x-3">
          <button 
            @click="toggleView" 
            type="button" 
            class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            <component :is="viewType === 'month' ? CalendarIcon : CalendarDaysIcon" class="h-5 w-5 mr-2 text-gray-500" />
            {{ viewType === 'month' ? 'Semaine' : 'Mois' }}
          </button>
          <router-link 
            v-if="canCreateEvent"
            to="/events/create"
            class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            Ajouter un événement
          </router-link>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-sm text-gray-500">Chargement des événements...</p>
    </div>

    <!-- Month View -->
    <div v-else-if="viewType === 'month'" class="bg-white shadow-sm rounded-lg overflow-hidden">
      <!-- Day Headers -->
      <div class="grid grid-cols-7 gap-px border-b border-gray-300 bg-gray-200 text-center text-xs font-semibold leading-6 text-gray-700">
        <div class="bg-white py-2">Lun</div>
        <div class="bg-white py-2">Mar</div>
        <div class="bg-white py-2">Mer</div>
        <div class="bg-white py-2">Jeu</div>
        <div class="bg-white py-2">Ven</div>
        <div class="bg-white py-2">Sam</div>
        <div class="bg-white py-2">Dim</div>
      </div>
      
      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 gap-px bg-gray-200">
        <div 
          v-for="day in monthDays" 
          :key="day.date" 
          class="relative bg-white px-2 py-2 min-h-[100px]" 
          :class="{ 'bg-gray-50 text-gray-400': !day.isCurrentMonth }"
        >
          <time 
            :datetime="day.date" 
            class="text-sm"
            :class="day.isToday ? 'flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 font-semibold text-white' : ''"
          >
            {{ day.dayNumber }}
          </time>
          <ol v-if="day.events.length > 0" class="mt-2 space-y-1">
            <li v-for="event in day.events.slice(0, 3)" :key="event.id">
              <router-link 
                :to="`/events/${event.id}`" 
                :class="[
                  'group flex items-center px-2 py-1 text-xs rounded transition-colors',
                  event.is_draft ? 'opacity-50' : ''
                ]"
                :style="{ 
                  backgroundColor: getOrgColor(event.organization?.color_chroma/20, event.organization?.color_hue, 1),
                  color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.3)
                }"
              >
                <span :class="[
                  'flex-auto truncate font-medium',
                  event.is_draft ? 'italic' : ''
                ]">
                  {{ event.is_draft ? '(Brouillon) ' : '' }}{{ event.title }}
                </span>
                <time 
                  class="ml-2 hidden flex-none xl:block"
                  style="opacity: 0.8"
                >
                  {{ formatTime(event.start_time) }}
                </time>
              </router-link>
            </li>
            <li v-if="day.events.length > 3" class="text-xs text-gray-500 px-2">
              +{{ day.events.length - 3 }} plus
            </li>
          </ol>
        </div>
      </div>
    </div>

    <!-- Week View -->
    <div v-else class="bg-white shadow-sm rounded-lg overflow-hidden">
      <!-- Day Headers -->
      <div class="grid grid-cols-7 gap-px border-b border-gray-300 bg-gray-200 text-center text-xs font-semibold leading-6 text-gray-700">
        <div v-for="day in weekDays" :key="day.date" class="bg-white py-3">
          <div class="text-gray-900">{{ day.dayName }}</div>
          <div 
            class="mt-1 flex items-center justify-center"
            :class="day.isToday ? 'mx-auto flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 font-semibold text-white' : 'text-gray-500'"
          >
            {{ day.dayNumber }}
          </div>
        </div>
      </div>
      
      <!-- Week Grid -->
      <div class="grid grid-cols-7 gap-px bg-gray-200 auto-rows-fr" style="min-height: 500px;">
        <div v-for="day in weekDays" :key="day.date" class="relative bg-white px-2 py-4">
          <ol v-if="day.events.length > 0" class="space-y-2">
            <li v-for="event in day.events" :key="event.id">
              <router-link 
                :to="`/events/${event.id}`"
                :class="[
                  'group block p-2 rounded-lg transition-colors',
                  event.is_draft ? 'opacity-60' : ''
                ]"
                :style="{ 
                  backgroundColor: getOrgColor(event.organization?.color_chroma/20, event.organization?.color_hue, 1),
                  borderLeft: `3px solid ${getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.6)}`
                }"
              >
                <p :class="[
                  'text-sm font-medium',
                  event.is_draft ? 'italic' : ''
                ]"
                :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.3) }"
                >
                  {{ event.is_draft ? '(Brouillon) ' : '' }}{{ event.title }}
                </p>
                <div 
                  class="flex items-center text-xs mt-1" 
                  :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.5) }"
                >
                  <ClockIcon class="h-3 w-3 mr-1" />
                  {{ formatTime(event.start_time) }}
                </div>
                <div 
                  v-if="event.location" 
                  class="flex items-center text-xs mt-1"
                  :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.5) }"
                >
                  <MapPinIcon class="h-3 w-3 mr-1" />
                  {{ event.location }}
                </div>
              </router-link>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { formatLocalDate } from '../utils/dateUtils'
import { PlusIcon, CalendarIcon, CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon, ClockIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'
import { getOrgColor } from '../utils/colorUtils'

const viewType = ref('month') // 'month' or 'week'
const { user, initialize, setToken, isSuperAdmin } = useAuth()
const currentDate = ref(new Date())
const events = ref([])
const userMemberships = ref([])
const loading = ref(false)

const toggleView = () => {
  viewType.value = viewType.value === 'month' ? 'week' : 'month'
}

const canCreateEvent = computed(() => {
  if (isSuperAdmin.value) return true
  return userMemberships.value.some(m => 
    m.role === 'org_admin' || m.role === 'org_member'
  )
})

const currentPeriodLabel = computed(() => {
  if (viewType.value === 'month') {
    return currentDate.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  } else {
    const weekStart = getWeekStart(currentDate.value)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 6)
    return `${weekStart.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })} - ${weekEnd.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}`
  }
})

const previousPeriod = () => {
  if (viewType.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  } else {
    currentDate.value = new Date(currentDate.value.getTime() - 7 * 24 * 60 * 60 * 1000)
  }
}

const nextPeriod = () => {
  if (viewType.value === 'month') {
    currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  } else {
    currentDate.value = new Date(currentDate.value.getTime() + 7 * 24 * 60 * 60 * 1000)
  }
}

const goToToday = () => {
  currentDate.value = new Date()
}

const getWeekStart = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Adjust when day is Sunday
  return new Date(d.setDate(diff))
}

const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  const firstDayOfWeek = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1
  const days = []
  
  // Previous month days
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDay - i)
    days.push(createDayObject(date, false))
  }
  
  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    days.push(createDayObject(date, true))
  }
  
  // Next month days
  const remainingDays = 35 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i)
    days.push(createDayObject(date, false))
  }
  
  return days
})

const weekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  const days = []
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart)
    date.setDate(date.getDate() + i)
    days.push({
      ...createDayObject(date, true),
      dayName: date.toLocaleDateString('fr-FR', { weekday: 'short' })
    })
  }
  
  return days
})

const createDayObject = (date, isCurrentMonth) => {
  const dateStr = date.toISOString().split('T')[0]
  const today = new Date()
  const isToday = dateStr === today.toISOString().split('T')[0]
  
  return {
    date: dateStr,
    dayNumber: date.getDate(),
    isCurrentMonth,
    isToday,
    events: getEventsForDate(dateStr)
  }
}

const getEventsForDate = (dateStr) => {
  return events.value.filter(event => {
    const eventDate = new Date(event.start_time).toISOString().split('T')[0]
    return eventDate === dateStr
  })
}

const formatTime = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await api.get('/events/')
    events.value = response.data
    
    // If authenticated, also load draft events where user has permission
    if (localStorage.getItem('auth_token')) {
      try {
        const draftsResponse = await api.get('/events/drafts')
        // Merge draft events into the main events array
        events.value = [...events.value, ...draftsResponse.data]
      } catch (error) {
        // Silently fail if drafts endpoint errors (user may not have permissions)
        console.debug('Could not load draft events:', error)
      }
    }
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loading.value = false
  }
}

const loadUserMemberships = async () => {
  try {
    const response = await api.get('/users/me/memberships')
    userMemberships.value = response.data
  } catch (error) {
    console.error('Failed to load user memberships:', error)
  }
}

// Watch for date changes to reload events if needed
watch(currentDate, () => {
  // Could implement smart loading based on visible date range
})

onMounted(async () => {
  // Check for OIDC callback token in URL
  const urlParams = new URLSearchParams(window.location.search)
  const authToken = urlParams.get('token')
  
  if (authToken) {
    await setToken(authToken)
    // Clean up URL
    window.history.replaceState({}, document.title, '/')
  }
  
  await initialize()
  await loadEvents()
})
</script>

