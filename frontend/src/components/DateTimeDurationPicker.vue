<template>
  <div class="bg-gray-50 p-4 rounded-lg">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-medium text-gray-900">Date et Heure</h3>
      <button 
        v-if="isModified" 
        @click="revertChanges"
        type="button"
        class="inline-flex items-center gap-x-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-500"
      >
        <ArrowUturnLeftIcon class="h-3.5 w-3.5" />
        Rétablir
      </button>
    </div>

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

    <div class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-2 items-end">
      <!-- Start Date -->
      <div>
        <label for="date" class="block text-sm font-medium leading-6 text-gray-900">Date de début</label>
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

      <!-- Start Time -->
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

      <!-- End Date -->
      <div>
        <label for="endDate" class="block text-sm font-medium leading-6 text-gray-900">Date de fin</label>
        <div class="mt-2 flex rounded-md shadow-sm">
          <div class="relative flex-grow focus-within:z-10">
            <input 
              type="date" 
              id="endDate" 
              ref="endDateInput"
              required
              v-model="endDate"
              @click="openEndDatePicker"
              class="block w-full rounded-none rounded-l-md border-0 py-1.5 pl-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
            />
          </div>
          <button 
            type="button" 
            @click="openEndDatePicker"
            class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 hidden sm:block"
          >
            <CalendarIcon class="-ml-0.5 h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
        </div>
      </div>

      <!-- End Time -->
      <div>
        <label for="endTime" class="block text-sm font-medium leading-6 text-gray-900">Heure de fin</label>
        <div class="mt-2 flex rounded-md shadow-sm">
          <div class="relative flex-grow focus-within:z-10">
             <input 
              type="time" 
              id="endTime" 
              ref="endTimeInput"
              required
              v-model="endTimeVal"
              @click="openEndTimePicker"
              class="block w-full rounded-none rounded-l-md border-0 py-1.5 pl-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
            />
          </div>
          <button 
            type="button"
            @click="openEndTimePicker" 
            class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 hidden sm:block"
          >
            <ClockIcon class="-ml-0.5 h-5 w-5 text-gray-400" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
    
    <slot name="footer"></slot>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { ExclamationTriangleIcon, CalendarIcon, ClockIcon, ArrowUturnLeftIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  startTime: {
    type: String,
    default: ''
  },
  endTime: {
    type: String,
    default: ''
  },
  originalStartTime: {
    type: String,
    default: ''
  },
  originalEndTime: {
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
const endDate = ref('')
const endTimeVal = ref('')
const dateInput = ref(null)
const timeInput = ref(null)
const endDateInput = ref(null)
const endTimeInput = ref(null)

const isModified = computed(() => {
  if (!props.originalStartTime && !props.originalEndTime) return false
  
  const getTime = (val) => {
    if (!val) return 0
    // Try to handle simple string comparison if possible, but Date parsing is safer
    const d = new Date(val)
    return isNaN(d.getTime()) ? 0 : d.getTime()
  }

  const cStart = getTime(props.startTime)
  const oStart = getTime(props.originalStartTime)
  const cEnd = getTime(props.endTime)
  const oEnd = getTime(props.originalEndTime)
  
  // Allow small margin of error? No, strict equality for UI state
  return cStart !== oStart || cEnd !== oEnd
})

const revertChanges = () => {
    if (props.originalStartTime) {
        emit('update:startTime', props.originalStartTime)
    }
    if (props.originalEndTime) {
        emit('update:endTime', props.originalEndTime)
    }
}

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

const openEndDatePicker = () => {
  if (endDateInput.value && endDateInput.value.showPicker) {
    endDateInput.value.showPicker()
  }
}

const openEndTimePicker = () => {
  if (endTimeInput.value && endTimeInput.value.showPicker) {
    endTimeInput.value.showPicker()
  }
}

const formatDate = (d) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const formatTime = (d) => {
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const updateInternalState = () => {
  if (!props.startTime && !props.endTime) {
     return
  }

  let startObj = null
  if (props.startTime) {
    const start = new Date(props.startTime)
    if (!isNaN(start.getTime())) {
       startObj = start
       date.value = formatDate(start)
       time.value = formatTime(start)
    }
  }

  if (props.endTime) {
    const end = new Date(props.endTime)
    if (!isNaN(end.getTime())) {
        endDate.value = formatDate(end)
        endTimeVal.value = formatTime(end)
    }
  } else if (startObj) {
    // Default end time is start + 2 hours
    const defaultEnd = new Date(startObj.getTime() + 2 * 60 * 60 * 1000)
    endDate.value = formatDate(defaultEnd)
    endTimeVal.value = formatTime(defaultEnd)
  }
}

const emitUpdates = () => {
  if (!date.value || !time.value) return

  // date is YYYY-MM-DD, time is HH:MM
  const startDateTime = new Date(`${date.value}T${time.value}:00`)
  
  if (isNaN(startDateTime.getTime())) return

  const formattedStart = startDateTime.toISOString()
  
  if (endDate.value && endTimeVal.value) {
    const endDateTime = new Date(`${endDate.value}T${endTimeVal.value}:00`)
    if (!isNaN(endDateTime.getTime())) {
       const formattedEnd = endDateTime.toISOString()
       
       emit('update:startTime', formattedStart)
       emit('update:endTime', formattedEnd)
       return
    }
  }

  // If end date/time incomplete, just emit start? Or keep previous end?
  // User asked for 2h min, but if they are typing...
  emit('update:startTime', formattedStart)
}

// Watch changes to Start Date/Time to maintain duration
watch([date, time], ([newDate, newTime], [oldDate, oldTime]) => {
  if (!oldDate || !oldTime || !newDate || !newTime) {
     // If transitioning from empty to full, or vice versa
     // If we just set the start, and end is empty, set default 2h
     if (newDate && newTime && (!endDate.value || !endTimeVal.value)) {
        const start = new Date(`${newDate}T${newTime}:00`)
        if (!isNaN(start.getTime())) {
           const end = new Date(start.getTime() + 2 * 60 * 60 * 1000)
           endDate.value = formatDate(end)
           endTimeVal.value = formatTime(end)
        }
     }
  } else {
     // Calculate previous start and end to find duration
     const oldStart = new Date(`${oldDate}T${oldTime}:00`)
     const currentEndStr = `${endDate.value}T${endTimeVal.value}:00`
     const currentEnd = new Date(currentEndStr)
     
     if (!isNaN(oldStart.getTime()) && !isNaN(currentEnd.getTime())) {
        const duration = currentEnd.getTime() - oldStart.getTime()
        const newStart = new Date(`${newDate}T${newTime}:00`)
        if (!isNaN(newStart.getTime())) {
           const newEnd = new Date(newStart.getTime() + duration)
           endDate.value = formatDate(newEnd)
           endTimeVal.value = formatTime(newEnd)
        }
     }
  }
  emitUpdates()
})

// Watch changes to End Date/Time just to emit
watch([endDate, endTimeVal], () => {
  emitUpdates()
})

watch(() => props.startTime, () => {
   const start = new Date(props.startTime)
   if (!isNaN(start.getTime())) {
     const d = formatDate(start)
     const t = formatTime(start)
     if (d !== date.value || t !== time.value) {
        date.value = d
        time.value = t
     }
   }
})

watch(() => props.endTime, () => {
   const end = new Date(props.endTime)
   if (!isNaN(end.getTime())) {
     const d = formatDate(end)
     const t = formatTime(end)
     if (d !== endDate.value || t !== endTimeVal.value) {
        endDate.value = d
        endTimeVal.value = t
     }
   }
})

onMounted(() => {
    updateInternalState()
})

</script>
