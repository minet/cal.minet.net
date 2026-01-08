<template>
  <div 
    class="inline-flex items-center rounded-lg border border-gray-200 bg-white hover:border-gray-300 transition-all duration-200 overflow-hidden pr-2 pl-1 py-1 shadow-sm"
  >
    <!-- Left: Organization Logo -->
    <div class="flex-shrink-0 mr-2">
      <div class="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden border border-gray-200">
        <img v-if="organization?.logo_url" :src="organization.logo_url" :alt="organization.name" class="h-full w-full object-cover" />
        <span v-else class="text-xs font-bold text-gray-600">{{ organization?.name?.charAt(0) || '?' }}</span>
      </div>
    </div>

    <!-- Center: Group Name & Org Name -->
    <div class="flex flex-col mr-3 min-w-[80px]">
      <span class="text-sm font-bold leading-tight text-gray-900">{{ group.name }}</span>
      <span class="text-[10px] text-gray-500 leading-tight truncate max-w-[120px]">{{ organization?.name }}</span>
    </div>

    <!-- Right: Leave Button -->
    <button 
      @click="$emit('leave', group)"
      class="flex-shrink-0 p-1.5 rounded-full hover:bg-red-50 text-gray-400 hover:text-red-600 focus:outline-none transition-colors"
      title="Quitter le groupe"
    >
      <XMarkIcon class="h-4 w-4" />
    </button>
  </div>
</template>

<script setup>
import { XMarkIcon } from '@heroicons/vue/24/outline'

defineProps({
  group: {
    type: Object,
    required: true
  },
  organization: {
    type: Object,
    default: null
  }
})

defineEmits(['leave'])
</script>
