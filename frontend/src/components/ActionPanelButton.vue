<template>
  <component 
    :is="resolvedTag"
    :to="to"
    :href="resolvedHref"
    :target="target"
    :disabled="disabled || loading"
    :class="[
      'group relative inline-flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed', 
      block ? 'w-full flex-1' : '',
      active ? 'active:scale-95' : '',
      computedAlignClass,
      computedVariantClass
    ]"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <svg v-if="loading" class="animate-spin h-5 w-5 flex-shrink-0" :class="hasText ? 'mr-3 -ml-0.5' : ''" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Left Icon (Primary) -->
    <component 
      v-else-if="icon" 
      :is="icon" 
      :class="[
        'h-5 w-5 flex-shrink-0 transition-transform duration-200',
        hasText ? 'mr-3 -ml-0.5' : '',
        computedIconClass
      ]" 
    />
    
    <!-- Content (Slot) -->
    <span v-if="hasText" class="truncate" :class="[block ? 'flex-1' : '']">
      <slot />
    </span>

    <!-- Right Icon (Trailing) -->
    <component 
      v-if="trailingIcon" 
      :is="trailingIcon" 
      :class="[
        'h-5 w-5 flex-shrink-0 transition-transform duration-200 opacity-70 group-hover:opacity-100',
        hasText ? 'ml-3 -mr-0.5' : '',
        computedIconClass
      ]" 
    />
  </component>
</template>

<script setup>
import { computed, useSlots } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  icon: {
    type: [Object, Function],
    default: null
  },
  trailingIcon: {
    type: [Object, Function],
    default: null
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
  },
  align: {
    type: String,
    default: 'left',
    validator: (v) => ['left', 'center', 'right'].includes(v)
  },
  block: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['click']);
const router = useRouter();
const slots = useSlots();

const hasText = computed(() => !!slots.default);

const computedAlignClass = computed(() => {
  if (!props.block) return 'justify-center';
  switch (props.align) {
    case 'center': return 'justify-center text-center';
    case 'right': return 'justify-end text-right';
    case 'left':
    default: return 'justify-start text-left';
  }
});

const handleClick = (event) => {
  if (props.disabled || props.loading) {
    event.preventDefault();
    return;
  }
  emit('click', event);
};

const resolvedTag = computed(() => {
  if (props.to && props.target) return 'a';
  if (props.to) return 'router-link';
  if (props.href) return 'a';
  return 'button';
});

const resolvedHref = computed(() => {
  if (props.to && props.target) {
    try { return router.resolve(props.to).href; } catch (e) { return props.to; }
  }
  return props.href;
});

const computedVariantClass = computed(() => {
  switch (props.variant) {
    case 'primary': return 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-600 shadow-sm border border-transparent';
    case 'secondary': return 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-600 shadow-sm border border-transparent';
    case 'accent': return 'bg-teal-600 text-white hover:bg-teal-700 focus:ring-teal-600 shadow-sm border border-transparent';
    case 'neutral': return 'bg-gray-900 text-white hover:bg-gray-800 focus:ring-gray-900 shadow-sm border border-transparent';
    case 'danger': return 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-600 shadow-sm border border-transparent';
    
    // Soft background variants for modern subtle UI
    case 'soft-primary': return 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 hover:text-indigo-800 focus:ring-indigo-500 border border-transparent';
    case 'soft-danger': return 'bg-red-50 text-red-700 hover:bg-red-100 hover:text-red-800 focus:ring-red-500 border border-transparent';
    case 'soft-success': return 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 hover:text-emerald-800 focus:ring-emerald-500 border border-transparent';

    case 'ghost': return 'bg-transparent text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-500 border border-transparent';
    case 'outline': return 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 hover:text-gray-900 focus:ring-gray-500 shadow-sm';
    
    // Custom colors matching original design
    case 'purple': return 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-600 shadow-sm border border-transparent';
    case 'fuchsia': return 'bg-fuchsia-600 text-white hover:bg-fuchsia-700 focus:ring-fuchsia-600 shadow-sm border border-transparent';
    case 'pink': return 'bg-pink-600 text-white hover:bg-pink-700 focus:ring-pink-600 shadow-sm border border-transparent';
    case 'rose': return 'bg-rose-600 text-white hover:bg-rose-700 focus:ring-rose-600 shadow-sm border border-transparent';
    case 'orange': return 'bg-orange-500 text-white hover:bg-orange-600 focus:ring-orange-500 shadow-sm border border-transparent';
    case 'amber': return 'bg-amber-500 text-white hover:bg-amber-600 focus:ring-amber-500 shadow-sm border border-transparent';
    case 'emerald': return 'bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-600 shadow-sm border border-transparent';
    case 'green': return 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-600 shadow-sm border border-transparent';
    case 'teal': return 'bg-teal-600 text-white hover:bg-teal-700 focus:ring-teal-600 shadow-sm border border-transparent';
    case 'cyan': return 'bg-cyan-600 text-white hover:bg-cyan-700 focus:ring-cyan-600 shadow-sm border border-transparent';
    case 'sky': return 'bg-sky-500 text-white hover:bg-sky-600 focus:ring-sky-500 shadow-sm border border-transparent';
    case 'blue': return 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-600 shadow-sm border border-transparent';
    case 'indigo': return 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-600 shadow-sm border border-transparent';
    case 'violet': return 'bg-violet-600 text-white hover:bg-violet-700 focus:ring-violet-600 shadow-sm border border-transparent';
    case 'gray': return 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-600 shadow-sm border border-transparent';
    
    // Default outline-like style as fallback
    default: return 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:text-gray-900 focus:ring-gray-500 shadow-sm';
  }
});

const computedIconClass = computed(() => {
  if (['ghost', 'outline', 'default'].includes(props.variant)) return 'text-gray-400 group-hover:text-gray-500';
  if (props.variant.startsWith('soft-')) return ''; // use text color inherit via CSS
  return 'text-white/80 group-hover:text-white';
});
</script>
