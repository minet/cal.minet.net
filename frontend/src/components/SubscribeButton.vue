<template>
  <ActionPanelButton 
    @click="toggleSubscription"
    :disabled="loading"
    :variant="isSubscribed ? 'neutral' : 'amber'"
    :icon="isSubscribed ? BellSlashIcon : BellIcon"
    :class="[
      loading ? 'opacity-50 cursor-not-allowed' : ''
    ]"
  >
    {{ isSubscribed ? 'Se désabonner' : 'S\'abonner' }}
  </ActionPanelButton>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { BellIcon, BellSlashIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'
import ActionPanelButton from './ActionPanelButton.vue' // Import ActionPanelButton

import { askPermissionAndSubscribe } from '../utils/push'

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
      // Ask for push permission
      askPermissionAndSubscribe()
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
