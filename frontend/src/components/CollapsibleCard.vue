<template>
  <div class="border rounded-md bg-gray-50 flex flex-col">
    <button 
      type="button" 
      @click="toggle"
      class="flex items-center justify-between w-full p-4 text-left transition-colors hover:bg-gray-100 rounded-t-md focus:outline-none"
    >
      <div class="flex items-center gap-3 overflow-hidden">
        <span class="text-sm font-medium text-gray-900 truncate">{{ title }}</span>
        <div v-show="!isOpen" class="flex-shrink-0 transition-opacity duration-200">
             <slot name="summary"></slot>
        </div>
      </div>
      <span class="ml-4 flex-shrink-0">
         <ChevronDownIcon 
          class="h-5 w-5 text-gray-500 transition-transform duration-300 ease-in-out" 
          :class="{ 'rotate-180': isOpen }" 
        />
      </span>
    </button>
    
    <div 
      class="grid transition-[grid-template-rows] duration-300 ease-in-out"
      :class="isOpen ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
    >
      <div class="overflow-hidden">
        <div class="p-4 border-t border-gray-200">
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: undefined
  },
  defaultOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const internalIsOpen = ref(props.defaultOpen)

const isOpen = computed({
  get: () => props.modelValue !== undefined ? props.modelValue : internalIsOpen.value,
  set: (val) => {
    if (props.modelValue !== undefined) {
      emit('update:modelValue', val)
    } else {
      internalIsOpen.value = val
    }
  }
})

const toggle = () => {
  isOpen.value = !isOpen.value
}
</script>
