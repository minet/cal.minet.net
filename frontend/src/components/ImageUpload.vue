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

    <!-- Crop Modal -->
    <TransitionRoot appear :show="showCropper" as="template">
      <Dialog as="div" @close="closeCropper" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  Ajuster l'image
                </DialogTitle>
                
                <div class="mt-2 h-96 bg-gray-100 rounded-lg overflow-hidden relative">
                   <Cropper
                      ref="cropper"
                      class="cropper"
                      background-class="cropper__background"
                      image-class="cropper__image"
                      area-class="cropper__area"
                      foreground-class="cropper__foreground"
                      :src="cropperImage"
                      :stencil-component="CircleStencil"
                      image-restriction="none"
                   />
                </div>

                <div class="mt-4 flex justify-end gap-3">
                  <button
                    type="button"
                    class="inline-flex justify-center rounded-md border border-transparent bg-gray-100 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gray-500 focus-visible:ring-offset-2"
                    @click="closeCropper"
                  >
                    Annuler
                  </button>
                  <button
                    type="button"
                    class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
                    @click="cropAndUpload"
                    :disabled="uploading"
                  >
                    {{ uploading ? 'Upload...' : 'Valider' }}
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>


<style>
.cropper {
  border: solid 1px #EEE;
  min-height: 300px;
  width: 100%;
}
.cropper__area {
    background: rgba(black, 1.0);
}

.cropper__background {
    background: #FFF;
}

.cropper__foreground {
    background: rgba(black, .0);
}
</style>

<script setup>
import { ref } from 'vue'
import { PhotoIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { Cropper, CircleStencil } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'
import api from '../utils/api'

const props = defineProps({
  modelValue: {
    type: String,
    default: null
  },
  label: {
    type: String,
    default: 'Image'
  },
  crop: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const dragover = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')

// Cropper state
const showCropper = ref(false)
const cropperImage = ref(null)
const currentFile = ref(null)
const cropper = ref(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (file) {
    if (props.crop) {
      openCropper(file)
    } else {
      await uploadFile(file)
    }
  }
}

const handleDrop = async (event) => {
  dragover.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    if (props.crop) {
      openCropper(file)
    } else {
      await uploadFile(file)
    }
  } else {
    error.value = 'Veuillez déposer un fichier image'
  }
}

const openCropper = (file) => {
  currentFile.value = file
  cropperImage.value = URL.createObjectURL(file)
  showCropper.value = true
}

const closeCropper = () => {
  showCropper.value = false
  if (cropperImage.value) {
    URL.revokeObjectURL(cropperImage.value)
    cropperImage.value = null
  }
  currentFile.value = null
  // Reset input just in case
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const cropAndUpload = async () => {
  if (!cropper.value) return
  
  const { canvas } = cropper.value.getResult()
  if (canvas) {
    canvas.toBlob(async (blob) => {
      if (blob) {
        // Create a new File object from the blob to preserve name/type if needed
        // or just pass blob. API expects multipart/form-data with 'file'.
        const fileToUpload = new File([blob], currentFile.value.name, { type: currentFile.value.type })
        await uploadFile(fileToUpload)
        closeCropper()
      }
    }, currentFile.value.type)
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
