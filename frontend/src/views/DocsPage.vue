<template>
  <div class="max-w-3xl mx-auto">
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-gray-900">Documentation</h1>
      <p class="mt-1 text-sm text-gray-500">
        Guides pour prendre en main l'application. Seuls les guides correspondant à vos
        permissions sont affichés ici.
      </p>
    </div>

    <!-- Search -->
    <div class="mb-6">
      <input
        v-model="search"
        type="search"
        placeholder="Rechercher dans la documentation…"
        class="w-full rounded-lg border border-gray-200 px-4 py-2 text-sm focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
      />
    </div>

    <div v-if="!ready" class="space-y-4">
      <div v-for="n in 4" :key="n" class="h-20 rounded-xl bg-gray-100 animate-pulse"></div>
    </div>

    <div v-else-if="filteredGroups.length === 0" class="text-center py-16 text-gray-400">
      <BookOpenIcon class="h-10 w-10 mx-auto mb-3 text-gray-300" />
      <p>Aucun guide ne correspond à votre recherche.</p>
    </div>

    <div v-else class="space-y-8">
      <section v-for="group in filteredGroups" :key="group.category">
        <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          {{ group.category }}
        </h2>
        <div class="space-y-3">
          <router-link
            v-for="doc in group.docs"
            :key="doc.slug"
            :to="`/docs/${doc.slug}`"
            class="block bg-white rounded-xl shadow-sm border border-gray-100 px-5 py-4 hover:border-indigo-200 hover:shadow transition"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <h3 class="text-base font-semibold text-gray-900">{{ doc.title }}</h3>
                <p v-if="doc.summary" class="mt-1 text-sm text-gray-500">{{ doc.summary }}</p>
              </div>
              <ChevronRightIcon class="h-5 w-5 text-gray-300 shrink-0 mt-1" />
            </div>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="scopeBadgeClass(doc.scope)"
              >
                {{ scopeLabel(doc.scope) }}
              </span>
              <span
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="audienceBadgeClass(doc.audience)"
              >
                {{ audienceLabel(doc.audience) }}
              </span>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { BookOpenIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { useDocs, type Doc } from '@/composables/useDocs'
import {
  audienceBadgeClass,
  audienceLabel,
  scopeBadgeClass,
  scopeLabel,
} from '@/utils/docsAccess'

const { accessibleDocs, ensureMemberships, membershipsLoaded } = useDocs()

const search = ref('')
const ready = computed(() => membershipsLoaded.value)

interface DocGroup {
  category: string
  docs: Doc[]
}

const filteredGroups = computed<DocGroup[]>(() => {
  const q = search.value.trim().toLowerCase()
  const docs = accessibleDocs.value.filter((d) => {
    if (!q) return true
    return (
      d.title.toLowerCase().includes(q) ||
      d.summary.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q)
    )
  })
  const groups = new Map<string, Doc[]>()
  for (const doc of docs) {
    const list = groups.get(doc.category) ?? []
    list.push(doc)
    groups.set(doc.category, list)
  }
  return Array.from(groups.entries()).map(([category, items]) => ({ category, docs: items }))
})

onMounted(() => {
  ensureMemberships()
})
</script>
