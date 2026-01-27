<template>
  <div class="bg-white shadow-sm rounded-lg p-6 mb-6 ">
    <div class="flex items-center justify-between" :class="{ 'mb-4': mobileOpen || !isMobile }">
      <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
      <!-- Mobile Toggle -->
      <button class="lg:hidden btn btn-square btn-ghost btn-sm" @click="mobileOpen = !mobileOpen">
        <component :is="mobileOpen ? XMarkIcon : Bars3Icon" class="h-5 w-5" />
      </button>
    </div>

    <div :class="[contentClass, mobileOpen ? 'flex' : 'hidden lg:flex']" class="gap-1 flex-col">
      <slot />
    </div>
    <slot name="footer" />
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
  contentClass: {
    type: String,
    default: 'flex-col space-y-3'
  }
});

const mobileOpen = ref(false);
const isMobile = ref(false); // In a real app we might use useMediaQuery or just rely on CSS media queries hiding the toggle

</script>
