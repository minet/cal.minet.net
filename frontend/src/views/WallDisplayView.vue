<template>
  <div v-if="loading" class="flex items-center justify-center h-screen bg-gray-50 text-gray-900">
    <div class="text-2xl">Chargement des événements...</div>
  </div>

  <div v-else-if="events.length === 0" class="flex items-center justify-center h-screen bg-gray-50 text-gray-900">
    <div class="text-3xl font-bold">Aucun événement à venir dans les 3 prochains jours</div>
  </div>

  <div 
    v-else
    class="fixed inset-0 z-50 flex overflow-hidden transition-colors duration-1000 ease-in-out"
    :style="{ background: currentEventBg }"
  >
    <!-- Progress Bar -->
    <div class="absolute top-0 left-0 h-2 bg-gray-900/10 z-50" :style="{ width: `${progress}%`, transition: 'width 0.1s linear' }"></div>

    <!-- Bubbles container -->
    <div class="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div 
            class="absolute rounded-full blur-3xl opacity-40 animate-float-slow" 
            :style="{ backgroundColor: currentEventBubbleColor, width: '40rem', height: '40rem', top: '-10%', left: '-10%' }"
        ></div>
        <div 
            class="absolute rounded-full blur-3xl opacity-30 animate-float-medium" 
            :style="{ backgroundColor: currentEventBubbleColor, width: '30rem', height: '30rem', bottom: '10%', right: '-5%', animationDelay: '1s' }"
        ></div>
        <div 
            class="absolute rounded-full blur-3xl opacity-20 animate-float-fast" 
            :style="{ backgroundColor: currentEventBubbleColor, width: '20rem', height: '20rem', top: '40%', left: '40%', animationDelay: '2s' }"
        ></div>
    </div>

    <transition name="slide" mode="out-in">
      <div v-if="isAdSlide" key="ad-slide" class="flex flex-col lg:flex-row w-full h-full relative z-10 items-center justify-center">
         <div class="flex flex-col items-center justify-center p-12 text-center max-w-5xl mx-auto">
             <h1 class="text-7xl lg:text-9xl font-black mb-12 text-gray-900 tracking-tight">Calend'INT</h1>
             <p class="text-4xl lg:text-5xl font-medium text-gray-700 mb-16 leading-normal">
                 Retrouvez tous les événements et ajoutez les vôtres sur
                 <span class="text-indigo-600 font-bold block mt-4">cal.minet.net</span>
             </p>
             <div class="bg-white p-8 rounded-3xl shadow-2xl ring-8 ring-indigo-50 h-100 w-100">
                 <QRCodeVue3
                  value="https://cal.minet.net/"
                  :width="512" :height="512"
                  :qrOptions="{ errorCorrectionLevel: 'H' }"
                  :dots-options="{ type: 'square' }"
                  :corners-dot-options="{type: 'square'}"
                  :corners-square-options="{type: 'square'}"
                  image='/favicon.svg'
                  :image-options="{
                    excavate: false
                  }"
                  />
             </div>
         </div>
      </div>

      <div v-else-if="eventSlide" :key="eventSlide.id" class="flex flex-col lg:flex-row w-full h-full relative z-10">
        
        <!-- Poster Side (Left) -->
        <div class="w-full lg:w-1/2 h-1/2 lg:h-full flex items-center justify-center p-8 lg:p-12 relative">
           <img
             v-if="eventSlide.poster_file || eventSlide.poster_url || eventSlide.video_file || eventSlide.video_url"
             :src="resolveMediaUrl(eventSlide.poster_file, 960) ?? eventSlide.poster_url ?? undefined"
             class="max-w-full max-h-full w-auto h-auto object-contain shadow-2xl rounded-3xl ring-4 ring-white/50"
             alt="Event Poster"
           >
           <div v-else class="w-full h-full flex items-center justify-center bg-white/30 rounded-3xl backdrop-blur-sm border-4 border-white/50">
              <span class="text-gray-500 text-2xl font-medium">Pas d'affiche</span>
           </div>
        </div>

        <!-- Info Side (Right) -->
        <div class="w-full lg:w-1/2 h-1/2 lg:h-full flex flex-col justify-start p-8 lg:p-16 pt-8 lg:pt-24 text-gray-900 overflow-hidden">
          
          <!-- Organization Pill -->
           <!-- Organization Pill -->
          <div class="mb-8 flex flex-wrap gap-4 items-center">
             <div class="inline-flex items-center bg-white shadow-xl rounded-full px-6 py-3 border border-gray-100 transform transition-transform duration-500 hover:scale-105">
                <img
                  v-if="eventSlide.organization?.logo_file || eventSlide.organization?.logo_url"
                  :src="resolveMediaUrl(eventSlide.organization?.logo_file, 64) ?? eventSlide.organization?.logo_url ?? undefined"
                  class="w-12 h-12 rounded-full mr-2 object-cover"
                  alt="Org Logo"
                />
                <span class="text-2xl font-bold tracking-wide text-gray-900">{{ eventSlide.organization?.name }}</span>
             </div>

             <div v-for="guest in eventSlide.guest_organizations" :key="guest.id"
                  class="inline-flex items-center bg-white/90 shadow-lg rounded-full px-4 py-2 border border-gray-100/50 transform transition-transform duration-500 hover:scale-105"
             >
                <img
                  v-if="guest.logo_file || guest.logo_url"
                  :src="resolveMediaUrl(guest.logo_file, 64) ?? guest.logo_url ?? undefined"
                  class="w-8 h-8 rounded-full mr-2 object-cover"
                  alt="Guest Logo"
                />
                <span class="text-lg font-bold tracking-wide text-gray-700">{{ guest.name }}</span>
             </div>
          </div>

          <!-- Title -->
          <h1 class="text-6xl lg:text-8xl font-black mb-8 leading-tight tracking-tight font-display text-gray-900 drop-shadow-sm">
            {{ eventSlide.title }}
          </h1>

          <!-- Details Grid -->
          <div class="grid grid-cols-1 gap-8 text-2xl lg:text-3xl font-medium text-gray-800">
            
            <!-- Date/Time -->
            <div class="flex items-center space-x-6 bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-sm">
                 <ClockIcon class="w-10 h-10" />
              <div>
                <div class="font-bold text-gray-900">{{ formatEventDate(eventSlide.start_time) }}</div>
                <div class="text-gray-600 text-xl mt-1">{{ formatEventTime(eventSlide.start_time) }} - {{ formatEventTime(eventSlide.end_time) }}</div>
              </div>
            </div>

            <!-- Location -->
            <div class="flex items-center space-x-6 bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-sm">
                 <MapPinIcon class="w-10 h-10" />
                <div class="font-bold text-gray-900">{{ eventSlide.location || 'Lieu non spécifié' }}</div>
            </div>

          </div>

          <!-- Reactions -->
          <div v-if="displayedReactions.length > 0" class="mt-6 flex flex-wrap gap-2">
            <div 
                v-for="reaction in displayedReactions" 
                :key="reaction.emoji"
                class="flex items-center space-x-2 bg-white/60 backdrop-blur-md rounded-full px-3 py-1.5 border border-white/40 shadow-sm text-lg font-medium text-gray-800"
            >
                <span>{{ reaction.emoji }}</span>
                <span>{{ reaction.count }}</span>
            </div>
            <div v-if="hiddenReactionsCount > 0" class="flex items-center bg-white/40 backdrop-blur-md rounded-full px-3 py-1.5 border border-white/30 text-gray-700 font-medium">
                +{{ hiddenReactionsCount }}
            </div>
          </div>

           <!-- Description (Truncated if too long) -->
          <div class="mt-6 text-xl lg:text-2xl text-gray-600 line-clamp-6 max-w-2xl leading-relaxed">
            {{ eventSlide.description }}
          </div>

        </div>
      
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { api } from '@/api'
import type { EventRead } from '@/api/types'
import { getEventGradient } from '../utils/colorUtils'
import { formatLocalDate } from '../utils/dateUtils'
import { ClockIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import QRCodeVue3 from 'qrcode-vue3'
import { resolveMediaUrl } from '../utils/media.js'

const loading = ref(true)
const events = ref<EventRead[]>([])
const currentIndex = ref(0)
const progress = ref(0)
let slideTimer: ReturnType<typeof setTimeout> | undefined
let progressTimer: ReturnType<typeof setInterval> | undefined
let refreshTimer: ReturnType<typeof setInterval> | undefined

const DURATION_MS = 10000 // 10 seconds
const UPDATE_INTERVAL_MS = 100

const REFRESH_INTERVAL_MS = 15 * 60 * 1000 // 15 minutes

type WallSlide = EventRead | { isAd: true }

const currentEvent = computed<WallSlide | null>(() => {
  if (events.value.length === 0) return null
  // If index is equal to length, it's the ad slide
  if (currentIndex.value === events.value.length) {
    return { isAd: true }
  }
  return events.value[currentIndex.value]
})

const isAdSlide = computed(() => currentEvent.value !== null && 'isAd' in currentEvent.value)
const eventSlide = computed<EventRead | null>(() => {
  if (!currentEvent.value || 'isAd' in currentEvent.value) return null
  return currentEvent.value
})

const currentEventBg = computed(() => {
  if (isAdSlide.value) return '#ffffff' // White background for ad
  if (!eventSlide.value?.organization) return '#f3f4f6' // gray-100 default
  // Use gradient
  return getEventGradient(eventSlide.value.organization, eventSlide.value.guest_organizations)
})

const displayedReactions = computed(() => {
  if (!eventSlide.value?.reactions) return []
  // Sort by count desc
  const sorted = [...eventSlide.value.reactions].sort((a, b) => b.count - a.count)
  // Take top 5
  return sorted.slice(0, 5)
})

const hiddenReactionsCount = computed(() => {
  if (!eventSlide.value?.reactions) return 0
  return Math.max(0, eventSlide.value.reactions.length - 5)
})

const currentEventBubbleColor = computed(() => {
  if (isAdSlide.value) return '#e0e7ff' // Light indigo for ad bubbles
  if (!eventSlide.value?.organization) return '#e5e7eb'
  // Use a normal/vibrant shade for bubbles
  return eventSlide.value.organization.color_secondary || '#e5e7eb'
})

const fetchEvents = async () => {
  try {
    const response = await api.events.list_events({ size: 100, upcoming: true })
    const now = new Date()
    const threeDaysLater = new Date(now)
    threeDaysLater.setDate(now.getDate() + 3)

    events.value = response.items.filter((event) => {
      const startTime = new Date(event.start_time)
      const endTime = new Date(event.end_time)
      
      const isUpcoming = startTime > now || (startTime <= now && endTime >= now) // Standard upcoming check logic or rely solely on start/end
      // Feed "upcoming=true" usually returns future events. 
      // We want to keep the 3 day window strict for *normal* events, but relax for featured.
      const isInWindow = startTime <= threeDaysLater || event.is_featured
      const isNotOver = endTime > now
      
      return isInWindow && isNotOver
    }).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    
    // If current index is out of bounds after refresh, reset it
    if (currentIndex.value > events.value.length) {
        currentIndex.value = 0
    }

  } catch (error) {
    console.error("Failed to fetch events", error)
  } finally {
    loading.value = false
    // Only start slideshow if not already running (or restart it if needed)
    if (!slideTimer) {
        startSlideshow()
    }
  }
}

const startSlideshow = () => {
    if (events.value.length === 0) return

    if (slideTimer) clearTimeout(slideTimer)
    if (progressTimer) clearInterval(progressTimer)

    progress.value = 0
    let elapsed = 0
    
    // Determine duration for CURRENT slide
    // If currentEvent is Ad (isAd=true) or not featured, use standard duration.
    // If featured, use double.
    const getDuration = () => {
      if (isAdSlide.value) return DURATION_MS
      return eventSlide.value?.is_featured ? DURATION_MS * 2 : DURATION_MS
    }

    let currentDuration = getDuration()

    progressTimer = setInterval(() => {
        elapsed += UPDATE_INTERVAL_MS
        progress.value = Math.min((elapsed / currentDuration) * 100, 100)
    }, UPDATE_INTERVAL_MS)

    slideTimer = setTimeout(() => {
        nextSlide()
        // Recursively restart slideshow for next slide to handle varying durations
        startSlideshow()
    }, currentDuration)
}

const nextSlide = () => {
    if (events.value.length === 0) return
    // Cycle through events + 1 for the ad
    currentIndex.value = (currentIndex.value + 1) % (events.value.length + 1)
}

const formatEventDate = (dateStr: string) => {
    return formatLocalDate(dateStr, { weekday: 'long', day: 'numeric', month: 'long' })
}

const formatEventTime = (dateStr: string) => {
    return formatLocalDate(dateStr, { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    fetchEvents()
    refreshTimer = setInterval(fetchEvents, REFRESH_INTERVAL_MS)
})

onUnmounted(() => {
  if (slideTimer) clearTimeout(slideTimer) // Changed from clearInterval
  if (progressTimer) clearInterval(progressTimer)
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.font-display {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Slide animation to mimic scrolling */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* Float animations */
@keyframes float {
  0% { transform: translate(0, 0) scale(1) rotate(0deg); }
  33% { transform: translate(100px, -150px) scale(1.15) rotate(12deg); }
  66% { transform: translate(-80px, 60px) scale(0.85) rotate(-8deg); }
  100% { transform: translate(0, 0) scale(1) rotate(0deg); }
}

.animate-float-slow {
  animation: float 25s infinite ease-in-out;
}

.animate-float-medium {
  animation: float 18s infinite ease-in-out;
}

.animate-float-fast {
  animation: float 12s infinite ease-in-out;
}
</style>
