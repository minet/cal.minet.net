<template>
  <div class="space-y-4">
    <label class="block text-sm font-medium text-gray-900">
      {{ label }}
    </label>
    
    <!-- Preview existing image -->
    <div v-if="modelValue" class="relative inline-block">
      <img 
        :src="modelValue" 
        alt="Preview" 
        class="h-32 w-32 object-cover rounded-lg border-2 border-gray-300"
      />
      <button 
        @click="removeImage"
        type="button"
        class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
      >
        <XMarkIcon class="h-4 w-4" />
      </button>
    </div>

    <!-- Upload area -->
    <div 
      v-else
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="handleDrop"
      :class="[
        'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
        dragover ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
      ]"
      @click="triggerFileInput"
    >
      <input 
        ref="fileInput"
        type="file" 
        accept="image/*"
        @change="handleFileChange"
        class="hidden"
      />
      
      <PhotoIcon class="mx-auto h-12 w-12 text-gray-400" />
      <p class="mt-2 text-sm text-gray-600">
        <span class="text-indigo-600 font-medium">Cliquez pour uploader</span>
        ou glissez-déposez
      </p>
      <p class="text-xs text-gray-500 mt-1">PNG, JPG, GIF jusqu'à 10MB</p>
    </div>

    <!-- Upload progress -->
    <div v-if="uploading" class="w-full">
      <div class="flex items-center space-x-2">
        <div class="flex-1 bg-gray-200 rounded-full h-2">
          <div class="bg-indigo-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${uploadProgress}%` }"></div>
        </div>
        <span class="text-sm text-gray-600">{{ uploadProgress }}%</span>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { PhotoIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  label: {
    type: String,
    default: 'Image'
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const dragover = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadFile(file)
  }
}

const handleDrop = async (event) => {
  dragover.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    await uploadFile(file)
  } else {
    error.value = 'Veuillez déposer un fichier image'
  }
}

const uploadFile = async (file) => {
  error.value = ''
  uploading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })

    emit('update:modelValue', response.data.url)
  } catch (err) {
    console.error('Upload failed:', err)
    error.value = err.response?.data?.detail || 'Échec de l\'upload'
  } finally {
    uploading.value = false
  }
}

const removeImage = () => {
  emit('update:modelValue', null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>
