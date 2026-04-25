<template>
  <!-- Desktop: Headless UI Dialog -->
  <TransitionRoot v-if="!isMobile" as="template" :show="modelValue">
    <Dialog as="div" class="relative z-50" @close="close">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 scale-95" enter-to="opacity-100 translate-y-0 scale-100"
            leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 scale-100"
            leave-to="opacity-0 translate-y-4 scale-95">
            <DialogPanel class="relative w-full max-w-lg transform rounded-2xl bg-white shadow-2xl transition-all">
              <!-- Header -->
              <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4">
                <div class="flex items-center gap-3">
                  <span class="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100">
                    <MegaphoneIcon class="h-4 w-4 text-indigo-600" />
                  </span>
                  <div>
                    <p class="text-xs font-medium text-indigo-600 uppercase tracking-wider">Nouveautés</p>
                    <DialogTitle as="h3" class="text-base font-semibold text-gray-900 leading-tight">
                      {{ current.title }}
                    </DialogTitle>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span v-if="changelogs.length > 1" class="text-xs text-gray-400">
                    {{ currentIndex + 1 }} / {{ changelogs.length }}
                  </span>
                  <button @click="close" class="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <!-- Content -->
              <div class="px-6 py-4 max-h-[60vh] overflow-y-auto">
                <p class="text-xs text-gray-400 mb-3">{{ formatDate(current.created_at) }}</p>
                <OrgDescriptionRenderer
                  :description="current.content"
                  :allowed-image-urls="current.image_urls ?? []"
                  :members="[]"
                />
              </div>

              <!-- Footer nav -->
              <div class="flex items-center justify-between border-t border-gray-100 px-6 py-4">
                <button v-if="currentIndex > 0" @click="prev"
                  class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors">
                  <ChevronLeftIcon class="h-4 w-4" />
                  Précédent
                </button>
                <div v-else />

                <button v-if="currentIndex < changelogs.length - 1" @click="next"
                  class="flex items-center gap-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
                  Suivant
                  <ChevronRightIcon class="h-4 w-4" />
                </button>
                <button v-else @click="close"
                  class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
                  Fermer
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Mobile: Bottom Drawer -->
  <Teleport v-else to="body">
    <Transition enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-full opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-full opacity-0">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex flex-col justify-end">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="close" />
        <div class="relative rounded-t-2xl bg-white shadow-2xl max-h-[82vh] flex flex-col">
          <!-- Drag handle -->
          <div class="flex justify-center pt-3 pb-1">
            <div class="h-1 w-10 rounded-full bg-gray-300" />
          </div>

          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
            <div class="flex items-center gap-2">
              <span class="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100">
                <MegaphoneIcon class="h-3.5 w-3.5 text-indigo-600" />
              </span>
              <div>
                <p class="text-xs font-medium text-indigo-600 uppercase tracking-wider">Nouveautés</p>
                <h3 class="text-sm font-semibold text-gray-900 leading-tight">{{ current.title }}</h3>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="changelogs.length > 1" class="text-xs text-gray-400">
                {{ currentIndex + 1 }} / {{ changelogs.length }}
              </span>
              <button @click="close" class="rounded-full p-1 text-gray-400 hover:bg-gray-100 transition-colors">
                <XMarkIcon class="h-5 w-5" />
              </button>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto px-5 py-4">
            <p class="text-xs text-gray-400 mb-3">{{ formatDate(current.created_at) }}</p>
            <OrgDescriptionRenderer
              :description="current.content"
              :allowed-image-urls="current.image_urls ?? []"
              :members="[]"
            />
          </div>

          <!-- Footer nav -->
          <div class="flex items-center justify-between border-t border-gray-100 px-5 py-4 pb-safe">
            <button v-if="currentIndex > 0" @click="prev"
              class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors">
              <ChevronLeftIcon class="h-4 w-4" />
              Précédent
            </button>
            <div v-else />

            <button v-if="currentIndex < changelogs.length - 1" @click="next"
              class="flex items-center gap-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
              Suivant
              <ChevronRightIcon class="h-4 w-4" />
            </button>
            <button v-else @click="close"
              class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 transition-colors">
              Fermer
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, ChevronLeftIcon, ChevronRightIcon, MegaphoneIcon } from '@heroicons/vue/24/outline'
import OrgDescriptionRenderer from './OrgDescriptionRenderer.vue'
import type { ChangelogEntryRead } from '@/api/types'

const props = defineProps<{
  changelogs: ChangelogEntryRead[]
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'all-seen', lastId: string): void
}>()

const currentIndex = ref(0)
const isMobile = ref(window.innerWidth < 1024)

const current = computed(() => props.changelogs[currentIndex.value])

function updateMobile() {
  isMobile.value = window.innerWidth < 1024
}

onMounted(() => window.addEventListener('resize', updateMobile))
onUnmounted(() => window.removeEventListener('resize', updateMobile))

watch(() => props.modelValue, (val) => {
  if (val) currentIndex.value = 0
})

function prev() {
  if (currentIndex.value > 0) currentIndex.value--
}

function next() {
  if (currentIndex.value < props.changelogs.length - 1) currentIndex.value++
}

function close() {
  const lastId = props.changelogs[props.changelogs.length - 1]?.id
  emit('update:modelValue', false)
  if (lastId) emit('all-seen', lastId)
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}
</script>
