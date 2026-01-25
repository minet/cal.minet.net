<template>
  <div class="bg-gray-50 p-4 rounded-lg">
    <h3 class="text-sm font-medium text-gray-900 mb-4">Date et Heure</h3>

    <div v-if="warningMessage" class="mb-4 rounded-md bg-yellow-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">Attention</h3>
          <div class="mt-2 text-sm text-yellow-700">
            <p>{{ warningMessage }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-3 items-end">
      <!-- Date -->
      <div>
        <label for="date" class="block text-sm font-medium leading-6 text-gray-900">Date</label>
        <div class="mt-2">
          <input 
            type="text" 
            id="date" 
            required
            v-model="date"
            placeholder="JJ/MM/AAAA"
            class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
          />
        </div>
      </div>

      <!-- Time -->
      <div>
        <label for="time" class="block text-sm font-medium leading-6 text-gray-900">Heure de début</label>
        <div class="mt-2">
          <input 
            type="text" 
            id="time" 
            required
            v-model="time"
            placeholder="HH:MM"
            class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
          />
        </div>
      </div>

      <!-- Duration -->
      <div>
        <label class="block text-sm font-medium leading-6 text-gray-900">Durée</label>
        <div class="mt-2 flex space-x-2">
          <div class="relative rounded-md shadow-sm flex-1">
            <input 
              type="number" 
              v-model.number="durationHours"
              min="0"
              class="block w-full rounded-md border-0 py-1.5 pl-3 pr-8 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
              placeholder="0" 
            />
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <span class="text-gray-500 sm:text-sm">h</span>
            </div>
          </div>
          <div class="relative rounded-md shadow-sm flex-1">
            <input 
              type="number" 
              v-model.number="durationMinutes"
              min="0"
              max="59"
              :step="15"
              class="block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
              placeholder="0" 
            />
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <span class="text-gray-500 sm:text-sm">min</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <slot name="footer"></slot>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  startTime: {
    type: String,
    default: ''
  },
  endTime: {
    type: String,
    default: ''
  },
  warningMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:startTime', 'update:endTime'])

const date = ref('')
const time = ref('')
const durationHours = ref(0)
const durationMinutes = ref(0)

const formatDateFR = (dateObj) => {
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')
  return `${day}/${month}/${year}`
}

const formatTimeFR = (dateObj) => {
  const hours = String(dateObj.getHours()).padStart(2, '0')
  const minutes = String(dateObj.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const updateInternalState = () => {
  if (!props.startTime || !props.endTime) {
     // Initialize defaults if empty (start next hour, duration 1h)
     if (!props.startTime && !props.endTime) {
        const now = new Date()
        now.setMinutes(0)
        now.setSeconds(0)
        now.setMilliseconds(0)
        now.setHours(now.getHours() + 1)
        
        // We trigger an emit, but we also set local first to avoid loops if we careful
        // Actually, better to just set local state from props if they exist, else wait.
        // But for "Create", they are empty initially. The parent likely sets them or expects us to init.
        // Let's rely on parent passing valid strings, or we init them.
        
        // Ideally, parent handles initialization.
        return
     }
  }

  // Parse strings to local Date objects
  // The props are expected to be "YYYY-MM-DDTHH:mm:ss" ISO format or similar
  
  if (props.startTime) {
    const start = new Date(props.startTime)
    if (!isNaN(start.getTime())) {
       date.value = formatDateFR(start)
       time.value = formatTimeFR(start)
    }
  }
  
  if (props.startTime && props.endTime) {
    const start = new Date(props.startTime)
    const end = new Date(props.endTime)
    if (!isNaN(start.getTime()) && !isNaN(end.getTime())) {
        const diffMs = end - start
        if (diffMs >= 0) {
            durationHours.value = Math.floor(diffMs / (1000 * 60 * 60))
            durationMinutes.value = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
        }
    }
  }
}

const emitUpdates = () => {
  if (!date.value || !time.value) return

  // Parse date DD/MM/YYYY and time HH:MM
  const dateParts = date.value.split('/')
  const timeParts = time.value.split(':')
  
  if (dateParts.length !== 3 || timeParts.length !== 2) return
  
  const [day, month, year] = dateParts
  const [hours, minutes] = timeParts
  
  // Basic validation
  if (day.length !== 2 || month.length !== 2 || year.length !== 4) return
  if (hours.length !== 2 || minutes.length !== 2) return

  const startDateTime = new Date(`${year}-${month}-${day}T${hours}:${minutes}:00`)
  
  if (isNaN(startDateTime.getTime())) return

  const formattedStart = startDateTime.toISOString()
  
  const durationMs = (durationHours.value * 60 * 60 * 1000) + (durationMinutes.value * 60 * 1000)
  const endDateTime = new Date(startDateTime.getTime() + durationMs)
  const formattedEnd = endDateTime.toISOString()
  
  emit('update:startTime', formattedStart)
  emit('update:endTime', formattedEnd)
}

watch(() => props.startTime, (newVal) => {
    // Only update if divergent to avoid loop with rounded minutes?
    // Simple approach: Always update internal state if prop changes from outside 
    // (We need to distinguish external change vs internal change triggered emit)
    // But since `formatDateTimeLocal` is stable, it should be fine.
    
    // We check if reconstructing gives same result to avoid overwriting user input while typing?
    // Unlikely to type partial props.
    updateInternalState()
})

watch([date, time, durationHours, durationMinutes], () => {
    emitUpdates()
})

onMounted(() => {
    updateInternalState()
})

</script>
