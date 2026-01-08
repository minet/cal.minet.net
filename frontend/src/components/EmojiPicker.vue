<template>
  <div class="emoji-picker bg-white rounded-lg shadow-xl border border-gray-200 w-full max-w-xs flex flex-col h-80">
    <!-- Header: Search or Categories -->
    <div class="p-2 border-b border-gray-100 flex items-center justify-between">
      <input 
        v-model="searchQuery" 
        type="text" 
        placeholder="Rechercher un emoji..." 
        class="w-full text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
      >
    </div>

    <!-- Mobile Native Input Trigger -->
    <div class="sm:hidden px-2 py-1 border-b border-gray-100 flex justify-center">
       <button 
         @click="triggerNativePicker"
         class="text-xs bg-gray-100 hovering:bg-gray-200 text-gray-700 font-medium py-1 px-3 rounded-full flex items-center"
       >
         <span>⌨️ Utiliser le clavier</span>
       </button>
       <!-- Invisible input to trigger keyboard -->
       <input 
          ref="nativeInputRef"
          type="text" 
          class="opacity-0 absolute h-0 w-0"
          @input="handleNativeInput"
       >
    </div>

    <!-- Emoji Content -->
    <div class="flex-1 overflow-y-auto p-3 min-h-0 custom-scrollbar emoji-font">
      <div v-if="loading" class="flex justify-center items-center h-full">
        <span class="text-gray-400 text-sm">Chargement...</span>
      </div>
      
      <div v-else>
        <!-- Recent Emojis -->
        <div v-if="recentEmojis.length > 0 && !searchQuery" class="mb-4">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 pl-1">Récents</h3>
          <div class="grid grid-cols-6 gap-2">
            <button
              v-for="emoji in recentEmojis"
              :key="emoji"
              @click="selectEmoji(emoji)"
              class="hover:bg-gray-100 rounded-lg p-2 text-2xl leading-none flex items-center justify-center transition-colors aspect-square"
            >
              {{ emoji }}
            </button>
          </div>
        </div>

        <!-- Filtered/All Emojis -->
        <div v-if="filteredEmojis.length > 0">
           <h3 v-if="!searchQuery" class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 pl-1">Tous</h3>
           <div class="grid grid-cols-6 gap-2">
            <button
              v-for="emojiObj in visibleEmojis"
              :key="emojiObj.char"
              @click="selectEmoji(emojiObj.char)"
              class="hover:bg-gray-100 rounded-lg p-2 text-2xl leading-none flex items-center justify-center transition-colors aspect-square"
              :title="emojiObj.name"
            >
              {{ emojiObj.char }}
            </button>
          </div>
          <!-- Load More / Limit -->
          <div v-if="hasMoreEmojis" ref="loadMoreSentinel" class="h-4"></div>
        </div>
        
        <div v-else-if="searchQuery" class="text-center py-4 text-gray-500 text-sm">
          Aucun emoji trouvé
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'

const SOURCE = "https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json"

const emit = defineEmits(['select'])

const emojis = ref([])
const loading = ref(true)
const searchQuery = ref('')
const recentEmojis = ref([])
const page = ref(1)
const PAGE_SIZE = 100
const nativeInputRef = ref(null)

// Load recents from localstorage
const loadRecents = () => {
  const stored = localStorage.getItem('recent_emojis')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed)) {
          // Filter out invalid items (objects, long strings)
          recentEmojis.value = parsed.filter(e => typeof e === 'string' && !e.includes('{'))
      }
    } catch (e) {
      console.error('Failed to parse recent emojis', e)
    }
  }
}

const saveConfirmRecent = (emoji) => {
  let recents = [...recentEmojis.value]
  // Remove if exists
  recents = recents.filter(e => e !== emoji)
  // Add to front
  recents.unshift(emoji)
  // Limit to 16
  recents = recents.slice(0, 16)
  
  recentEmojis.value = recents
  localStorage.setItem('recent_emojis', JSON.stringify(recents))
}

const fetchEmojis = async () => {
  loading.value = true
  try {
    const response = await fetch(SOURCE)
    const data = await response.json()
    
    const rawEmojis = Array.isArray(data) ? data : (data.emojis || [])
    
    emojis.value = rawEmojis.map(e => {
        if (typeof e === 'string') {
            return { char: e, name: 'emoji' }
        }
        return {
            char: e.emoji || e.char || '',
            name: [e.description, ...(e.aliases || []), e.name].filter(Boolean).join(' ')
        }
    }).filter(e => e.char)
    
  } catch (error) {
    console.error('Failed to load emojis:', error)
  } finally {
    loading.value = false
  }
}

const filteredEmojis = computed(() => {
  if (!searchQuery.value) return emojis.value
  const query = searchQuery.value.toLowerCase()
  return emojis.value.filter(e => e.name.toLowerCase().includes(query))
})

const visibleEmojis = computed(() => {
  // Simple pagination/virtualization limit
  return filteredEmojis.value.slice(0, page.value * PAGE_SIZE)
})

const hasMoreEmojis = computed(() => {
  return visibleEmojis.value.length < filteredEmojis.value.length
})

const selectEmoji = (emoji) => {
  saveConfirmRecent(emoji)
  emit('select', emoji)
}

const handleNativeInput = (event) => {
  const val = event.target.value
  if (val) {
    // Try to detect emoji?
    // Ideally we assume user picked an emoji if they used the special keyboard.
    // But text input might send letters.
    // Check if it's an emoji roughly (regex) or just exact input.
    // Or just take the last char?
    // Usually native picker inserts the emoji.
    
    // reset input
    event.target.value = ''
    
    // Emit
    // Verify it's not empty string
    if (val.trim()) {
        const char = val.trim()
        selectEmoji(char)
    }
  }
}

const triggerNativePicker = () => {
    nativeInputRef.value?.focus()
    // On mobile, focus triggers keyboard.
}

// Intersection Observer for infinite scroll
const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting && hasMoreEmojis.value) {
    page.value++
  }
}, { rootMargin: '100px' })


watch(() => visibleEmojis.value.length, () => {
    // Re-bind observer if needed?
    // Actually we just need to observe the sentinel.
    nextTick(() => {
        const sentinel = document.querySelector('.emoji-picker .h-4') // Need better selector or ref
    })
})

onMounted(() => {
  loadRecents()
  fetchEmojis()
  
  // Setup observer
  const sentinel = document.querySelector('.emoji-picker .h-4') // This might not exist yet if loading
  // Better use ref in template
})

// Correct usage of sentinel ref
watch(() => loading.value, (newVal) => {
    if (!newVal) {
        nextTick(() => {
             // We need to access the ref after it renders
             // But template refs in filtered list are tricky if list is empty.
        })
    }
})

// Simple infinite scroll logic using scroll event might be safer than IntersectionObserver in this context if refs are unstable
// But let's try to bind observer to a ref element `loadMoreSentinel`.

const loadMoreSentinel = ref(null)

watch(loadMoreSentinel, (el) => {
    if (el) observer.observe(el)
})

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1; 
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #d1d5db; 
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #9ca3af; 
}

.emoji-font {
  font-family: "Noto Color Emoji", sans-serif;
}
</style>
