<template>
  <div v-if="loading" class="h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-700">
    <p class="text-white text-lg">Chargement...</p>
  </div>

  <div v-else-if="event" class="h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-700 overflow-hidden">
    <div class="text-center px-8 max-w-4xl">
      <!-- Event Title -->
      <h1 class="text-6xl md:text-8xl font-bold text-white mb-8 drop-shadow-lg">
        {{ event.title }}
      </h1>

      <!-- Poster -->
      <div v-if="event.poster_url" class="mb-8">
        <img :src="event.poster_url" :alt="event.title" class="max-h-64 mx-auto rounded-lg shadow-2xl" />
      </div>

      <!-- Countdown -->
      <div class="mb-12">
        <CountdownTimer :targetDate="event.start_time" />
      </div>

      <!-- Organization -->
      <div v-if="event.organization" class="mb-8">
        <p class="text-2xl text-white/90">
          Organisé par <span class="font-semibold">{{ event.organization.name }}</span>
        </p>
      </div>

      <!-- Location & Date -->
      <div class="flex flex-col md:flex-row items-center justify-center gap-6 text-white/80 text-lg mb-8">
        <div v-if="event.location" class="flex items-center">
          <MapPinIcon class="h-6 w-6 mr-2" />
          {{ event.location }}
        </div>
        <div class="flex items-center">
          <CalendarIcon class="h-6 w-6 mr-2" />
          {{ formatDate(event.start_time) }}
        </div>
      </div>

      <!-- Description (Collapsible) -->
      <div v-if="event.description" class="mt-8">
        <button 
          @click="showDescription = !showDescription"
          class="text-white/90 hover:text-white text-sm font-medium mb-4 flex items-center mx-auto"
        >
          <ChevronDownIcon :class="['h-5 w-5 mr-1 transition-transform', showDescription ? 'rotate-180' : '']" />
          {{ showDescription ? 'Masquer' : 'Voir' }} la description
        </button>
        
        <transition name="fade">
          <div v-if="showDescription" class="bg-white/10 backdrop-blur-lg rounded-lg p-6 text-white/90 max-w-2xl mx-auto">
            <p class="whitespace-pre-wrap text-left">{{ event.description }}</p>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import CountdownTimer from '../components/CountdownTimer.vue'
import { MapPinIcon, CalendarIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const event = ref(null)
const loading = ref(true)
const showDescription = ref(false)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadEvent = async () => {
  try {
    const response = await api.get(`/events/${route.params.id}`)
    event.value = response.data
  } catch (error) {
    console.error('Failed to load event:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadEvent()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
