<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-sm text-gray-500">Chargement...</p>
  </div>

  <div v-else-if="organization">
    <!-- Header -->
    <header 
      class="shadow-sm rounded-lg mb-6 overflow-hidden transition-colors"
      :style="{ 
        backgroundColor: getOrgColor(organization.color_chroma/20, organization.color_hue, 1),
        borderTop: `4px solid ${getOrgColor(organization.color_chroma, organization.color_hue, 0.6)}`
      }"
    >
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div 
              class="h-16 w-16 rounded-full flex items-center justify-center overflow-hidden transition-colors"
              :style="{ backgroundColor: getOrgColor(organization.color_chroma/20, organization.color_hue, 1) }"
              :class="{ 'bg-indigo-100': organization.color_chroma === null }"
            >
              <img v-if="organization.logo_url" :src="organization.logo_url" :alt="organization.name" class="h-full w-full object-cover" />
              <span 
                v-else 
                class="text-2xl font-semibold"
                :style="{ color: getOrgColor(organization.color_chroma, organization.color_hue, 0.4) }"
                :class="{ 'text-indigo-600': organization.color_chroma === null }"
              >{{ organization.name.charAt(0) }}</span>
            </div>
            <div>
              <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ organization.name }}</h1>
              <p class="text-sm text-gray-500">{{ organization.type }}</p>
            </div>
          </div>
          

        </div>

      </div>
    </header>

    <ActionPanel 
       title="Actions"
       content-class="flex flex-col lg:flex-row lg:flex-wrap lg:gap-3 lg:space-y-0"
    >
         <ShareButton 
            v-if="isMember || (user && user.is_superadmin)"
            :item-id="organization.id" 
            item-type="organization" 
            :block="true"
            variant="indigo"
            class="lg:w-auto"
            :organization="organization"
         />
         
         <SubscribeButton 
            v-if="!isMember" 
            :organization-id="organization.id" 
            class="w-full lg:w-auto" 
         />
         
         <ActionPanelButton 
            v-if="canEdit"
            :to="`/organizations/${organization.id}/tags`"
            :icon="TagIcon"
            variant="purple"
            class="w-full lg:w-auto"
          >
            Tags
          </ActionPanelButton>
          
          <ActionPanelButton 
            v-if="canEdit"
            :to="`/organizations/${organization.id}/groups`"
            :icon="UsersIcon"
            variant="emerald"
            class="w-full lg:w-auto"
          >
            Groupes
          </ActionPanelButton>
          
          <ActionPanelButton 
            v-if="canEdit"
            :to="`/organizations/${organization.id}/members`"
            :icon="UserGroupIcon"
            variant="gray"
            class="w-full lg:w-auto"
          >
            Membres
          </ActionPanelButton>
          
          <ActionPanelButton 
            v-if="canEdit"
            :to="`/organizations/${organization.id}/edit`"
            :icon="PencilIcon"
            variant="sky"
            class="w-full lg:w-auto"
          >
            Modifier
          </ActionPanelButton>

          <template #footer>
            <p v-if="!isMember" class="text-xs text-gray-500 mt-2 text-center" >
              S'abonner ajoute les événements à votre <router-link to="/profile" class="text-indigo-600 hover:underline">calendrier</router-link>
            </p>
          </template>
    </ActionPanel>

    <!-- Description -->
    <div v-if="organization.description" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Description</h2>
      <p class="text-gray-700 whitespace-pre-wrap">{{ organization.description }}</p>
    </div>

    <!-- Parent Organization -->
    <div v-if="parent" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Organisation parente</h2>
      <router-link 
        :to="`/organizations/${parent.id}`"
        class="flex items-center space-x-3 hover:bg-gray-50 p-3 rounded-lg transition-colors"
      >
        <div 
          class="h-10 w-10 rounded-full flex items-center justify-center"
          :style="{ backgroundColor: getOrgColor(parent.color_chroma/20, parent.color_hue, 1) }"
        >
          <img v-if="parent.logo_url" :src="parent.logo_url" :alt="parent.name" class="h-full w-full object-cover rounded-full" />
          <span 
            v-else 
            class="font-semibold"
            :style="{ color: getOrgColor(parent.color_chroma, parent.color_hue, 0.4) }"
          >{{ parent.name.charAt(0) }}</span>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">{{ parent.name }}</p>
          <p class="text-xs text-gray-500">{{ parent.type }}</p>
        </div>
      </router-link>
    </div>
    
    <!-- Custom Links -->
    <div v-if="organization.organization_links && organization.organization_links.length > 0" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Liens</h2>
      <ul class="space-y-2">
        <li v-for="link in organization.organization_links" :key="link.id">
            <a :href="link.url" target="_blank" class="text-indigo-600 hover:text-indigo-800 flex items-center">
                <LinkIcon class="h-4 w-4 mr-2" />
                {{ link.name }}
            </a>
        </li>
      </ul>
    </div>

    <!-- Tags -->
    <div v-if="tags.length > 0" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Tags</h2>
      <div class="flex flex-wrap gap-2">
        <TagBadge 
          v-for="tag in tags" 
          :key="tag.id" 
          :tag="tag" 
          :organization="organization"
          :subscribed="isSubscribedToTag(tag.id)"
          :show-subscribe="true"
          :show-share="isMember || (user && user.is_superadmin)"
          @toggle-subscription="toggleTagSubscription"
          @share="openTagShare"
        />
      </div>
    </div>

    <!-- Members -->
    <div class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Membres</h2>
      
      <div v-if="loadingMembers" class="text-center py-4">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>
      
      <div v-else-if="members.length === 0" class="text-center py-8">
        <p class="text-sm text-gray-500">Aucun membre</p>
      </div>
      
      <ul v-else class="divide-y divide-gray-200">
        <li v-for="member in members" :key="member.user_id" class="py-4 flex items-center justify-between">
          <router-link :to="`/users/${member.user_id}`" class="flex items-center space-x-3 hover:bg-gray-50 p-2 rounded-lg transition-colors text-left w-full sm:w-auto">
            <UserAvatar 
              :src="member.profile_picture_url" 
              :name="member.full_name || member.email" 
              size="md" 
            />
            <div>
              <p class="text-sm font-medium text-gray-900">{{ member.full_name || member.email }}</p>
              <p class="text-xs text-gray-500">{{ member.email }}</p>
            </div>
          </router-link>
          <span :class="getRoleBadgeClass(member.role)" class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ml-2">
            {{ getRoleLabel(member.role) }}
          </span>
        </li>
      </ul>
    </div>

    <!-- Future Events -->
    <div class="bg-white shadow-sm rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Événements à venir</h2>
      
      <div v-if="loadingEvents" class="text-center py-4">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>
      
      <div v-else-if="events.length === 0" class="text-center py-8">
        <p class="text-sm text-gray-500">Aucun événement à venir</p>
      </div>
      
      <ul v-else class="divide-y divide-gray-200">
        <li v-for="event in events" :key="event.id" class="py-4">
          <router-link :to="`/events/${event.id}`" class="block hover:bg-gray-50 -mx-6 px-6 py-3 transition-colors">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-900">{{ event.title }}</p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ formatDate(event.start_time) }}
                  <span v-if="event.location"> • {{ event.location }}</span>
                </p>
              </div>
              <ChevronRightIcon class="h-5 w-5 text-gray-400" />
            </div>
          </router-link>
        </li>
      </ul>
    </div>
    <!-- Hidden Share Button for Tags -->
    <ShareButton 
      v-if="activeShareTag" 
      ref="tagShareButton" 
      :item-id="activeShareTag.id" 
      item-type="tag" 
      class="hidden" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import SubscribeButton from '../components/SubscribeButton.vue'
import ShareButton from '../components/ShareButton.vue'
import ActionPanel from '../components/ActionPanel.vue'
import ActionPanelButton from '../components/ActionPanelButton.vue'
import UserAvatar from '../components/UserAvatar.vue'

import TagBadge from '../components/TagBadge.vue'
import api from '../utils/api'
import { getOrgColor } from '../utils/colorUtils'
import { 
  PencilIcon, 
  ChevronRightIcon, 
  UserGroupIcon, 
  TagIcon, 
  UsersIcon,
  LinkIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const { user } = useAuth()
const organization = ref(null)
const parent = ref(null)
const members = ref([])
const events = ref([])
const tags = ref([])
const subscriptions = ref([])
const canEdit = ref(false)
const loading = ref(true)
const loadingMembers = ref(false)
const loadingEvents = ref(false)

const activeShareTag = ref(null)
const tagShareButton = ref(null)

const openTagShare = (tag) => {
  activeShareTag.value = tag
  nextTick(() => {
    tagShareButton.value?.openModal()
  })
}

const isMember = computed(() => {
  return members.value.some(m => m.user_id === user.value?.id)
})

const getRoleLabel = (role) => {
  const labels = {
    'superadmin': 'Superadmin',
    'org_admin': 'Administrateur',
    'org_member': 'Éditeur',
    'org_viewer': 'Lecteur',
  }
  return labels[role] || role
}

const getRoleBadgeClass = (role) => {
  const classes = {
    'superadmin': 'bg-purple-50 text-purple-700 ring-purple-700/10',
    'org_admin': 'bg-blue-50 text-blue-700 ring-blue-700/10',
    'org_member': 'bg-green-50 text-green-700 ring-green-600/20',
    'org_viewer': 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  }
  return classes[role] || 'bg-gray-50 text-gray-700 ring-gray-600/20'
}

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

const loadOrganization = async () => {
  try {
    const response = await api.get(`/organizations/${route.params.id}`)
    organization.value = response.data
    
    // Load parent if exists
    if (organization.value.parent_id) {
      const parentResponse = await api.get(`/organizations/${organization.value.parent_id}`)
      parent.value = parentResponse.data
    } else {
      parent.value = null
    }
  } catch (error) {
    console.error('Failed to load organization:', error)
  } finally {
    loading.value = false
  }
}

const loadMembers = async () => {
  loadingMembers.value = true
  try {
    const response = await api.get(`/organizations/${route.params.id}/members`)
    members.value = response.data
  } catch (error) {
    console.error('Failed to load members:', error)
  } finally {
    loadingMembers.value = false
  }
}

const loadEvents = async () => {
  loadingEvents.value = true
  try {
    const response = await api.get(`/organizations/${route.params.id}/events`)
    events.value = response.data
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loadingEvents.value = false
  }
}

const loadTags = async () => {
  try {
    const response = await api.get(`/organizations/${route.params.id}/tags`)
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
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

const checkCanEdit = async () => {
  try {
    const response = await api.get(`/organizations/${route.params.id}/can-edit`)
    canEdit.value = response.data.can_edit
  } catch (error) {
    console.error('Failed to check edit permission:', error)
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

const loadAll = () => {
  loading.value = true
  loadOrganization()
  loadMembers()
  loadEvents()
  loadTags()
  loadSubscriptions()
  checkCanEdit()
}

// Watch for route changes to reload data when navigating between organizations
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadAll()
  }
})

onMounted(() => {
  loadAll()
})
</script>
