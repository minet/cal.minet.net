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
        <div class="mt-2 flex rounded-md shadow-sm">
          <div class="relative flex-grow focus-within:z-10">
            <input 
              type="date" 
              id="date" 
              ref="dateInput"
              required
              v-model="date"
              @click="openDatePicker"
              class="block w-full rounded-none rounded-l-md border-0 py-1.5 pl-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
            />
          </div>
          <button 
            type="button" 
            @click="openDatePicker"
            class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 hidden sm:block"
          >
            <CalendarIcon class="-ml-0.5 h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
        </div>
      </div>

      <!-- Time -->
      <div>
        <label for="time" class="block text-sm font-medium leading-6 text-gray-900">Heure de début</label>
        <div class="mt-2 flex rounded-md shadow-sm">
          <div class="relative flex-grow focus-within:z-10">
             <input 
              type="time" 
              id="time" 
              ref="timeInput"
              required
              v-model="time"
              @click="openTimePicker"
              class="block w-full rounded-none rounded-l-md border-0 py-1.5 pl-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
            />
          </div>
          <button 
            type="button"
            @click="openTimePicker" 
            class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 hidden sm:block"
          >
            <ClockIcon class="-ml-0.5 h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
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
import { ExclamationTriangleIcon, CalendarIcon, ClockIcon } from '@heroicons/vue/24/outline'

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
const dateInput = ref(null)
const timeInput = ref(null)

const openDatePicker = () => {
  if (dateInput.value && dateInput.value.showPicker) {
    dateInput.value.showPicker()
  }
}

const openTimePicker = () => {
  if (timeInput.value && timeInput.value.showPicker) {
    timeInput.value.showPicker()
  }
}

const updateInternalState = () => {
  if (!props.startTime && !props.endTime) {
     // Default initialization handled by parent usually, but if we wanted defaults:
     return
  }

  if (props.startTime) {
    const start = new Date(props.startTime)
    if (!isNaN(start.getTime())) {
       // Format to YYYY-MM-DD for input type="date"
       const year = start.getFullYear()
       const month = String(start.getMonth() + 1).padStart(2, '0')
       const day = String(start.getDate()).padStart(2, '0')
       date.value = `${year}-${month}-${day}`
       
       // Format to HH:MM for input type="time"
       const hours = String(start.getHours()).padStart(2, '0')
       const minutes = String(start.getMinutes()).padStart(2, '0')
       time.value = `${hours}:${minutes}`
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

  // date is YYYY-MM-DD, time is HH:MM
  const startDateTime = new Date(`${date.value}T${time.value}:00`)
  
  if (isNaN(startDateTime.getTime())) return

  const formattedStart = startDateTime.toISOString()
  
  const durationMs = (durationHours.value * 60 * 60 * 1000) + (durationMinutes.value * 60 * 1000)
  const endDateTime = new Date(startDateTime.getTime() + durationMs)
  const formattedEnd = endDateTime.toISOString()
  
  emit('update:startTime', formattedStart)
  emit('update:endTime', formattedEnd)
}

watch(() => props.startTime, () => {
    // Only update if external change? 
    // Ideally compare values, but simple re-sync for now
    updateInternalState()
})

watch([date, time, durationHours, durationMinutes], () => {
    emitUpdates()
})

onMounted(() => {
    updateInternalState()
})

</script>
