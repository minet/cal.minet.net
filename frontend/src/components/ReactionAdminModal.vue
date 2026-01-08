<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-50" @close="open = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button type="button" class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" @click="open = false">
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-indigo-100 sm:mx-0 sm:h-10 sm:w-10">
                  <FaceSmileIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left w-full">
                  <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Réactions</DialogTitle>
                  <div class="mt-2">
                    <p v-if="loading" class="text-sm text-gray-500">Chargement...</p>
                    <div v-else-if="reactions.length === 0" class="text-sm text-gray-500">Aucune réaction</div>
                    <ul v-else class="divide-y divide-gray-100 max-h-96 overflow-y-auto mt-4">
                      <li v-for="reaction in reactions" :key="reaction.user.id + reaction.emoji" class="flex items-center justify-between py-3">
                        <div class="flex items-center gap-3">
                          <UserAvatar :src="reaction.user.profile_picture_url" :name="reaction.user.full_name || reaction.user.email" size="sm" />
                          <div>
                            <p class="text-sm font-medium text-gray-900">{{ reaction.user.full_name }}</p>
                            <p class="text-xs text-gray-500">{{ formatDate(reaction.created_at) }}</p>
                          </div>
                        </div>
                        <div class="flex items-center gap-4">
                          <span class="text-2xl">{{ reaction.emoji }}</span>
                          <button 
                             @click="deleteReaction(reaction)"
                             class="text-red-400 hover:text-red-600 p-1 rounded-full hover:bg-red-50 transition-colors"
                             title="Supprimer la réaction"
                          >
                             <TrashIcon class="h-4 w-4" />
                          </button>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { FaceSmileIcon, XMarkIcon, TrashIcon } from '@heroicons/vue/24/outline'
import UserAvatar from './UserAvatar.vue'
import api from '../utils/api'

const props = defineProps({
  modelValue: Boolean,
  eventId: String
})

const emit = defineEmits(['update:modelValue', 'change'])

const open = ref(props.modelValue)
const reactions = ref([])
const loading = ref(false)

watch(() => props.modelValue, (val) => {
  open.value = val
  if (val) {
    loadReactions()
  }
})

watch(open, (val) => {
  emit('update:modelValue', val)
})

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
  })
}

const loadReactions = async () => {
  loading.value = true
  try {
    const response = await api.get(`/events/${props.eventId}/reactions`)
    reactions.value = response.data
  } catch (error) {
    console.error('Failed to load reactions:', error)
  } finally {
    loading.value = false
  }
}

const deleteReaction = async (reaction) => {
  if (!confirm(`Supprimer la réaction de ${reaction.user.full_name} ?`)) return
  
  try {
    await api.delete(`/events/${props.eventId}/reactions/${reaction.user.id}`)
    reactions.value = reactions.value.filter(r => r.user.id !== reaction.user.id)
    emit('change')
  } catch (error) {
    console.error('Failed to delete reaction:', error)
    alert('Impossible de supprimer la réaction')
  }
}
</script>
