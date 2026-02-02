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
            <template v-for="(event, index) in day.events.slice(0, 4)" :key="event.id + '_' + day.date">
              <!-- Spacer for continuation of multi-day event (invisible) -->
              <li 
                v-if="event.isPlaceholder" 
                class="invisible h-6"
                aria-hidden="true"
              ></li>

              <!-- Visible Event -->
              <li 
                v-else
                class="relative h-6"
                :class="{'z-10': event.isMultiDay}"
              >
                <router-link 
                  :to="`/events/${event.id}`" 
                  :title="getEventTitle(event)"
                  :class="[
                    'group flex items-center px-2 py-1 text-xs rounded transition-colors absolute top-0 left-0 h-full box-border',
                    ['public_rejected', 'public_pending', 'private'].includes(event.visibility) ? 'border-2' : '',
                    event.visibility === 'public_rejected' ? 'border-red-500 opacity-25' : '',
                    event.visibility === 'public_pending' ? 'border-yellow-500 opacity-50' : '',
                    event.visibility === 'private' ? 'border-blue-500' : '',
                    (event.visibility === 'draft' || event.is_draft) ? 'opacity-50' : '',
                    event.isMultiDay ? 'mx-[-8px] rounded-md shadow-sm' : 'w-full'
                  ]"
                  :style="{ 
                    backgroundColor: event.organization?.color_secondary || '#f3f4f6',
                    color: event.organization?.color_dark || '#1f2937',
                    width: event.visualSpan ? `calc((100% + 16px) * ${event.visualSpan} + (${event.visualSpan} - 1) * 1px)` : '100%',
                    borderTopRightRadius: event.isSegmentEnd ? '0.375rem' : '0',
                    borderBottomRightRadius: event.isSegmentEnd ? '0.375rem' : '0',
                    borderRightWidth: event.isSegmentEnd ? '' : '0',
                    borderTopLeftRadius: event.isSegmentStart ? '0.375rem' : '0',
                    borderBottomLeftRadius: event.isSegmentStart ? '0.375rem' : '0',
                    borderLeft: event.isSegmentStart ? `3px solid ${event.organization?.color_primary || '#4f46e5'}` : '0'
                  }"
                >
                  <div class="flex items-center gap-1.5 min-w-0">
                    <div class="flex -space-x-1.5 shrink-0" v-if="(event.guest_organizations && event.guest_organizations.length > 0) || event.organization?.logo_url">
                         <img 
                           v-if="event.organization?.logo_url"
                           :src="event.organization?.logo_url" 
                           class="h-4 w-4 rounded-full ring-1 ring-white object-cover bg-white"
                           :title="event.organization?.name"
                         />
                         <template
                           v-for="guest in event.guest_organizations" 
                           :key="guest.id"
                         >
                           <img  
                             v-if="guest.logo_url"
                             :src="guest.logo_url" 
                             class="h-4 w-4 rounded-full ring-1 ring-white object-cover bg-white"
                             :title="guest.name"
                           />
                         </template>
                    </div>
                    
                    <span :class="[
                      'flex-auto truncate font-medium',
                      (event.visibility === 'draft' || event.is_draft) ? 'italic' : ''
                    ]">
                      <span v-if="event.organization?.name" class="font-bold mr-1">{{ event.organization.name }}:</span>{{ event.title }}
                    </span>
                  </div>
                  <time 
                    v-if="!event.isMultiDay"
                    class="ml-2 hidden flex-none xl:block"
                    style="opacity: 0.8"
                  >
                    {{ formatTime(event.start_time) }}
                  </time>
                </router-link>
              </li>
            </template>
            <li v-if="day.events.length > 4" class="text-xs text-gray-500 px-2">
              +{{ day.events.length - 4 }} plus
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
                <template v-for="(event, index) in day.events" :key="event.id + '_' + day.date">
                  <!-- Case 1: Multi-day Event (Spanning Bar) -->
                  <template v-if="event.isMultiDay">
                     <!-- Placeholder -->
                     <li v-if="event.isPlaceholder" class="invisible h-8" aria-hidden="true"></li>
                     <!-- Visible Bar -->
                     <li v-else class="relative h-8" :class="{'z-10': true}">
                        <router-link 
                          :to="`/events/${event.id}`"
                          :title="getEventTitle(event)"
                          :class="[
                             'group flex items-center px-2 text-xs rounded-md shadow-sm transition-colors absolute top-0 left-0 h-full box-border mx-[-8px]',
                             ['public_rejected', 'public_pending', 'private'].includes(event.visibility) ? 'border-2' : '',
                          ]"
                          :style="{ 
                             backgroundColor: event.organization?.color_secondary || '#f3f4f6',
                             color: event.organization?.color_dark || '#1f2937',
                             width: event.visualSpan ? `calc((100% + 16px) * ${event.visualSpan} + (${event.visualSpan} - 1) * 1px)` : '100%',
                             borderTopRightRadius: event.isSegmentEnd ? '0.375rem' : '0',
                             borderBottomRightRadius: event.isSegmentEnd ? '0.375rem' : '0',
                             borderRightWidth: event.isSegmentEnd ? '' : '0',
                             borderTopLeftRadius: event.isSegmentStart ? '0.375rem' : '0',
                             borderBottomLeftRadius: event.isSegmentStart ? '0.375rem' : '0',
                             borderLeft: event.isSegmentStart ? `3px solid ${event.organization?.color_primary || '#4f46e5'}` : '0'
                          }"
                        >
                           <div class="flex items-center gap-1.5 min-w-0 w-full">
                               <div class="flex -space-x-1.5 shrink-0" v-if="(event.guest_organizations && event.guest_organizations.length > 0) || event.organization?.logo_url">
                                    <img 
                                      v-if="event.organization?.logo_url"
                                      :src="event.organization?.logo_url" 
                                      class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                                      :title="event.organization?.name"
                                    />
                                    <template
                                      v-for="guest in event.guest_organizations" 
                                      :key="guest.id"
                                    >
                                      <img  
                                        v-if="guest.logo_url"
                                        :src="guest.logo_url" 
                                        class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                                        :title="guest.name"
                                      />
                                    </template>
                               </div>
                               <span class="font-medium truncate mr-1">
                                   <span v-if="event.organization?.name" class="font-bold mr-1">{{ event.organization.name }}:</span>{{ event.title }}
                               </span>
                               <span class="opacity-75 truncate text-[10px] ml-auto shrink-0">{{ formatTime(event.start_time) }}</span>
                           </div>
                        </router-link>
                     </li>
                  </template>

                  <!-- Case 2: Single-day Event (Detailed Card) -->
                  <li v-else>
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
                        backgroundColor: event.organization?.color_secondary || '#f3f4f6',
                        borderLeft: `3px solid ${event.organization?.color_primary || '#4f46e5'}`
                      }"
                    >
                      <!-- Organization Badges -->
                      <div class="flex items-center gap-1 mb-1.5">
                        <template v-if="event.guest_organizations && event.guest_organizations.length > 0">
                           <div class="flex -space-x-1.5">
                              <img 
                                v-if="event.organization?.logo_url"
                                :src="event.organization?.logo_url" 
                                class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                                :title="event.organization?.name"
                              />
                              <template
                                v-for="guest in event.guest_organizations" 
                                :key="guest.id"
                              >
                                <img  
                                  v-if="guest.logo_url"
                                  :src="guest.logo_url" 
                                  class="h-5 w-5 rounded-full ring-1 ring-white object-cover bg-white"
                                  :title="guest.name"
                                />
                              </template>
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
                                    :style="{ color: event.organization?.color_primary || '#4f46e5' }">
                                {{ event.organization?.name }}
                              </span>
                           </div>
                        </template>
                      </div>

                      <p :class="[
                        'text-sm font-medium',
                        (event.visibility === 'draft' || event.is_draft) ? 'italic' : ''
                      ]"
                      :style="{ color: event.organization?.color_dark || '#1f2937' }"
                      >
                        {{ event.title }}
                      </p>
                      <div 
                        class="flex items-center text-xs mt-1" 
                        :style="{ color: event.organization?.color_dark || '#374151' }"
                      >
                        <ClockIcon class="h-3 w-3 mr-1" />
                        {{ formatTime(event.start_time) }}
                      </div>
                      <div 
                        v-if="event.location" 
                        class="flex items-center text-xs mt-1"
                        :style="{ color: event.organization?.color_dark || '#374151' }"
                      >
                        <MapPinIcon class="h-3 w-3 mr-1" />
                        {{ event.location }}
                      </div>
                    </router-link>
                  </li>
                </template>
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

const viewType = ref('week') // 'month' or 'week'
const { user, initialize, setToken, isSuperAdmin, isAuthenticated } = useAuth()
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
  if (!isAuthenticated.value) return false
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
  currentDate.value.setHours(0, 0, 0, 0)
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

const toLocalISOString = (date) => {
  const options = { year: 'numeric', month: '2-digit', day: '2-digit' }
  const formatted = new Intl.DateTimeFormat('fr-FR', options).format(date)
  return formatted
}

const createDayObject = (date, isCurrentMonth) => {
  const dateStr = toLocalISOString(date)
  const isToday = dateStr === toLocalISOString(new Date())
  
  return {
    date: dateStr,
    dayNumber: date.getDate(),
    isCurrentMonth,
    isToday,
    events: getEventsForDate(dateStr)
  }
}

const getEventsForDate = (dateStr) => {
  return processedEventsMap.value[dateStr] || []
}

const processedEventsMap = computed(() => {
  const map = {}
  
  // Sort events globally first: Long events, then Time, then Duration
  const sortedEvents = [...events.value].sort((a, b) => {
    const aLong = isLongEvent(a)
    const bLong = isLongEvent(b)
    if (aLong && !bLong) return -1
    if (!aLong && bLong) return 1
    
    const timeDiff = new Date(a.start_time) - new Date(b.start_time)
    if (timeDiff !== 0) return timeDiff
    
    return (new Date(b.end_time || b.start_time) - new Date(b.start_time)) - 
           (new Date(a.end_time || a.start_time) - new Date(a.start_time))
  })
  
  sortedEvents.forEach(originalEvent => {
    const startDate = new Date(originalEvent.start_time)
    const endDate = originalEvent.end_time ? new Date(originalEvent.end_time) : new Date(startDate)
    const isLong = isLongEvent(originalEvent)
    
    // Normalize dates to YYYY-MM-DD
    let current = new Date(startDate)
    current.setHours(0, 0, 0, 0)
    let endDay = new Date(endDate)
    // If end time is midnight (00:00), it counts as previous day for inclusive logic
    if (endDay.getHours() === 0 && endDay.getMinutes() === 0 && endDay > startDate) {
      endDay.setDate(endDay.getDate() - 1)
    }
    endDay.setHours(0, 0, 0, 0)
    
    if (!isLong) {
      // Single day behavior
      const dateStr = toLocalISOString(startDate)
      if (!map[dateStr]) map[dateStr] = []
      map[dateStr].push({ ...originalEvent, isMultiDay: false })
      return
    }

    // Multi-day behavior
    while (current <= endDay) {
      const dateStr = toLocalISOString(current)
      if (!map[dateStr]) map[dateStr] = []
      
      const dayOfWeek = current.getDay() // 0=Sun, 1=Mon
      const isMonday = dayOfWeek === 1
      const isStartDay = current.getTime() === new Date(startDate).setHours(0,0,0,0)
      
      // Determine if this is the start of a visual segment
      // Start of segment if: It is the event start date OR It is a Monday (start of row)
      const isSegmentStart = isStartDay || isMonday
      
      // Calculate remaining days in this week (Mon-Sun)
      // Mon(1)->7, Tue(2)->6, ..., Sun(0)->1
      const daysInWeek = 8 - (dayOfWeek || 7)
      
      // Calculate remaining days in the event
      // Difference in days + 1
      const msPerDay = 24 * 60 * 60 * 1000
      const daysLeftInEvent = Math.ceil((endDay - current) / msPerDay) + 1
      
      // Calculate visual span (capped by week end)
      const visualSpan = isSegmentStart ? Math.min(daysInWeek, daysLeftInEvent) : 0
      
      // Is this the very first part of the entire event?
      const isFirstSegment = isStartDay
      // Is this the very last part of the entire event?
      // It implies that the visual segment ends exactly when the event ends.
      // visualSpan days have passed.
      const isLastSegment = isSegmentStart && (visualSpan === daysLeftInEvent)

      map[dateStr].push({
        ...originalEvent,
        isMultiDay: true,
        isPlaceholder: !isSegmentStart,
        visualSpan: visualSpan,
        isSegmentStart: isFirstSegment, // For corner styling (true start)
        isSegmentEnd: isLastSegment // For corner styling (true end)
      })
      
      // Next day
      current.setDate(current.getDate() + 1)
    }
  })

  return map
})

const isLongEvent = (event) => {
  if (!event.end_time) return false
  const start = new Date(event.start_time)
  const end = new Date(event.end_time)
  return (end - start) > (24 * 60 * 60 * 1000)
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

watch([currentDate, viewType], () => {
  loadEvents()
})

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
            upcoming: false, // Disable default upcoming filter to see past events in current view
            limit: 1000 // Increase limit to ensure we get all events for the month
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

onMounted(async () => {
  // Set current date to start of day
  currentDate.value = new Date()
  currentDate.value.setUTCHours(0, 0, 0, 0)

  // Check for OIDC callback token in URL
  const urlParams = new URLSearchParams(window.location.search)
  const authToken = urlParams.get('token')
  
  if (authToken) {
    await setToken(authToken)
    // Clean up URL
    window.history.replaceState({}, document.title, '/')
  }
  
  // Only initialize auth if we have a token, to avoid 401 redirect on public dashboard
  if (authToken || localStorage.getItem('auth_token')) {
      await initialize()
      await loadUserMemberships()
  }
  
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

