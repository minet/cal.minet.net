<template>
  <div>
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Organisations</h1>
        <router-link v-if="isSuperAdmin" to="/organizations/create" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Créer une organisation</router-link>
      </div>
    </header>

    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div v-if="loading" class="text-center py-12">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>
      
      <div v-else-if="organizations.length === 0" class="text-center py-12">
        <p class="text-sm text-gray-500">Aucune organisation trouvée</p>
      </div>
      
      <ul v-else role="list" class="divide-y divide-gray-100">
        <li v-for="org in organizations" :key="org.id">
          <router-link 
            :to="`/organizations/${org.id}`"
            class="flex justify-between gap-x-6 py-5 px-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex min-w-0 gap-x-4">
              <div 
                v-if="org.logo_url" 
                class="h-12 w-12 flex-none rounded-full flex items-center justify-center overflow-hidden"
                :style="{ backgroundColor: getOrgColor(org.color_chroma/20, org.color_hue, 1) }"
              >
                <img class="h-full w-full object-cover" :src="org.logo_url" :alt="org.name" />
              </div>
              <div 
                v-else 
                class="h-12 w-12 flex-none rounded-full flex items-center justify-center bg-gray-50"
                :style="{ backgroundColor: getOrgColor(org.color_chroma/20, org.color_hue, 1) }"
              >
                <BuildingOfficeIcon 
                  class="h-7 w-7 text-gray-400" 
                  :style="{ color: getOrgColor(org.color_chroma, org.color_hue, 0.4) }"
                />
              </div>
              <div class="min-w-0 flex-auto">
                <p class="text-sm font-semibold leading-6 text-gray-900">{{ org.name }}</p>
                <p class="mt-1 truncate text-xs leading-5 text-gray-500">{{ org.description }}</p>
              </div>
            </div>
            <div class="hidden shrink-0 sm:flex sm:flex-col sm:items-end gap-2">
              <span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">{{ org.type }}</span>
              <div @click.prevent>
                <SubscribeButton :organization-id="org.id" class="!px-3 !py-1" />
              </div>
            </div>
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import api from '../utils/api'
import { getOrgColor } from '../utils/colorUtils'
import { BuildingOfficeIcon } from '@heroicons/vue/24/outline'
import SubscribeButton from '../components/SubscribeButton.vue'

const organizations = ref([])
const loading = ref(false)

const loadOrganizations = async () => {
  loading.value = true
  try {
    const response = await api.get('/organizations/')
    organizations.value = response.data
  } catch (error) {
    console.error('Failed to load organizations:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOrganizations()
})
</script>
