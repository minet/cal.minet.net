<template>
  <div class="bg-gray-50 p-4 rounded-lg">
    <div class="flex items-center justify-between">
      <label class="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          :checked="enabled"
          @change="$emit('update:enabled', ($event.target as HTMLInputElement).checked)"
          class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
        />
        <span class="text-sm font-medium text-gray-900">Événement récurrent</span>
      </label>
    </div>

    <div v-if="enabled" class="mt-4 space-y-5">
      <p class="text-xs text-gray-500">
        L'événement sera recréé aux mêmes heures locales de début et de fin sur chaque jour sélectionné.
        Les heures affichées s'ajustent automatiquement aux changements d'heure été/hiver.
      </p>

      <!-- Weekday picker -->
      <div>
        <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">Jours de la semaine</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="day in weekdayOptions"
            :key="day.value"
            type="button"
            @click="toggleWeekday(day.value)"
            :class="[
              'h-9 w-9 rounded-full text-xs font-semibold transition-colors',
              weekdays.includes(day.value)
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-100'
            ]"
          >
            {{ day.label }}
          </button>
        </div>
      </div>

      <!-- End condition -->
      <div>
        <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">Fin de la récurrence</label>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <input
              type="radio"
              id="end-type-date"
              value="date"
              :checked="endType === 'date'"
              @change="$emit('update:endType', 'date')"
              class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600"
            />
            <label for="end-type-date" class="text-sm text-gray-700 whitespace-nowrap">Jusqu'au</label>
            <input
              type="date"
              :value="untilDate"
              @input="$emit('update:untilDate', ($event.target as HTMLInputElement).value)"
              @focus="$emit('update:endType', 'date')"
              class="block w-full max-w-[10rem] rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
          <div class="flex items-center gap-3">
            <input
              type="radio"
              id="end-type-count"
              value="count"
              :checked="endType === 'count'"
              @change="$emit('update:endType', 'count')"
              class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600"
            />
            <label for="end-type-count" class="text-sm text-gray-700 whitespace-nowrap">Nombre d'occurrences</label>
            <input
              type="number"
              min="1"
              :max="maxOccurrences"
              :value="count"
              @input="$emit('update:count', Number(($event.target as HTMLInputElement).value))"
              @focus="$emit('update:endType', 'count')"
              class="block w-24 rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>
      </div>

      <!-- Preview -->
      <div v-if="weekdays.length > 0">
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium leading-6 text-gray-900">
            Aperçu ({{ occurrences.length }} événement{{ occurrences.length > 1 ? 's' : '' }})
          </label>
          <p v-if="isCapped" class="text-xs text-orange-600">
            Limite de {{ maxOccurrences }} occurrences atteinte
          </p>
        </div>
        <div v-if="occurrences.length > 0" class="max-h-48 overflow-y-auto rounded-md border border-gray-200 divide-y divide-gray-100 bg-white">
          <div
            v-for="occ in occurrences"
            :key="occ.key"
            class="flex items-center justify-between px-3 py-1.5 text-sm text-gray-700"
          >
            <span class="capitalize">{{ formatOccurrence(occ.start) }}</span>
            <button
              type="button"
              @click="removeOccurrence(occ.key)"
              title="Retirer cette occurrence"
              class="text-gray-400 hover:text-red-600"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
        <p v-else class="text-xs text-gray-500">Aucune occurrence future avec ces paramètres.</p>

        <button
          v-if="skipDates.length > 0"
          type="button"
          @click="$emit('update:skipDates', [])"
          class="mt-2 text-xs text-indigo-600 hover:text-indigo-700"
        >
          Réinitialiser les occurrences retirées ({{ skipDates.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { computeRecurringOccurrences, MAX_RECURRING_OCCURRENCES } from '../utils/recurrence'

const props = defineProps<{
  enabled: boolean
  weekdays: number[]
  endType: 'date' | 'count'
  untilDate: string
  count: number
  skipDates: string[]
  startTime: string
  endTime: string
}>()

const emit = defineEmits<{
  'update:enabled': [boolean]
  'update:weekdays': [number[]]
  'update:endType': ['date' | 'count']
  'update:untilDate': [string]
  'update:count': [number]
  'update:skipDates': [string[]]
}>()

const maxOccurrences = MAX_RECURRING_OCCURRENCES

const weekdayOptions = [
  { value: 1, label: 'Lun' },
  { value: 2, label: 'Mar' },
  { value: 3, label: 'Mer' },
  { value: 4, label: 'Jeu' },
  { value: 5, label: 'Ven' },
  { value: 6, label: 'Sam' },
  { value: 0, label: 'Dim' },
]

const toggleWeekday = (value: number) => {
  const current = props.weekdays
  if (current.includes(value)) {
    emit('update:weekdays', current.filter(d => d !== value))
  } else {
    emit('update:weekdays', [...current, value].sort())
  }
}

const rawOccurrences = computed(() => {
  const start = new Date(props.startTime)
  const end = new Date(props.endTime)
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return []

  return computeRecurringOccurrences({
    startDate: start,
    endDate: end,
    weekdays: props.weekdays,
    until: props.endType === 'date' && props.untilDate ? new Date(`${props.untilDate}T23:59:59`) : null,
    count: props.endType === 'count' ? props.count : null,
  })
})

const occurrences = computed(() =>
  rawOccurrences.value.filter(occ => !props.skipDates.includes(occ.key)),
)

const isCapped = computed(() => rawOccurrences.value.length >= maxOccurrences)

const removeOccurrence = (key: string) => {
  emit('update:skipDates', [...props.skipDates, key])
}

const formatOccurrence = (d: Date) =>
  new Intl.DateTimeFormat('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' }).format(d)

defineExpose({ occurrences })
</script>
