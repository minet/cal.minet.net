<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-sm text-gray-500">Chargement...</p>
  </div>

  <div v-else-if="event">
    <!-- Header -->
    <header 
      class="shadow-sm rounded-lg mb-6 transition-colors"
      :style="{ 
        background: getEventGradient(event.organization, event.guest_organizations, 20, 1),
        borderTop: `4px solid ${getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.6)}`
      }"
    >
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ event.title }}</h1>
            <ReactionList 
              v-if="event" 
              :event-id="event.id" 
              :reactions="event.reactions"
              :btn-add="canEdit"
              @update="loadEvent" 
              class="mb-2"
            />
            <div class="mt-1 flex items-center text-xs text-gray-500 mb-2">
              <InformationCircleIcon class="h-3 w-3 mr-1" />
              Interagir ajoute l'événement à votre calendrier
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 sm:gap-3">
              <!-- Visibility Badge -->
              <span v-if="event.visibility === 'draft'" class="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                <DocumentTextIcon class="mr-1.5 h-4 w-4" />
                Brouillon
              </span>
              <span v-else-if="event.visibility === 'private'" class="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-600/20">
                <LockClosedIcon class="mr-1.5 h-4 w-4" />
                Privé
              </span>
              <span v-else-if="event.visibility === 'public_pending'" class="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
                <ClockIcon class="mr-1.5 h-4 w-4" />
                En attente d'approbation
              </span>
               <span v-else-if="event.visibility === 'public_rejected'" class="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20">
                <XMarkIcon class="mr-1.5 h-4 w-4" />
                Refusé
              </span>
              <span v-else class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                <GlobeAltIcon class="mr-1.5 h-4 w-4" />
                Public
              </span>
              <router-link 
                v-if="event.organization"
                :to="`/organizations/${event.organization.id}`"
                class="text-sm font-medium hover:underline transition-colors"
                :style="{ color: getOrgColor(event.organization?.color_chroma, event.organization?.color_hue, 0.4) }"
              >
                {{ event.organization.name }}
              </router-link>
              <template v-if="event.guest_organizations && event.guest_organizations.length">
                  <span class="text-gray-400 mx-2 text-sm">×</span>
                  <div class="flex flex-wrap gap-1 items-center">
                    <router-link 
                        v-for="(guest, idx) in event.guest_organizations" 
                        :key="guest.id"
                        :to="`/organizations/${guest.id}`"
                        class="text-sm font-medium hover:underline transition-colors block"
                        :style="{ color: getOrgColor(guest.color_chroma, guest.color_hue, 0.4) }"
                    >
                        {{ guest.name }}<span v-if="idx < event.guest_organizations.length - 1" class="text-gray-400 font-normal">, </span>
                    </router-link>
                  </div>
              </template>
            </div>
          </div>
          


      </div>
    </div>
    </header>

    <!-- Event Details Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Poster -->
        <div v-if="event.poster_url" class="bg-white shadow-sm rounded-lg overflow-hidden">
          <img :src="event.poster_url" :alt="event.title" class="w-full object-cover" />
        </div>
        
        <!-- Description -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-3">Description</h2>
          <p class="text-gray-700 whitespace-pre-wrap">{{ event.description || 'Aucune description' }}</p>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <ActionPanel title="Actions">
             <ShareButton :item-id="event.id" item-type="event" :block="true" variant="indigo" />
             
             <ActionPanelButton
              v-if="canEdit"
              :icon="FaceSmileIcon"
              @click="showReactionModal = true"
              variant="amber"
              class="w-full"
            >
              Réactions
            </ActionPanelButton>
            
            <ActionPanelButton
              v-if="canEdit"
              :to="`/events/${event.id}/edit`"
              :icon="PencilIcon"
              variant="sky"
              class="w-full"
            >
              Modifier
            </ActionPanelButton>
            
            <ActionPanelButton
               v-if="canEdit"
               :icon="DocumentDuplicateIcon"
               @click="duplicateEvent"
               variant="cyan"
               class="w-full"
            >
              Dupliquer
            </ActionPanelButton>
            
            <ActionPanelButton
              :to="`/countdown/${event.id}`"
              target="_blank"
              :icon="ClockIcon"
              variant="rose"
              class="w-full"
            >
              Compte à rebours
            </ActionPanelButton>
        </ActionPanel>

        <!-- Date & Time -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Date et heure</h3>
          
          <div class="space-y-3">
            <div>
              <p class="text-xs text-gray-500">Début</p>
              <p class="text-sm font-medium text-gray-900">{{ formatDateTime(event.start_time) }}</p>
            </div>
            
            <div>
              <p class="text-xs text-gray-500">Fin</p>
              <p class="text-sm font-medium text-gray-900">{{ formatDateTime(event.end_time) }}</p>
            </div>
            
            <div>
              <p class="text-xs text-gray-500">Durée</p>
              <p class="text-sm font-medium text-gray-900">{{ getDuration() }}</p>
            </div>
          </div>
        </div>
        <!-- Location -->
        <div v-if="event.location" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Lieu</h3>
          <p class="text-sm text-gray-700 flex items-center">
            <MapPinIcon class="h-5 w-5 text-gray-400 mr-2" />
            <a 
              v-if="event.location_url" 
              :href="event.location_url" 
              target="_blank" 
              class="text-indigo-600 hover:text-indigo-500 hover:underline"
            >
              {{ event.location }}
            </a>
            <span v-else>{{ event.location }}</span>
          </p>
        </div>

        <!-- Visibility & Group Info -->
        <div v-if="event.visibility === 'private' && event.group" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Groupe</h3>
          <p class="text-sm text-gray-700 flex items-center">
            <LockClosedIcon class="h-5 w-5 text-gray-400 mr-2" />
            <span class="font-medium text-gray-900">{{ event.group.name }}</span>
          </p>
          <p class="text-xs text-gray-500 mt-1">Événement privé, visible uniquement par les membres du groupe</p>
        </div>
        
        <OrganizationCard 
          :organization="event.organization" 
          :show-type="true"
          :no-border="true"
          class="shadow-sm bg-white rounded-lg" 
        />
        
        <!-- Guest Organizations -->
        <OrganizationCard 
            v-for="guest in event.guest_organizations"
            :key="guest.id"
            :organization="guest"
            :show-type="true"
            :no-border="true"
            class="shadow-sm bg-white rounded-lg"
        />
        
        <!-- Tags -->
        <div v-if="event.tags && event.tags.length > 0" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Tags</h3>
          <div class="flex flex-wrap gap-2">
            <TagBadge 
              v-for="tag in event.tags" 
              :key="tag.id" 
              :tag="tag" 
              :organization="event.organization"
              :subscribed="isSubscribedToTag(tag.id)"
              :show-subscribe="true"
              @toggle-subscription="toggleTagSubscription"
            />
          </div>
        </div>

        

        
      </div>
    </div>
    
    <ReactionAdminModal 
      v-if="canEdit" 
      v-model="showReactionModal" 
      :event-id="event.id"
      @change="loadEvent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import api from '../utils/api'
import { 
  ClockIcon, 
  MapPinIcon, 
  PencilIcon,
  BellIcon,
  BellSlashIcon,
  DocumentTextIcon,
  LockClosedIcon,
  GlobeAltIcon,
  InformationCircleIcon,
  DocumentDuplicateIcon
} from '@heroicons/vue/24/outline'
import { formatLocalDate } from '../utils/dateUtils'
import TagBadge from '../components/TagBadge.vue'
import OrganizationCard from '../components/OrganizationCard.vue'
import ReactionList from '../components/ReactionList.vue'
import ReactionAdminModal from '../components/ReactionAdminModal.vue'
import { FaceSmileIcon } from '@heroicons/vue/24/outline'
import { getOrgColor, getEventGradient } from '../utils/colorUtils'
import ShareButton from '../components/ShareButton.vue'
import ActionPanel from '../components/ActionPanel.vue'
import ActionPanelButton from '../components/ActionPanelButton.vue'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const event = ref(null)
const userMemberships = ref([])
const subscriptions = ref([])
const loading = ref(true)
const showReactionModal = ref(false)

const canEdit = computed(() => {
  if (!event.value || !user.value) return false
  
  // Superadmin can edit anything
  if (user.value.is_superadmin) return true
  
  // Check if user is admin or member of the event's organization
  return userMemberships.value.some(m => 
    m.organization_id === event.value.organization.id && 
    (m.role === 'org_admin' || m.role === 'org_member')
  )
})

const formatDateTime = (dateString) => {
  return formatLocalDate(dateString, { dateStyle: 'full', timeStyle: 'short' })
}

const getDuration = () => {
  if (!event.value) return ''
  
  const start = new Date(event.value.start_time)
  const end = new Date(event.value.end_time)
  const diffMs = end - start
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h${minutes > 0 ? ` ${minutes}min` : ''}`
  }
  return `${minutes} min`
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

const loadUserMemberships = async () => {
  try {
    const response = await api.get('/users/me/memberships')
    userMemberships.value = response.data
  } catch (error) {
    console.error('Failed to load memberships:', error)
  }
}

const loadSubscriptions = async () => {
  try {
    const response = await api.get('/subscriptions/me')
    subscriptions.value = [
      ...response.data.organizations,
      ...response.data.tags
    ]
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  }
}

import { askPermissionAndSubscribe } from '../utils/push'

const isSubscribedToTag = (tagId) => {
  return subscriptions.value.some(sub => sub.tag?.id === tagId)
}

const toggleTagSubscription = async (tag) => {
  const subscription = subscriptions.value.find(sub => sub.tag?.id === tag.id)
  
  try {
    if (subscription) {
      await api.delete(`/subscriptions/tags/${tag.id}`)
      subscriptions.value = subscriptions.value.filter(sub => sub.tag?.id !== tag.id)
    } else {
      const response = await api.post(`/subscriptions/tags/${tag.id}`)
      subscriptions.value.push({
        id: response.data.subscription_id,
        tag: { id: tag.id }
      })
      askPermissionAndSubscribe()
    }
  } catch (error) {
    console.error('Failed to toggle subscription:', error)
  }
}

const duplicateEvent = () => {
  router.push({
    name: 'CreateEvent',
    state: { duplicateEvent: JSON.parse(JSON.stringify(event.value)) }
  })
}

onMounted(() => {
  loadEvent()
  loadUserMemberships()
  loadSubscriptions()
})
</script>
