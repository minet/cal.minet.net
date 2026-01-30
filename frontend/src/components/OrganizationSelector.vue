<template>
  <div>
    <h3 class="text-sm font-medium text-gray-900 mb-4">{{ label }}</h3>
    
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="org in organizations"
        :key="org.id"
        @click="selectOrganization(org)"
        :class="[
          'relative flex cursor-pointer rounded-lg border p-4 shadow-sm focus:outline-none transition-all',
          isSelected(org.id)
            ? 'border-indigo-600 ring-2 ring-indigo-600 bg-indigo-50'
            : 'border-gray-300 hover:border-indigo-400 bg-white'
        ]"
      >
        <div class="flex flex-1">
          <div class="flex flex-col">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 h-10 w-10">
                <img 
                  v-if="org.logo_url" 
                  :src="org.logo_url" 
                  :alt="org.name" 
                  class="h-10 w-10 rounded-full object-cover bg-white"
                />
                <div 
                  v-else 
                  class="h-10 w-10 rounded-full flex items-center justify-center font-bold"
                  :style="{ 
                    backgroundColor: org.color_secondary || '#f0f9ff', 
                    color: org.color_primary || '#0369a1' 
                  }"
                >
                  <span class="text-sm">{{ org.name.charAt(0) }}</span>
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <span class="block text-sm font-medium text-gray-900 truncate">
                  {{ org.name }}
                </span>
                <span class="block text-xs text-gray-500 truncate">
                  {{ org.type }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div
          v-if="isSelected(org.id)"
          class="absolute top-2 right-2 flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600"
        >
          <CheckIcon class="h-3 w-3 text-white" />
        </div>
      </div>
    </div>
    
    <div v-if="organizations.length === 0" class="text-center py-12">
      <p class="text-sm text-gray-500">{{ emptyMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  organizations: {
    type: Array,
    required: true
  },
  modelValue: {
    type: [String, Array],
    default: null
  },
  label: {
    type: String,
    default: 'Sélectionner une organisation'
  },
  emptyMessage: {
    type: String,
    default: 'Aucune organisation disponible'
  },
  multiple: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedId = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  selectedId.value = newValue
})

const isSelected = (id) => {
  if (props.multiple) {
    return Array.isArray(selectedId.value) && selectedId.value.includes(id)
  }
  return selectedId.value === id
}

const selectOrganization = (org) => {
  if (props.multiple) {
    let newVal = Array.isArray(selectedId.value) ? [...selectedId.value] : []
    const index = newVal.indexOf(org.id)
    if (index === -1) {
      newVal.push(org.id)
    } else {
      newVal.splice(index, 1)
    }
    selectedId.value = newVal
    emit('update:modelValue', newVal)
  } else {
    selectedId.value = org.id
    emit('update:modelValue', org.id)
  }
}
</script>
