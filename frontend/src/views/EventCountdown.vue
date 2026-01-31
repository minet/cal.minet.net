<template>
  <div v-if="loading" class="h-screen flex items-center justify-center bg-gray-50 text-gray-900">
    <p class="text-lg animate-pulse">Chargement...</p>
  </div>

  <div 
    v-else-if="event" 
    class="h-screen flex items-center justify-center overflow-hidden relative"
    :style="{ background: backgroundGradient }"
  >
    <!-- Background Bubbles -->
    <div class="absolute inset-0 z-0 overflow-hidden pointer-events-none">
      <div 
        v-for="(org, index) in [event.organization, ...(event.guest_organizations || [])].filter(Boolean)"
        :key="index"
        class="absolute rounded-full blur-3xl opacity-20"
        :class="index % 2 === 0 ? 'animate-float-slow' : 'animate-float-medium'"
        :style="{ 
          backgroundColor: org.color_secondary || bubbleColor, 
          width: index % 2 === 0 ? '40rem' : '30rem', 
          height: index % 2 === 0 ? '40rem' : '30rem', 
          top: index % 2 === 0 ? `${-10 + (index * 5)}%` : 'auto',
          bottom: index % 2 !== 0 ? `${10 + (index * 5)}%` : 'auto',
          left: index % 2 === 0 ? `${-10 + (index * 5)}%` : 'auto',
          right: index % 2 !== 0 ? `${-5 + (index * 5)}%` : 'auto',
          animationDelay: `${index * 1.5}s`
        }"
      ></div>
    </div>

    <div class="text-center px-4 max-w-5xl relative z-10 w-full flex flex-col h-full justify-center">
      
      <!-- Organization Pill -->
      <div v-if="event.organization" class="mb-4 flex justify-center flex-wrap gap-4">
        <div class="inline-flex items-center bg-white/80 backdrop-blur-md shadow-md rounded-full px-4 py-2 border border-white/20 transform transition-transform hover:scale-105">
            <img 
                v-if="event.organization.logo_url" 
                :src="event.organization.logo_url" 
                class="w-10 h-10 rounded-full mr-3 object-cover shadow-sm" 
                alt="Org Logo" 
            />
            <span class="text-xl font-bold tracking-tight text-gray-900">{{ event.organization.name }}</span>
        </div>

        <div v-for="guest in event.guest_organizations" :key="guest.id"
            class="inline-flex items-center bg-white/80 backdrop-blur-md shadow-md rounded-full px-4 py-2 border border-white/20 transform transition-transform hover:scale-105"
        >
            <img 
                v-if="guest.logo_url" 
                :src="guest.logo_url" 
                class="w-8 h-8 rounded-full mr-2 object-cover shadow-sm" 
                alt="Guest Logo" 
            />
            <span class="text-lg font-semibold tracking-tight text-gray-800">{{ guest.name }}</span>
        </div>
      </div>

      <!-- Event Title -->
      <h1 class="text-5xl md:text-7xl lg:text-8xl font-black text-gray-100 mb-8 drop-shadow-sm tracking-tight leading-tight">
        {{ event.title }}
      </h1>

      <!-- Poster (Optional) -->
      <div v-if="event.poster_url" class="mb-8">
        <img :src="event.poster_url" :alt="event.title" class="max-h-64 md:max-h-80 mx-auto rounded-3xl shadow-2xl ring-8 ring-white/30" />
      </div>

      <!-- Countdown -->
      <div class="mb-12">
        <CountdownTimer :targetDate="event.start_time" :textColor="'text-white'" />
      </div>

      <!-- Details -->
      <div class="flex flex-col md:flex-row items-center justify-center gap-6 text-gray-800 text-xl font-medium mb-8">
        <div v-if="event.location" class="flex items-center bg-white/60 backdrop-blur-md py-2 px-4 rounded-xl shadow-sm">
          <MapPinIcon class="h-6 w-6 mr-2 text-indigo-600" />
          {{ event.location }}
        </div>
        <div class="flex items-center bg-white/60 backdrop-blur-md py-2 px-4 rounded-xl shadow-sm">
          <CalendarIcon class="h-6 w-6 mr-2 text-indigo-600" />
          {{ formatDate(event.start_time) }}
        </div>
      </div>

      <!-- Reactions -->
      <div class="mb-8 flex justify-center">
         <div class="bg-white/60 backdrop-blur-md rounded-2xl p-4 shadow-lg inline-block">
             <ReactionList 
               v-if="event" 
               :event-id="event.id" 
               :reactions="event.reactions"
               :btn-add="true" 
               @update="refreshReactions" 
               @click.capture="checkAuth"
             />
         </div>
      </div>

      <!-- View Event Button -->
      <!-- <div class="mt-4">
        <router-link :to="`/events/${event.id}`" class="text-indigo-700 font-semibold hover:underline">
            Voir les détails de l'événement
        </router-link>
      </div> -->
    </div>
    </div>

    <!-- Login Modal -->
    <LoginModal 
      :isOpen="showLoginModal" 
      :description="loginDescription"
      cancelText="Pas maintenant"
      @close="handleModalClose"
    />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../utils/api'
import { useAuth } from '../composables/useAuth'
import CountdownTimer from '../components/CountdownTimer.vue'
import ReactionList from '../components/ReactionList.vue'
import { MapPinIcon, CalendarIcon } from '@heroicons/vue/24/outline'
import LoginModal from '../components/LoginModal.vue'
import { getEventGradient } from '../utils/colorUtils'

const showLoginModal = ref(false)
const loginDescription = ref("Connectez-vous pour réagir, ajouter cet événement à votre calendrier et profiter de toutes les fonctionnalités !")

const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()
const event = ref(null)
const loading = ref(true)

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

const backgroundGradient = computed(() => {
    if (!event.value) return '#f3f4f6'
    return getEventGradient(event.value.organization, event.value.guest_organizations)
})

const bubbleColor = computed(() => {
    if (!event.value?.organization) return '#e5e7eb'
    return event.value.organization.color_secondary || '#e5e7eb' 
})

const loadEvent = async () => {
  try {
    const response = await api.get(`/events/${route.params.id}`)
    event.value = response.data
  } catch (error) {
    console.error('Failed to load event:', error)
    if (error.response && error.response.status === 403) {
        loginDescription.value = "Cet événement est privé ou vous n'avez pas la permission de le voir. Veuillez vous connecter."
        showLoginModal.value = true
    }
  } finally {
    loading.value = false
  }
}

const handleModalClose = () => {
    showLoginModal.value = false
    // If we have no event (e.g. private event load failed), redirect to home
    if (!event.value) {
        router.push('/')
    }
}

const refreshReactions = async () => {
   // Just reload the event to get updated reactions
   const response = await api.get(`/events/${route.params.id}`)
   event.value.reactions = response.data.reactions
}

const checkAuth = (e) => {
    // This is a capture phase listener. 
    // If user interacts with reaction list (specifically adding), we want to redirect if not logged in.
    // However, ReactionList handles the click internally.
    // We can intercept: if not authenticated, prevent default and redirect.
    // But 'click.capture' on the container will catch ANY click inside.
    
    // Simplest approach: if any click happens inside the reaction block and user is not auth, redirect.
    // Reactions are interactive, so clicking them means intent to react or unreact.
    if (!isAuthenticated.value) {
        e.preventDefault()
        e.stopPropagation()
        loginDescription.value = "Connectez-vous pour réagir, ajouter cet événement à votre calendrier et profiter de toutes les fonctionnalités !"
        showLoginModal.value = true
    }
}

onMounted(() => {
  loadEvent()
})
</script>

<style scoped>
/* Float animations from WallDisplay */
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
</style>
