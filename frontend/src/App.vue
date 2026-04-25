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
        <div v-else-if="$route.name !== 'Feed' && $route.name !== 'Login'" class="sticky top-0 z-40 flex h-16 items-center justify-end gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:px-6">
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

    <!-- Changelog viewer — shown once per session for unseen entries -->
    <ChangelogViewer
      v-if="unseenChangelogs.length > 0"
      :changelogs="unseenChangelogs"
      v-model="showChangelog"
      @all-seen="onChangelogSeen"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAuth } from './composables/useAuth'
import Sidebar from './components/Sidebar.vue'
import ChangelogViewer from './components/ChangelogViewer.vue'
import { Bars3Icon } from '@heroicons/vue/24/outline'
import { api } from './api'
import { type ChangelogEntryRead } from './api/types'

const { isAuthenticated, initialize } = useAuth()
initialize()
const sidebarOpen = ref(false)

const unseenChangelogs = ref<ChangelogEntryRead[]>([])
const showChangelog = ref(false)

watch(isAuthenticated, async (val) => {
  if (val) {
    try {
      unseenChangelogs.value = await api.changelog.listUnseen()
      if (unseenChangelogs.value.length > 0) {
        showChangelog.value = true
      }
    } catch (_e) {
      // Fail silently — changelog is non-critical
    }
  }
}, { immediate: true })

async function onChangelogSeen(lastId: string) {
  unseenChangelogs.value = []
  try {
    await api.changelog.markSeen(lastId)
  } catch (_e) {
    // Fail silently
  }
}
</script>
