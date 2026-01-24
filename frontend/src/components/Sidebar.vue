<template>
  <div v-if="isAuthenticated" class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-2xl overflow-y-auto transform transition-transform duration-300 lg:translate-x-0" :class="{ '-translate-x-full lg:translate-x-0': !isOpen, 'translate-x-0': isOpen }">
    <!-- User Section -->
    <div class="p-6 border-b border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <img src="/CalendINT_text.svg" alt="Calend'INT" class="h-16 w-auto" />
        <button @click="$emit('close')" class="md:hidden text-gray-500 hover:text-gray-700">
          <XMarkIcon class="h-6 w-6" />
        </button>
      </div>
      <router-link v-if="user" to="/profile" class="flex items-center space-x-3 hover:bg-gray-50 p-2 -m-2 rounded-lg transition-colors group">
        <UserAvatar 
          :src="user.profile_picture_url" 
          :name="user.full_name || user.email" 
          size="md" 
        />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate group-hover:text-indigo-600 transition-colors">{{ user.full_name || user.email }}</p>
          <p class="text-xs text-gray-500 truncate">Voir mon profil</p>
        </div>
      </router-link>
    </div>

    <!-- Navigation Links -->
    <div class="px-6 py-4 space-y-6">
      <!-- Accès rapide -->
      <div>
        <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Accès rapide</h4>
        <nav class="space-y-1">
          <router-link to="/" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-slate-50 hover:text-slate-700">
            <NewspaperIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-slate-500 transition-colors" />
            À venir
          </router-link>

          <router-link 
            v-if="isSuperAdmin || organizations.length > 0"
            to="/events/create" 
            class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-indigo-50 hover:text-indigo-700"
          >
            <PlusIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-indigo-500 transition-colors" />
            Nouvel événement
          </router-link>

          <router-link 
            v-if="isSuperAdmin || organizations.length > 0" 
            to="/my-events" 
            class="group flex items-center justify-between px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-slate-50 hover:text-slate-700"
          >
            <div class="flex items-center">
              <TicketIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-slate-500 transition-colors" />
              Mes événements
            </div>
            <span 
              v-if="user?.rejected_events_count > 0" 
              class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
            >
              {{ user.rejected_events_count }}
            </span>
          </router-link>

        </nav>
      </div>

      <!-- Administration -->
      <div v-if="isSuperAdmin">
        <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Administration</h4>
        <nav class="space-y-1">
          <router-link 
            to="/approval-requests" 
            class="group flex items-center justify-between px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-amber-50 hover:text-amber-700"
          >
            <div class="flex items-center">
              <ClipboardDocumentCheckIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-amber-500 transition-colors" />
              Approbations
            </div>
            <span 
              v-if="user?.pending_approvals_count > 0" 
              class="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800"
            >
              {{ user.pending_approvals_count }}
            </span>
          </router-link>

          <router-link to="/admin/users" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50 hover:text-gray-900">
            <UsersIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-gray-500 transition-colors" />
            Utilisateurs
          </router-link>

          <router-link to="/admin/tags" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50 hover:text-gray-900">
            <TagIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-gray-500 transition-colors" />
            Tags
          </router-link>
        </nav>
      </div>

      <!-- Découvrir -->
      <div>
        <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Découvrir</h4>
        <nav class="space-y-1">
          <router-link to="/dashboard" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-emerald-50 hover:text-emerald-700">
            <CalendarIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-emerald-500 transition-colors" />
            Calendrier
          </router-link>

          <router-link to="/events" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-pink-50 hover:text-pink-700">
            <CalendarDaysIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-pink-500 transition-colors" />
            Tous les événements
          </router-link>

          <router-link to="/subscriptions" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-purple-50 hover:text-purple-700">
            <BellIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-purple-500 transition-colors" />
            Mes abonnements
          </router-link>

          <router-link to="/organizations" class="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-blue-50 hover:text-blue-700">
            <BuildingOfficeIcon class="h-5 w-5 mr-3 text-gray-400 group-hover:text-blue-500 transition-colors" />
            Toutes les organisations
          </router-link>
        </nav>
      </div>
    </div>

    <!-- My Organizations Section -->
    <div class="px-6 pb-6" v-if="user && organizations.length > 0 && !loading">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Mes organisations</h4>
      </div>
            
      <nav class="">
        <div v-for="org in organizations" :key="org.id" class="group">
          <div class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-colors">
            <router-link :to="`/organizations/${org.id}`" class="flex items-center space-x-3 flex-1 min-w-0">
              <div 
                class="flex-shrink-0 h-6 w-6 rounded-full flex items-center justify-center overflow-hidden transition-colors"
                :style="{ backgroundColor: getOrgColor(org.color_chroma/20, org.color_hue, 1) }"
                :class="{ 'bg-gray-200': org.color_chroma === null }"
              >
                <img v-if="org.logo_url" :src="org.logo_url" :alt="org.name" class="h-full w-full object-cover" />
                <span v-else class="text-xs font-medium" :style="{ color: getOrgColor(org.color_chroma, org.color_hue, 0.4) }">{{ org.name.charAt(0) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">{{ org.name }}</p>
              </div>
            </router-link>
            <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <router-link :to="`/organizations/${org.id}/edit`" class="p-1 text-gray-400 hover:text-indigo-600" title="Modifier">
                <Cog6ToothIcon class="h-4 w-4" />
              </router-link>
            </div>
          </div>
        </div>
      </nav>
    </div>

    <!-- Logout Button -->
    <div class="p-6 border-t border-gray-200">
      <button @click="handleLogout" class="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
        <ArrowRightOnRectangleIcon class="h-5 w-5 mr-2" />
        Logout
      </button>
    </div>
  </div>

  <!-- Overlay for mobile -->
  <div v-if="isAuthenticated && isOpen" @click="$emit('close')" class="fixed inset-0 bg-black/50 z-40 md:hidden"></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import api from '../utils/api'
import UserAvatar from './UserAvatar.vue'
import { getOrgColor } from '../utils/colorUtils'
import { 
  XMarkIcon, 
  PlusIcon, 
  CalendarIcon, 
  Cog6ToothIcon,
  BuildingOfficeIcon,
  CalendarDaysIcon,
  ArrowRightOnRectangleIcon,
  BellIcon,
  NewspaperIcon,
  TicketIcon,
  ClipboardDocumentCheckIcon,
  UsersIcon,
  TagIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true
  }
})

defineEmits(['close'])

const { user, isAuthenticated, isSuperAdmin, logout } = useAuth()
const organizations = ref([])
const loading = ref(false)

const loadUserOrganizations = async () => {
  if (!isAuthenticated.value) return
  
  loading.value = true
  try {
    const response = await api.get('/users/me/organizations')
    organizations.value = response.data
  } catch (error) {
    console.error('Failed to load organizations:', error)
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  logout()
}

onMounted(() => {
  loadUserOrganizations()
})
</script>
