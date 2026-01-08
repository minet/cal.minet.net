<template>
  <div class="text-center">
    <div v-if="isPast" class="text-5xl md:text-7xl font-bold text-white">
      L'événement a commencé !
    </div>
    
    <div v-else class="grid grid-cols-4 gap-4 md:gap-8">
      <div v-for="(value, label) in timeUnits" :key="label" class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 md:p-8">
        <div class="text-5xl md:text-7xl font-bold text-white mb-2">
          {{ value }}
        </div>
        <div class="text-lg md:text-xl text-white/70 uppercase tracking-wider">
          {{ label }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  targetDate: {
    type: String,
    required: true
  }
})

const now = ref(new Date())
let intervalId = null

const targetDateTime = computed(() => new Date(props.targetDate))
const timeDiff = computed(() => targetDateTime.value - now.value)
const isPast = computed(() => timeDiff.value <= 0)

const timeUnits = computed(() => {
  if (isPast.value) {
    return { Jours: 0, Heures: 0, Minutes: 0, Secondes: 0 }
  }

  const diff = timeDiff.value
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  return {
    Jours: String(days).padStart(2, '0'),
    Heures: String(hours).padStart(2, '0'),
    Minutes: String(minutes).padStart(2, '0'),
    Secondes: String(seconds).padStart(2, '0')
  }
})

onMounted(() => {
  // Update every second
  intervalId = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>
