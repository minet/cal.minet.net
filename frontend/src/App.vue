<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Layout-less routes (like countdown) -->
    <template v-if="$route.meta.layout === 'none'">
      <router-view />
    </template>
    
    <!-- Normal layout with sidebar -->
    <template v-else>
      <Sidebar v-if="isAuthenticated" :is-open="sidebarOpen" @close="sidebarOpen = false" />
      
      <div :class="[isAuthenticated ? 'lg:pl-72' : '', 'flex flex-col min-h-screen']">
        <!-- Mobile menu button -->
        <div v-if="isAuthenticated" class="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:hidden">
          <button type="button" @click="sidebarOpen = true" class="-m-2.5 p-2.5 text-gray-700">
            <Bars3Icon class="h-6 w-6" />
          </button>
        </div>

        <!-- Sign in button for unauthenticated users -->
        <div v-else-if="$route.name !== 'Feed'" class="sticky top-0 z-40 flex h-16 items-center justify-end gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:px-6">
          <router-link to="/login" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            Se connecter
          </router-link>
        </div>

        <!-- Main content -->
        <main class="flex-1" :class="[$route.name !== 'Feed' ? 'py-10' : '']">
          <div :class="[$route.name !== 'Feed' ? 'px-4 sm:px-6 lg:px-8' : '']">
            <router-view />
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from './composables/useAuth'
import Sidebar from './components/Sidebar.vue'
import { Bars3Icon } from '@heroicons/vue/24/outline'

const { isAuthenticated, initialize } = useAuth()
initialize()
const sidebarOpen = ref(false)
</script>
