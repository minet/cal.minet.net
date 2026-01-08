<template>
  <div>
    <label v-if="label" :for="selectId" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <select
      :id="selectId"
      :value="stringValue"
      @change="handleChange"
      :required="required"
      :disabled="disabled"
      :class="[
        'block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6',
        error ? 'ring-red-300 focus:ring-red-500' : 'ring-gray-300 focus:ring-indigo-600',
        disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white'
      ]"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="getOptionKey(option)"
        :value="getOptionStringValue(option)"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    required: true,
    // Format: [{ value: 'val', label: 'Label', description: 'Optional description', disabled: false }]
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const selectId = computed(() => props.id || `select-${Math.random().toString(36).substr(2, 9)}`)

// Convert value to string for the select element
const stringValue = computed(() => {
  if (props.modelValue === null) return '__NULL__'
  if (props.modelValue === true) return '__TRUE__'
  if (props.modelValue === false) return '__FALSE__'
  return String(props.modelValue)
})

// Get string value for option
const getOptionStringValue = (option) => {
  if (option.value === null) return '__NULL__'
  if (option.value === true) return '__TRUE__'
  if (option.value === false) return '__FALSE__'
  return String(option.value)
}

const getOptionKey = (option) => {
  return getOptionStringValue(option)
}

// Convert string back to original type
const handleChange = (event) => {
  const stringVal = event.target.value
  
  if (stringVal === '__NULL__') {
    emit('update:modelValue', null)
    return
  }
  if (stringVal === '__TRUE__') {
    emit('update:modelValue', true)
    return
  }
  if (stringVal === '__FALSE__') {
    emit('update:modelValue', false)
    return
  }
  
  // Try to find the original value from options
  const option = props.options.find(opt => getOptionStringValue(opt) === stringVal)
  if (option) {
    emit('update:modelValue', option.value)
  } else {
    emit('update:modelValue', stringVal)
  }
}
</script>
