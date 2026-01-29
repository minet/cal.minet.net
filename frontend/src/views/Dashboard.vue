<template>
  <div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 sm:gap-0">
        <div class="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4 w-full sm:w-auto">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Calendrier</h1>
          <div class="flex items-center justify-center sm:justify-start space-x-2 w-full sm:w-auto">
            <button @click="previousPeriod" class="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronLeftIcon class="h-5 w-5 text-gray-600" />
            </button>
            <span 
              @click="goToToday" 
              class="text-sm font-medium text-gray-700 min-w-[200px] text-center cursor-pointer select-none hover:bg-gray-50 rounded py-1 transition-colors"
            >
              {{ currentPeriodLabel }}
            </span>
            <button @click="nextPeriod" class="p-2 hover:bg-gray-100 rounded-lg">
              <ChevronRightIcon class="h-5 w-5 text-gray-600" />
            </button>
            <button @click="goToToday" class="hidden sm:block ml-2 px-3 py-1 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg">
              Aujourd'hui
            </button>
          </div>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <button 
            @click="toggleView" 
            type="button" 
            class="hidden sm:inline-flex w-full justify-center sm:w-auto items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            <component :is="viewType === 'month' ? CalendarIcon : CalendarDaysIcon" class="h-5 w-5 mr-2 text-gray-500" />
            {{ viewType === 'month' ? 'Semaine' : 'Mois' }}
          </button>
          <router-link 
            v-if="canCreateEvent"
            to="/events/create"
            class="inline-flex w-full justify-center sm:w-auto items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
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
                :title="getEventTitle(event)"
                :class="[
                  'group flex items-center px-2 py-1 text-xs rounded transition-colors',
                  ['public_rejected', 'public_pending', 'private'].includes(event.visibility) ? 'border-2' : '',
                  event.visibility === 'public_rejected' ? 'border-red-500 opacity-25' : '',
                  event.visibility === 'public_pending' ? 'border-yellow-500 opacity-50' : '',
                  event.visibility === 'private' ? 'border-blue-500' : '',
                  (event.visibility === 'draft' || event.is_draft) ? 'opacity-50' : ''
                ]"
                :style="{ 
                  backgroundColor: getOrgColor(event.organization?.color_chroma/20, event.organization?.color_hue, 1),
                  color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.3)
                }"
              >
                <span :class="[
                  'flex-auto truncate font-medium',
                  (event.visibility === 'draft' || event.is_draft) ? 'italic' : ''
                ]">
                  {{ event.title }}
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
    <!-- Week View -->
    <div v-else class="bg-white shadow-sm rounded-lg overflow-hidden flex flex-col">
      <div ref="weekScrollContainer" class="overflow-x-auto w-full no-scrollbar">
        <div class="min-w-[1050px] bg-gray-200">
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
                    :title="getEventTitle(event)"
                    :class="[
                      'group block p-2 rounded-lg transition-colors',
                      ['public_rejected', 'public_pending', 'private'].includes(event.visibility) ? 'border-2' : '',
                      event.visibility === 'public_rejected' ? 'border-red-500 opacity-25' : '',
                      event.visibility === 'public_pending' ? 'border-yellow-500 opacity-50' : '',
                      event.visibility === 'private' ? 'border-blue-500' : '',
                      (event.visibility === 'draft' || event.is_draft) ? 'opacity-50' : ''
                    ]"
                    :style="{ 
                      backgroundColor: getOrgColor(event.organization?.color_chroma/20, event.organization?.color_hue, 1),
                      borderLeft: `3px solid ${getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.6)}`
                    }"
                  >
                    <!-- Organization Badges -->
                    <div class="flex items-center gap-1 mb-1.5">
                      <template v-if="event.guest_organizations && event.guest_organizations.length > 0">
                         <div class="flex -space-x-1.5">
                            <img 
                              :src="event.organization?.logo_url || `https://ui-avatars.com/api/?name=${event.organization?.name}&background=random`" 
                              class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                              :title="event.organization?.name"
                            />
                            <img 
                              v-for="guest in event.guest_organizations" 
                              :key="guest.id"
                              :src="guest.logo_url || `https://ui-avatars.com/api/?name=${guest.name}&background=random`" 
                              class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                              :title="guest.name"
                            />
                         </div>
                      </template>
                      <template v-else>
                         <div class="inline-flex items-center rounded-full bg-white/60 px-1.5 py-0.5 backdrop-blur-sm">
                            <img 
                              v-if="event.organization?.logo_url"
                              :src="event.organization.logo_url" 
                              class="mr-1 h-3 w-3 rounded-full object-cover"
                            />
                            <span class="text-[10px] font-medium leading-none truncate max-w-[100px]" 
                                  :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.4) }">
                              {{ event.organization?.name }}
                            </span>
                         </div>
                      </template>
                    </div>

                    <p :class="[
                      'text-sm font-medium',
                      (event.visibility === 'draft' || event.is_draft) ? 'italic' : ''
                    ]"
                    :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.3) }"
                    >
                      {{ event.title }}
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { formatLocalDate } from '../utils/dateUtils'
import { PlusIcon, CalendarIcon, CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon, ClockIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'
import { getOrgColor } from '../utils/colorUtils'

const viewType = ref('week') // 'month' or 'week'
const { user, initialize, setToken, isSuperAdmin } = useAuth()
const currentDate = ref(new Date())
const events = ref([])
const userMemberships = ref([])
const loading = ref(false)

const toggleView = () => {
  viewType.value = viewType.value === 'month' ? 'week' : 'month'
  if (viewType.value === 'week') {
    nextTick(scrollToToday)
  }
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
  if (viewType.value === 'week') {
    nextTick(scrollToToday)
  }
}

const weekScrollContainer = ref(null)

const scrollToToday = () => {
  if (!weekScrollContainer.value) return
  
  const todayIndex = weekDays.value.findIndex(day => day.isToday)
  if (todayIndex !== -1) {
    const container = weekScrollContainer.value
    const scrollWidth = container.scrollWidth
    const clientWidth = container.clientWidth
    
    // If not overflowing, no need to scroll
    if (scrollWidth <= clientWidth) return

    const colWidth = scrollWidth / 7
    // Center the element
    const scrollPos = (colWidth * todayIndex) - (clientWidth / 2) + (colWidth / 2)
    
    container.scrollTo({
      left: scrollPos,
      behavior: 'smooth'
    })
  }
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

const getEventTitle = (event) => {
  if (event.visibility === 'public_rejected') return `Refusé : ${event.title}`
  if (event.visibility === 'public_pending') return `En attente : ${event.title}`
  if (event.visibility === 'private') return `Privé : ${event.title}`
  if (event.visibility === 'draft' || event.is_draft) return `Brouillon : ${event.title}`
  return event.title
}

const loadEvents = async () => {
  loading.value = true
  try {
    let start_date, end_date
    
    // Calculate date range based on view
    if (viewType.value === 'month') {
        const year = currentDate.value.getFullYear()
        const month = currentDate.value.getMonth()
        // Include previous month's tail and next month's head
        // To be safe, let's grab from 1st of month - 7 days to last of month + 7 days
        // Or better: use logic matching monthDays computation
        const firstDay = new Date(year, month, 1)
        const lastDay = new Date(year, month + 1, 0)
        
        // Extend to cover full grid if needed, or just strict month + overlap
        // Simple safe margin: -7 days, +7 days from month boundaries
        const start = new Date(firstDay)
        start.setDate(start.getDate() - 7)
        const end = new Date(lastDay)
        end.setDate(end.getDate() + 7)
        
        start_date = start.toISOString()
        end_date = end.toISOString()
    } else {
        // Week view
        const weekStart = getWeekStart(currentDate.value)
        const weekEnd = new Date(weekStart)
        weekEnd.setDate(weekEnd.getDate() + 7) // +7 inclusive
        
        start_date = weekStart.toISOString()
        end_date = weekEnd.toISOString()
    }

    const response = await api.get('/events/', {
        params: {
            size: 512,
            start_date: start_date,
            end_date: end_date,
            upcoming: false // Disable default upcoming filter to see past events in current view
        }
    })
    events.value = response.data.items
    
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
watch([currentDate, viewType], () => {
  loadEvents()
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
  
  if (viewType.value === 'week') {
    nextTick(scrollToToday)
  }

  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

const handleKeydown = (e) => {
  // Ignore if user is typing in an input
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return
  
  if (e.key === 'ArrowLeft') {
    previousPeriod()
  } else if (e.key === 'ArrowRight') {
    nextPeriod()
  }
}
</script>

