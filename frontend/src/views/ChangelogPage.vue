<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900">Nouveautés</h1>
      <p class="mt-1 text-sm text-gray-500">Historique des mises à jour de l'application.</p>
    </div>

    <div v-if="loading" class="space-y-6">
      <div v-for="n in 3" :key="n" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-1/3 mb-3" />
        <div class="h-3 bg-gray-100 rounded w-full mb-2" />
        <div class="h-3 bg-gray-100 rounded w-5/6" />
      </div>
    </div>

    <div v-else-if="entries.length === 0" class="text-center py-16 text-gray-400">
      <MegaphoneIcon class="h-10 w-10 mx-auto mb-3 opacity-40" />
      <p class="text-sm">Aucune nouveauté pour le moment.</p>
    </div>

    <div v-else class="space-y-6">
      <article v-for="entry in entries" :key="entry.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-50 flex items-center justify-between">
          <h2 class="text-base font-semibold text-gray-900">{{ entry.title }}</h2>
          <time class="text-xs text-gray-400 shrink-0 ml-4">{{ formatDate(entry.created_at) }}</time>
        </div>
        <div class="px-6 py-4">
          <OrgDescriptionRenderer
            :description="entry.content"
            :allowed-image-urls="entry.image_urls ?? []"
            :members="[]"
          />
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MegaphoneIcon } from '@heroicons/vue/24/outline'
import OrgDescriptionRenderer from '@/components/OrgDescriptionRenderer.vue'
import { api } from '@/api'
import type { ChangelogEntryRead } from '@/api/types'

const entries = ref<ChangelogEntryRead[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    entries.value = await api.changelog.list()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}
</script>
