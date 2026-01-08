<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="tag in availableTags"
        :key="tag.id"
        type="button"
        @click="toggleTag(tag.id)"
        :class="[
          'inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-all',
          isSelected(tag.id) 
            ? 'border-current shadow-sm' 
            : 'border-gray-200 hover:border-gray-300'
        ]"
        :style="getTagStyle(tag)"
      >
        <span v-if="isSelected(tag.id)" class="mr-1.5">✓</span>
        {{ tag.name }}
      </button>
      <p v-if="availableTags.length === 0" class="text-sm text-gray-500">
        Aucun tag disponible pour cette organisation
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../utils/api'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  organizationId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const availableTags = ref([])

const loadTags = async () => {
  if (!props.organizationId) {
    availableTags.value = []
    return
  }
  
  try {
    const response = await api.get(`/organizations/${props.organizationId}/tags`)
    availableTags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
    availableTags.value = []
  }
}

const isSelected = (tagId) => {
  return props.modelValue.includes(tagId)
}

const toggleTag = (tagId) => {
  const newValue = isSelected(tagId)
    ? props.modelValue.filter(id => id !== tagId)
    : [...props.modelValue, tagId]
  
  emit('update:modelValue', newValue)
}

const getTagStyle = (tag) => {
  const isActive = isSelected(tag.id)
  return {
    backgroundColor: isActive ? tag.color + '30' : 'transparent',
    color: isActive ? darkenColor(tag.color) : '#6B7280',
    borderColor: isActive ? tag.color : '#E5E7EB'
  }
}

const darkenColor = (color) => {
  try {
    const hex = color.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16)
    const g = parseInt(hex.substr(2, 2), 16)
    const b = parseInt(hex.substr(4, 2), 16)
    
    const factor = 0.7
    return `rgb(${Math.floor(r * factor)}, ${Math.floor(g * factor)}, ${Math.floor(b * factor)})`
  } catch {
    return color
  }
}

watch(() => props.organizationId, () => {
  loadTags()
  // Clear selected tags when organization changes
  emit('update:modelValue', [])
})

onMounted(() => {
  loadTags()
})
</script>
