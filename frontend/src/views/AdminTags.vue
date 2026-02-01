<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Gestion des tags</h1>
    
    <div class="mb-6">
        <OrganizationSelector 
            :organizations="organizations" 
            v-model="selectedOrganizationId"
            label="Choisir une organisation"
        />
    </div>

    <div v-if="selectedOrganizationId" class="bg-white shadow-sm rounded-lg overflow-hidden">
      <!-- Search & Filter -->
        <div class="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
           <div class="relative rounded-md shadow-sm max-w-xs w-full">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
            </div>
            <input 
              type="text" 
              v-model="searchQuery"
              class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
              placeholder="Rechercher un tag..." 
            />
          </div>
          <div class="text-sm text-gray-500">
             {{ filteredTags.length }} tags trouvés
          </div>
        </div>

      <ul role="list" class="divide-y divide-gray-100">
        <li v-for="tag in filteredTags" :key="tag.id" class="relative flex justify-between gap-x-6 px-4 py-5 hover:bg-gray-50 sm:px-6">
          <div class="flex min-w-0 gap-x-4">
             <!-- Color dot -->
            <div class="flex items-center">
                 <span class="inline-block w-4 h-4 rounded-full" :style="{ backgroundColor: tag.color }"></span>
            </div>
            <div class="min-w-0 flex-auto">
              <p class="text-sm font-semibold leading-6 text-gray-900">
                <span class="absolute inset-x-0 -top-px bottom-0" />
                {{ tag.name }}
              </p>
              <p class="mt-1 flex text-xs leading-5 text-gray-500">
                Id: {{ tag.id }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-x-4 z-10">
               <label class="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    :checked="tag.is_auto_approved" 
                    class="sr-only peer"
                    @change="toggleAutoApprove(tag)"
                    :disabled="loadingId === tag.id"
                  >
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  <span class="ml-3 text-sm font-medium text-gray-900">Auto-approuvé</span>
                </label>
          </div>
        </li>
        <li v-if="filteredTags.length === 0" class="px-4 py-6 text-center text-gray-500">
            Aucun tag trouvé pour cette organisation
        </li>
      </ul>
    </div>
    

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../utils/api'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import OrganizationSelector from '../components/OrganizationSelector.vue'

const tags = ref([])
const organizations = ref([])
const selectedOrganizationId = ref(null)
const searchQuery = ref('')
const loadingId = ref(null)

const filteredTags = computed(() => {
    if (!searchQuery.value) return tags.value
    const query = searchQuery.value.toLowerCase()
    return tags.value.filter(t => t.name.toLowerCase().includes(query))
})

const loadOrganizations = async () => {
    try {
        const response = await api.get('/organizations/') 
        organizations.value = response.data
    } catch (error) {
        console.error('Failed to load organizations:', error)
    }
}

const loadTags = async () => {
    if (!selectedOrganizationId.value) {
        tags.value = []
        return
    }
    
    try {
        const response = await api.get(`/organizations/${selectedOrganizationId.value}/tags`)
        tags.value = response.data
    } catch (error) {
        console.error('Failed to load tags:', error)
        tags.value = []
    }
}

const toggleAutoApprove = async (tag) => {
    loadingId.value = tag.id
    try {
        const newValue = !tag.is_auto_approved
        await api.put(`/tags/${tag.id}/auto-approve`, null, {
            params: { is_auto_approved: newValue }
        })
        tag.is_auto_approved = newValue
    } catch (error) {
        console.error('Failed to toggle auto-approve:', error)
        loadTags()
    } finally {
        loadingId.value = null
    }
}

watch(selectedOrganizationId, () => {
    loadTags()
})

onMounted(() => {
    loadOrganizations()
})
</script>
