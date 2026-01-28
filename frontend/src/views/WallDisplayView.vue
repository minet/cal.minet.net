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
      <div v-if="currentEvent.isAd" key="ad-slide" class="flex flex-col lg:flex-row w-full h-full relative z-10 items-center justify-center">
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

      <div v-else :key="currentEvent.id" class="flex flex-col lg:flex-row w-full h-full relative z-10">
        
        <!-- Poster Side (Left) -->
        <div class="w-full lg:w-1/2 h-1/2 lg:h-full flex items-center justify-center p-8 lg:p-12 relative">
           <img 
             v-if="currentEvent.poster_url"
             :src="currentEvent.poster_url" 
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
                  v-if="currentEvent.organization?.logo_url" 
                  :src="currentEvent.organization.logo_url" 
                  class="w-12 h-12 rounded-full mr-2 object-cover" 
                  alt="Org Logo" 
                />
                <span class="text-2xl font-bold tracking-wide text-gray-900">{{ currentEvent.organization?.name }}</span>
             </div>

             <div v-for="guest in currentEvent.guest_organizations" :key="guest.id"
                  class="inline-flex items-center bg-white/90 shadow-lg rounded-full px-4 py-2 border border-gray-100/50 transform transition-transform duration-500 hover:scale-105"
             >
                <img 
                  v-if="guest.logo_url" 
                  :src="guest.logo_url" 
                  class="w-8 h-8 rounded-full mr-2 object-cover" 
                  alt="Guest Logo" 
                />
                <span class="text-lg font-bold tracking-wide text-gray-700">{{ guest.name }}</span>
             </div>
          </div>

          <!-- Title -->
          <h1 class="text-6xl lg:text-8xl font-black mb-8 leading-tight tracking-tight font-display text-gray-900 drop-shadow-sm">
            {{ currentEvent.title }}
          </h1>

          <!-- Details Grid -->
          <div class="grid grid-cols-1 gap-8 text-2xl lg:text-3xl font-medium text-gray-800">
            
            <!-- Date/Time -->
            <div class="flex items-center space-x-6 bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-sm">
                 <ClockIcon class="w-10 h-10" />
              <div>
                <div class="font-bold text-gray-900">{{ formatEventDate(currentEvent.start_time) }}</div>
                <div class="text-gray-600 text-xl mt-1">{{ formatEventTime(currentEvent.start_time) }} - {{ formatEventTime(currentEvent.end_time) }}</div>
              </div>
            </div>

            <!-- Location -->
            <div class="flex items-center space-x-6 bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-sm">
                 <MapPinIcon class="w-10 h-10" />
                <div class="font-bold text-gray-900">{{ currentEvent.location || 'Lieu non spécifié' }}</div>
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
            {{ currentEvent.description }}
          </div>

        </div>
      
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../utils/api'
import { getOrgColor, getEventGradient } from '../utils/colorUtils'
import { formatLocalDate } from '../utils/dateUtils'
import { ClockIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import QRCodeVue3 from 'qrcode-vue3'

const loading = ref(true)
const events = ref([])
const currentIndex = ref(0)
const progress = ref(0)
let slideTimer = null
let progressTimer = null
let refreshTimer = null

const DURATION_MS = 10000 // 10 seconds
const UPDATE_INTERVAL_MS = 100

const REFRESH_INTERVAL_MS = 15 * 60 * 1000 // 15 minutes

const currentEvent = computed(() => {
  return { isAd: true }
  if (events.value.length === 0) return {}
  // If index is equal to length, it's the ad slide
  if (currentIndex.value === events.value.length) {
  }
  return events.value[currentIndex.value]
})

const currentEventBg = computed(() => {
  if (currentEvent.value.isAd) return '#ffffff' // White background for ad
  if (!currentEvent.value?.organization) return '#f3f4f6' // gray-100 default
  // Use gradient
  return getEventGradient(currentEvent.value.organization, currentEvent.value.guest_organizations)
})

const displayedReactions = computed(() => {
  if (!currentEvent.value.reactions) return []
  // Sort by count desc
  const sorted = [...currentEvent.value.reactions].sort((a, b) => b.count - a.count)
  // Take top 5
  return sorted.slice(0, 5)
})

const hiddenReactionsCount = computed(() => {
  if (!currentEvent.value.reactions) return 0
  return Math.max(0, currentEvent.value.reactions.length - 5)
})

const currentEventBubbleColor = computed(() => {
  if (currentEvent.value.isAd) return '#e0e7ff' // Light indigo for ad bubbles
  if (!currentEvent.value?.organization) return '#e5e7eb'
  // Use a normal/vibrant shade for bubbles
  return getOrgColor(
      currentEvent.value.organization.color_chroma, 
      currentEvent.value.organization.color_hue, 
      0.65
  )
})

const fetchEvents = async () => {
  try {
    const response = await api.get('/events/', { 
        params: { 
            size: 100,
            upcoming: true
        } 
    })
    const now = new Date()
    const threeDaysLater = new Date(now)
    threeDaysLater.setDate(now.getDate() + 3)

    events.value = response.data.items.filter(event => {
      const startTime = new Date(event.start_time)
      const endTime = new Date(event.end_time)
      
      const isPublic = event.visibility === 'public_approved'
      const isUpcoming = startTime <= threeDaysLater || event.is_featured
      const isNotOver = endTime > now
      
      return isPublic && isUpcoming && isNotOver
    }).sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
    
    // If current index is out of bounds after refresh, reset it
    // Note: bounds is now length + 1 (for ad)
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

    clearInterval(slideTimer)
    clearInterval(progressTimer)

    progress.value = 0
    let elapsed = 0

    progressTimer = setInterval(() => {
        elapsed += UPDATE_INTERVAL_MS
        progress.value = (elapsed / DURATION_MS) * 100
    }, UPDATE_INTERVAL_MS)

    slideTimer = setInterval(() => {
        nextSlide()
        elapsed = 0
        progress.value = 0
    }, DURATION_MS)
}

const nextSlide = () => {
    if (events.value.length === 0) return
    // Cycle through events + 1 for the ad
    currentIndex.value = (currentIndex.value + 1) % (events.value.length + 1)
}

const formatEventDate = (dateStr) => {
    return formatLocalDate(dateStr, { weekday: 'long', day: 'numeric', month: 'long' })
}

const formatEventTime = (dateStr) => {
    return formatLocalDate(dateStr, { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    fetchEvents()
    refreshTimer = setInterval(fetchEvents, REFRESH_INTERVAL_MS)
})

onUnmounted(() => {
    clearInterval(slideTimer)
    clearInterval(progressTimer)
    clearInterval(refreshTimer)
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
