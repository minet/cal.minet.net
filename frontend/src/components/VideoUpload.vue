<template>
  <div class="space-y-4">
    <label class="block text-sm font-medium text-gray-900">
      {{ label }}
    </label>

    <!-- Preview existing video -->
    <div v-if="modelValue" class="relative inline-block">
      <video
        :src="modelValue"
        controls
        class="h-32 rounded-lg border-2 border-gray-300 max-w-xs"
      />
      <button
        @click="removeVideo"
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
        accept="video/mp4,video/webm,video/quicktime,video/avi,video/x-matroska"
        @change="handleFileChange"
        class="hidden"
      />

      <FilmIcon class="mx-auto h-12 w-12 text-gray-400" />
      <p class="mt-2 text-sm text-gray-600">
        <span class="text-indigo-600 font-medium">Cliquez pour uploader</span>
        ou glissez-déposez
      </p>
      <p class="text-xs text-gray-500 mt-1">MP4, WebM, MOV jusqu'à 100MB</p>
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
import { XMarkIcon, FilmIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  label: {
    type: String,
    default: 'Vidéo'
  }
})

const emit = defineEmits(['update:modelValue', 'update:storedFileId'])

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
  if (file) await uploadFile(file)
}

const handleDrop = async (event) => {
  dragover.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('video/')) {
    await uploadFile(file)
  } else {
    error.value = 'Veuillez déposer un fichier vidéo'
  }
}

const uploadFile = async (file) => {
  error.value = ''
  uploading.value = true
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/upload/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })

    emit('update:modelValue', response.data.url)
    emit('update:storedFileId', response.data.stored_file_id)
  } catch (err) {
    console.error('Upload failed:', err)
    error.value = err.response?.data?.detail || 'Échec de l\'upload'
  } finally {
    uploading.value = false
  }
}

const removeVideo = () => {
  emit('update:modelValue', null)
  emit('update:storedFileId', null)
  if (fileInput.value) fileInput.value.value = ''
}
</script>
