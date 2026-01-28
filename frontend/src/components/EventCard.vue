<template>
  <div 
    class="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 h-full flex flex-col"
    :class="{
      'border-2': ['public_rejected', 'public_pending', 'private'].includes(event.visibility),
      'border-red-500 opacity-25': event.visibility === 'public_rejected',
      'border-yellow-500 opacity-50': event.visibility === 'public_pending',
      'border-blue-500': event.visibility === 'private',
      'opacity-50': event.visibility === 'draft'
    }"
  >
    <!-- Poster Image (Optional) -->
    <div v-if="event.poster_url" class="relative sm:h-96 w-full overflow-hidden rounded-t-xl">
      <img 
        :src="event.poster_url" 
        :alt="event.title" 
        class="w-full h-full object-cover transform hover:scale-105 transition-transform duration-500"
      />
      <!-- Organization Logo Overlay -->
      <div class="absolute bottom-3 right-3 flex items-center space-x-2 overflow-hidden p-1 bg-white/90 rounded-full shadow-md backdrop-blur-sm">
        <template v-for="guest in event.guest_organizations" :key="guest.id">
            <img 
                v-if="guest.logo_url"
                :src="guest.logo_url" 
                :alt="guest.name"
                class="inline-block h-10 w-10 rounded-full ring-2 ring-white object-cover"
                :title="guest.name"
            />
            <div 
                v-else
                class="inline-block h-10 w-10 rounded-full ring-2 ring-white flex items-center justify-center font-bold"
                :style="{ backgroundColor: getOrgColor(guest.color_chroma, guest.color_hue, 0.95), color: getOrgColor(guest.color_chroma, guest.color_hue, 0.4) }"
                :title="guest.name"
            >
                {{ guest.name.charAt(0) }}
            </div>
        </template>
        
        <img 
          v-if="event.organization?.logo_url"
          :src="event.organization.logo_url" 
          :alt="event.organization.name" 
          class="inline-block h-10 w-10 rounded-full ring-2 ring-white object-cover z-10"
          :title="event.organization.name"
        />
        <div 
          v-else-if="event.organization"
          class="inline-block h-10 w-10 rounded-full ring-2 ring-white z-10 flex items-center justify-center font-bold"
          :style="{ backgroundColor: getOrgColor(event.organization.color_chroma, event.organization.color_hue, 0.95), color: getOrgColor(event.organization.color_chroma, event.organization.color_hue, 0.4) }"
          :title="event.organization.name"
        >
          {{ event.organization.name.charAt(0) }}
        </div>
      </div>
    </div>
    
    <!-- No Poster Fallback - Just Org Logo -->
    <div 
      v-else 
      class="relative h-24 flex items-center justify-center p-4 transition-colors rounded-t-xl"
      :style="{ background: getEventGradient(event.organization, event.guest_organizations, 2, 1) }"
    >
      <div class="absolute -bottom-6 left-6 flex items-center -space-x-2">
        <img 
          v-if="event.organization?.logo_url"
          :src="event.organization.logo_url" 
          :alt="event.organization.name" 
          class="h-12 w-12 rounded-full border-4 border-white object-cover z-20 bg-white"
        />
        <div 
          v-else-if="event.organization"
          class="h-12 w-12 rounded-full border-4 border-white z-20 bg-white flex items-center justify-center font-bold"
          :style="{ color: getOrgColor(event.organization.color_chroma, event.organization.color_hue, 0.4) }"
        >
          {{ event.organization.name.charAt(0) }}
        </div>

        <template v-for="guest in event.guest_organizations" :key="guest.id">
            <img 
                v-if="guest.logo_url"
                :src="guest.logo_url" 
                :alt="guest.name"
                class="h-12 w-12 rounded-full border-4 border-white object-cover bg-white"
                :title="guest.name"
            />
            <div 
                v-else
                class="h-12 w-12 rounded-full border-4 border-white bg-white flex items-center justify-center text-xs font-bold"
                :style="{ color: getOrgColor(guest.color_chroma, guest.color_hue, 0.4) }"
                :title="guest.name"
            >
                {{ guest.name.charAt(0) }}
            </div>
        </template>
      </div>
    </div>

    <div class="p-5 flex-1 flex flex-col pt-8">
      <!-- Date and Time -->
      <div class="flex items-center text-sm text-indigo-600 font-semibold mb-2">
        <span class="uppercase tracking-wide">{{ formattedDate }}</span>
        <span class="mx-2">•</span>
        <span>{{ formattedTime }}</span>
      </div>

      <!-- Title -->
      <h3 class="text-xl font-bold text-gray-900 mb-2 line-clamp-2">{{ event.title }}</h3>

      <ReactionList 
        v-if="event"
        :event-id="event.id" 
        :reactions="event.reactions"
        :btn-add="false"
        @update="refreshReactions"
        class="mb-3"
      />

      <!-- Location -->
      <div class="flex items-center text-gray-500 text-sm mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="truncate">{{ event.location || 'Lieu non spécifié' }}</span>
      </div>

      <!-- Description (First line) -->
      <p class="text-gray-600 text-sm mb-4 line-clamp-2 flex-1">
        {{ firstLineDescription }}
      </p>

      <!-- Footer/Action -->
      <div class="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center">
        <span 
          class="max-w-[150px] truncate inline-block align-middle text-xs font-medium px-2 py-1 rounded-full border transition-colors"
          :class="{ 'bg-gray-100 text-gray-500 border-gray-100': event.organization?.color_chroma === null }"
          :style="{ 
            backgroundColor: getOrgColor(event.organization?.color_chroma/20, event.organization?.color_hue, 1),
            color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.4),
            borderColor: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.9)
          }"
        >
          {{ event.organization?.name || 'Organisation' }}
          <span v-if="event.guest_organizations?.length" class="ml-1 opacity-75 text-[10px]">
            +{{ event.guest_organizations.length }}
          </span>
        </span>
        <router-link :to="`/events/${event.id}`" class="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center group">
          Voir détails
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatLocalDate } from '../utils/dateUtils'

import ReactionList from './ReactionList.vue'
import api from '../utils/api'
import { getOrgColor, getEventGradient } from '../utils/colorUtils'

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

const refreshReactions = async () => {
  try {
    const response = await api.get(`/events/${props.event.id}`)
    props.event.reactions = response.data.reactions
  } catch (error) {
    console.error('Failed to refresh reactions', error)
  }
}

const formattedDate = computed(() => {
  if (!props.event.start_time) return ''
  return formatLocalDate(props.event.start_time, { 
    weekday: 'short', 
    day: 'numeric', 
    month: 'short' 
  })
})

const formattedTime = computed(() => {
  if (!props.event.start_time) return ''
  return formatLocalDate(props.event.start_time, { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

const firstLineDescription = computed(() => {
  if (!props.event.description) return ''
  // Split by newline and take the first non-empty line
  const lines = props.event.description.split('\n').filter(line => line.trim() !== '')
  return lines.length > 0 ? lines[0] : ''
})
</script>
