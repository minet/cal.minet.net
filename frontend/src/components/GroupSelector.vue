<template>
  <div v-if="organizationId">
    <label class="block text-sm font-medium text-gray-700 mb-2">Groupe</label>
    <select
      :value="modelValue"
      @change="emit('update:modelValue', $event.target.value)"
      class="block w-full rounded-md border-0 py-2 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm"
    >
      <option value="">Sélectionnez un groupe</option>
      <option v-for="group in groups" :key="group.id" :value="group.id">
        {{ group.name }}
        <span v-if="group.member_count">({{ group.member_count }} membres)</span>
      </option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../utils/api'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  organizationId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const groups = ref([])

const loadGroups = async () => {
  if (!props.organizationId) {
    groups.value = []
    return
  }
  
  try {
    const response = await api.get(`/organizations/${props.organizationId}/groups`)
    groups.value = response.data
  } catch (error) {
    console.error('Failed to load groups:', error)
    groups.value = []
  }
}

watch(() => props.organizationId, () => {
  loadGroups()
  // Clear selected group when organization changes
  emit('update:modelValue', null)
})

onMounted(() => {
  loadGroups()
})
</script>
