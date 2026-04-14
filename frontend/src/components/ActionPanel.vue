<template>
  <div class="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl mb-6 overflow-hidden transition-all duration-200">
    <div class="px-6 py-4 flex items-center justify-between border-b border-gray-100" :class="{ 'pb-4': mobileOpen || !isMobile, 'border-b-0': !mobileOpen && isMobile }">
      <slot name="header">
        <div>
          <h3 class="text-base font-semibold leading-6 text-gray-900">{{ title }}</h3>
          <p v-if="description" class="mt-1 flex text-sm text-gray-500">{{ description }}</p>
        </div>
      </slot>
      <!-- Mobile Toggle -->
      <button class="lg:hidden p-2 -mr-2 text-gray-400 hover:bg-gray-100 rounded-lg transition-colors" @click="mobileOpen = !mobileOpen">
        <component :is="mobileOpen ? XMarkIcon : Bars3Icon" class="h-5 w-5" />
      </button>
    </div>

    <!-- Content -->
    <div :class="[contentClass, mobileOpen ? 'flex' : 'hidden lg:flex', paddingClass]" class="flex-col gap-2">
      <slot />
    </div>

    <!-- Optional Footer -->
    <div v-if="$slots.footer" class="bg-gray-50 px-6 py-4 border-t border-gray-100">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline';

defineProps({
  title: {
    type: String,
    default: 'Actions'
  },
  description: {
    type: String,
    default: ''
  },
  contentClass: {
    type: String,
    default: ''
  },
  paddingClass: {
    type: String,
    default: 'p-6'
  }
});

const mobileOpen = ref(false);
const isMobile = ref(false); // In a real app we might use useMediaQuery
</script>
