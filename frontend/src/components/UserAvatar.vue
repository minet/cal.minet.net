<template>
  <div 
    :class="[
      'rounded-full flex items-center justify-center overflow-hidden bg-gray-200',
      sizeClass
    ]"
  >
    <img 
      v-if="src" 
      :src="src" 
      :alt="alt" 
      class="h-full w-full object-cover" 
    />
    <span v-else :class="['font-medium text-gray-600', textSizeClass]">
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: 'User avatar'
  },
  name: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  }
})

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .split(/\s+/)
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
})

const sizeClass = computed(() => {
  const sizes = {
    xs: 'h-6 w-6',
    sm: 'h-8 w-8',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16',
    '2xl': 'h-24 w-24'
  }
  return sizes[props.size]
})

const textSizeClass = computed(() => {
  const sizes = {
    xs: 'text-xs',
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-xl',
    '2xl': 'text-3xl'
  }
  return sizes[props.size]
})
</script>
