<template>
  <component 
    :is="tag"
    :to="to"
    :href="href"
    :target="target"
    :class="[
      'inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-semibold shadow-sm ring-1 ring-inset gap-3', 
      block ? 'w-full' : '',
      variantClass
    ]"
    @click="$emit('click', $event)"
  >
    <component :is="icon" class="h-5 w-5 flex-shrink-0" />
    <span class="flex-1 text-left truncate"><slot /></span>
  </component>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  icon: {
    type: [Object, Function], // Component
    required: true
  },
  to: {
    type: [String, Object],
    default: null
  },
  href: {
    type: String,
    default: null
  },
  target: {
      type: String,
      default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'secondary', 'accent', 'neutral', 'ghost', 'outline', 'danger', 'purple', 'emerald', 'gray', 'indigo', 'amber', 'rose', 'sky', 'cyan'].includes(value)
  },
  block: {
      type: Boolean,
      default: false
  }
});

defineEmits(['click']);

const tag = computed(() => {
  if (props.to) return 'router-link';
  if (props.href) return 'a';
  return 'button';
});

const variantClass = computed(() => {
  switch (props.variant) {
    case 'primary': return 'bg-indigo-600 text-white ring-indigo-600 hover:bg-indigo-500 shadow-sm transition-all duration-200';
    case 'secondary': return 'bg-purple-600 text-white ring-purple-600 hover:bg-purple-500 shadow-sm transition-all duration-200';
    case 'accent': return 'bg-teal-600 text-white ring-teal-600 hover:bg-teal-500 shadow-sm transition-all duration-200';
    case 'neutral': return 'bg-gray-900 text-white ring-gray-900 hover:bg-gray-800 shadow-sm transition-all duration-200';
    case 'ghost': return 'bg-transparent text-gray-900 ring-transparent hover:bg-gray-50 transition-all duration-200';
    case 'outline': return 'bg-transparent text-gray-900 ring-gray-300 hover:bg-gray-50 transition-all duration-200';
    case 'danger': return 'bg-red-600 text-white ring-red-600 hover:bg-red-500 shadow-sm transition-all duration-200';
    
    // Custom colors matching original design (with improved contrast/hover)
    case 'purple': return 'bg-purple-500 text-white ring-purple-500 hover:bg-purple-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'emerald': return 'bg-emerald-500 text-white ring-emerald-500 hover:bg-emerald-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'gray': return 'bg-gray-500 text-white ring-gray-500 hover:bg-gray-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'indigo': return 'bg-indigo-500 text-white ring-indigo-500 hover:bg-indigo-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'amber': return 'bg-amber-500 text-white ring-amber-500 hover:bg-amber-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'rose': return 'bg-rose-500 text-white ring-rose-500 hover:bg-rose-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'sky': return 'bg-sky-500 text-white ring-sky-500 hover:bg-sky-600 shadow-md hover:shadow-lg transition-all duration-200';
    case 'cyan': return 'bg-cyan-500 text-white ring-cyan-500 hover:bg-cyan-600 shadow-md hover:shadow-lg transition-all duration-200';
    
    // Default white style requested
    default: return 'bg-white text-gray-900 ring-gray-300 hover:bg-gray-50 shadow-sm hover:shadow transition-all duration-200';
  }
});
</script>
