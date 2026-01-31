<template>
  <div class="flex flex-wrap items-center gap-2" v-if="btnAdd || sortedReactions.length > 0">
    <!-- Existing Reactions -->
    <button
      v-for="reaction in sortedReactions"
      :key="reaction.emoji"
      @click="toggleReaction(reaction.emoji)"
      :class="[
        'inline-flex items-center px-2 py-1 rounded-full text-sm font-medium border transition-colors',
        reaction.user_reacted 
          ? 'bg-indigo-100 border-indigo-200 text-indigo-800 hover:bg-indigo-200' 
          : 'bg-gray-100 border-gray-200 text-gray-700 hover:bg-gray-200'
      ]"
      :title="reaction.user_reacted ? 'Cliquez pour retirer votre réaction' : 'Cliquez pour ajouter cette réaction'"
    >
      <span class="mr-1">{{ reaction.emoji }}</span>
      <span class="text-xs">{{ reaction.count }}</span>
    </button>

    <!-- Add Reaction Button -->
    <div v-if="btnAdd && !hasUserReacted" class="relative" ref="pickerContainer">
      <button
        @click="showPicker = !showPicker"
        class="inline-flex items-center justify-center h-7 w-7 rounded-full bg-gray-50 border border-gray-200 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
        title="Ajouter une réaction"
      >
        <PlusIcon class="h-4 w-4" />
      </button>

      <!-- Emoji Picker Popover -->
      <div 
        v-if="showPicker" 
        class="absolute z-50 left-0 mt-2 w-80 transform -translate-x-1/4 sm:translate-x-0"
      >
        <!-- Overlay to close on click outside -->
        <div class="fixed inset-0 z-40" @click="showPicker = false"></div>
        
        <div class="relative z-50">
            <EmojiPicker @select="onEmojiSelect" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import EmojiPicker from './EmojiPicker.vue'
import api from '../utils/api'

import { askPermissionAndSubscribe } from '../utils/push'

const props = defineProps({
  eventId: {
    type: String,
    required: true
  },
  reactions: {
    type: Array,
    default: () => []
  },
  btnAdd: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update'])

const showPicker = ref(false)
const loading = ref(false)

const sortedReactions = computed(() => {
  // Sort by count desc, then alphabetically
  return [...props.reactions].sort((a, b) => b.count - a.count || a.emoji.localeCompare(b.emoji))
})

const hasUserReacted = computed(() => {
  return props.reactions.some(r => r.user_reacted)
})

const toggleReaction = async (emoji) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const response = await api.post(`/events/${props.eventId}/react`, { emoji })
    emit('update')
    
    // Check if added (message says "Reaction added")
    if (response.data.message === "Reaction added" || response.data.message === "Reaction updated") {
        askPermissionAndSubscribe()
    }
  } catch (error) {
    console.error('Failed to react:', error)
  } finally {
    loading.value = false
    showPicker.value = false
  }
}

const onEmojiSelect = (emoji) => {
  toggleReaction(emoji)
}
</script>
