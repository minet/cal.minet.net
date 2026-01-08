<template>
  <div 
    class="inline-flex items-center rounded-lg border transition-all duration-200 overflow-hidden pr-2 pl-1 py-1"
    :class="[
      subscribed ? 'border-transparent shadow-sm' : 'border-gray-200 bg-white hover:border-gray-300',
      clickable ? 'cursor-pointer' : ''
    ]"
    :style="style"
    @click="handleClick"
  >
    <!-- Left: Organization Logo -->
    <div class="flex-shrink-0 mr-2">
      <div class="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden border border-gray-200">
        <img v-if="organization?.logo_url" :src="organization.logo_url" :alt="organization.name" class="h-full w-full object-cover" />
        <span v-else class="text-xs font-bold text-gray-600">{{ organization?.name?.charAt(0) || '?' }}</span>
      </div>
    </div>

    <!-- Center: Tag Name & Org Name -->
    <div class="flex flex-col mr-3 min-w-[80px]">
      <span class="text-sm font-bold leading-tight">{{ tag.name }}</span>
      <span class="text-[10px] opacity-75 leading-tight truncate max-w-[120px]">{{ organization?.name }}</span>
    </div>

    <!-- Right: Subscribe Button -->
    <button 
      v-if="showSubscribe"
      @click.stop="toggleSubscription"
      class="flex-shrink-0 p-1.5 rounded-full hover:bg-black/5 focus:outline-none transition-colors"
      :class="subscribed ? 'text-white hover:bg-white/20' : 'text-gray-400 hover:text-gray-600'"
      :title="subscribed ? 'Se désabonner' : 'S\'abonner'"
    >
      <BellSlashIcon v-if="subscribed" class="h-4 w-4" />
      <BellIcon v-else class="h-4 w-4" />
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { BellIcon, BellSlashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  tag: {
    type: Object,
    required: true
  },
  organization: {
    type: Object,
    default: null
  },
  subscribed: {
    type: Boolean,
    default: false
  },
  showSubscribe: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'toggle-subscription'])

const style = computed(() => {
  if (props.subscribed) {
    return {
      backgroundColor: props.tag.color,
      color: '#ffffff'
    }
  }
  return {
    // When not subscribed, we use default white bg and gray text, 
    // but maybe we can use the tag color for the tag name?
    // For now let's keep it simple as per the class bindings above.
    // Actually, let's use the tag color for the border or text if desired.
    // But the design request implies a more complex card-like look.
    // Let's stick to the class bindings for base style, but maybe use color for text?
    color: '#1f2937', // text-gray-900
    borderColor: props.tag.color
  }
})

const handleClick = () => {
  if (props.clickable) {
    emit('click', props.tag)
  }
}

const toggleSubscription = () => {
  emit('toggle-subscription', props.tag)
}
</script>
