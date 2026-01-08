<template>
  <button 
    @click="toggleSubscription"
    :disabled="loading"
    :class="[
      'inline-flex items-center px-4 py-2 text-sm font-semibold rounded-md transition-colors',
      isSubscribed 
        ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
        : 'bg-indigo-600 text-white hover:bg-indigo-700',
      loading ? 'opacity-50 cursor-not-allowed' : ''
    ]"
  >
    <BellIcon v-if="!isSubscribed" class="h-5 w-5 mr-2" />
    <BellSlashIcon v-else class="h-5 w-5 mr-2" />
    {{ isSubscribed ? 'Se désabonner' : 'S\'abonner' }}
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BellIcon, BellSlashIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'

const props = defineProps({
  organizationId: {
    type: String,
    required: true
  }
})

const isSubscribed = ref(false)
const loading = ref(false)

const checkSubscription = async () => {
  try {
    const response = await api.get('/subscriptions/me')
    isSubscribed.value = response.data.organizations.some(
      sub => sub.organization?.id === props.organizationId
    )
  } catch (error) {
    console.error('Failed to check subscription:', error)
  }
}

const toggleSubscription = async () => {
  loading.value = true
  try {
    if (isSubscribed.value) {
      await api.delete(`/subscriptions/organizations/${props.organizationId}`)
      isSubscribed.value = false
    } else {
      await api.post(`/subscriptions/organizations/${props.organizationId}`)
      isSubscribed.value = true
    }
  } catch (error) {
    console.error('Failed to toggle subscription:', error)
    alert(error.response?.data?.detail || 'Erreur lors de l\'abonnement')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkSubscription()
})
</script>
