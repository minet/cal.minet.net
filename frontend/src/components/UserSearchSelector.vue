<template>
  <div class="relative">
    <TextInput
      v-model="searchQuery"
      :placeholder="placeholder"
    >
      <template #icon>
        <div v-if="loading" class="absolute right-3 top-8">
          <svg class="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
      </template>
    </TextInput>

    <!-- Dropdown -->
    <div
      v-if="showDropdown && searchQuery.length > 0"
      class="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm"
    >
      <div v-if="loading" class="px-4 py-3 text-sm text-gray-500 text-center">
        Recherche...
      </div>
      <div v-else-if="filteredResults.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
        Aucun utilisateur trouvé
      </div>
      <button
        v-else
        v-for="user in filteredResults"
        :key="user.id"
        @click="selectUser(user)"
        class="w-full text-left px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center space-x-3"
      >
        <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
          <img v-if="user.profile_picture_url" :src="user.profile_picture_url" :alt="getFullName(user)" class="h-full w-full object-cover" />
          <span v-else class="text-gray-600 font-medium text-sm">{{ getInitials(user) }}</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900">{{ getFullName(user) }}</p>
          <p class="text-xs text-gray-500 truncate">{{ user.email }}</p>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import TextInput from './TextInput.vue'
import api from '../utils/api'

const props = defineProps({
  placeholder: {
    type: String,
    default: 'Rechercher un utilisateur...'
  },
  filter: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['select'])

const searchQuery = ref('')
const searchResults = ref([])
const loading = ref(false)
const showDropdown = ref(false)
let debounceTimeout = null

const filteredResults = computed(() => {
  if (!props.filter) return searchResults.value
  return searchResults.value.filter(props.filter)
})

const getFullName = (user) => {
  if (user.full_name) {
    return user.full_name
  }
  return user.email || 'Inconnu'
}

const getInitials = (user) => {
  const name = getFullName(user)
  if (!name) return '?'
  return name
    .split(/\s+/)
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

// Watch for search query changes
watch(searchQuery, () => {
  clearTimeout(debounceTimeout)
  
  if (searchQuery.value.length === 0) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  
  showDropdown.value = true
  debounceTimeout = setTimeout(async () => {
    await searchUsers()
  }, 300)
})

const searchUsers = async () => {
  if (searchQuery.value.length === 0) return
  
  loading.value = true
  try {
    const response = await api.get(`/users/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = response.data
  } catch (error) {
    console.error('Failed to search users:', error)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const selectUser = (user) => {
  emit('select', user)
  searchQuery.value = ''
  searchResults.value = []
  showDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showDropdown.value = false
  }
}

if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}
</script>
