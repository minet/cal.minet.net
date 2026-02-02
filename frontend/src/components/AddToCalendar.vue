<template>
  <div>
    <button
      @click="isOpen = true"
      class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      <CalendarIcon class="h-5 w-5 mr-2" />
      S'abonner au calendrier
    </button>

    <TransitionRoot appear :show="isOpen" as="template">
      <Dialog as="div" @close="closeModal" class="relative z-50">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/25 backdrop-blur-sm" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div
            class="flex min-h-full items-center justify-center p-4 text-center"
          >
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel
                class="w-full max-w-lg transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all"
              >
                <DialogTitle
                  as="h3"
                  class="text-lg font-medium leading-6 text-gray-900 flex justify-between items-center mb-4"
                >
                  <span>Ajouter au calendrier</span>
                  <button
                    @click="closeModal"
                    class="rounded-full p-1 hover:bg-gray-100 transition-colors"
                  >
                    <XMarkIcon class="h-5 w-5 text-gray-500" />
                  </button>
                </DialogTitle>
                
                <div class="space-y-3">
                  <!-- Apple Calendar -->
                  <a :href="appleCalendarUrl" class="group flex items-start p-3 rounded-lg hover:bg-gray-50 border border-gray-200 hover:border-indigo-300 transition-all cursor-pointer">
                    <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-gray-100 text-gray-900 group-hover:bg-white group-hover:shadow-sm">
                      <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.74 1.18 0 2.21-.93 3.23-.93 1.55 0 2.68.56 3.13 1.23-.74.63-1.61 1.63-1.61 3.59 0 3.06 2.53 4.29 2.53 4.29-.08.34-.58 1.9-1.36 3.05zm-4.04-16.1c.64-1.08 1.4-1.89 2.68-2.18.23 1.41-.47 2.8-1.36 3.73-.78.8-2.1 1.45-3.32 1.3-.12-1.36.81-2.24 2-2.85z"/>
                      </svg>
                    </div>
                    <div class="ml-4 flex-1">
                      <h4 class="text-sm font-medium text-gray-900">Apple Calendar</h4>
                      <p class="text-xs text-gray-500 mt-0.5">iPhone, iPad, Mac</p>
                    </div>
                  </a>

                  <!-- Google Calendar -->
                  <a :href="googleCalendarUrl" target="_blank" class="group flex items-start p-3 rounded-lg hover:bg-gray-50 border border-gray-200 hover:border-indigo-300 transition-all cursor-pointer">
                    <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-white border border-gray-100 group-hover:shadow-sm">
                      <GoogleIcon class="h-6 w-6" />
                    </div>
                    <div class="ml-4 flex-1">
                      <h4 class="text-sm font-medium text-gray-900">Google Calendar</h4>
                      <p class="text-xs text-gray-500 mt-0.5">Android, Web Desktop</p>
                    </div>
                  </a>

                  <!-- Autre application (Webcal) -->
                  <a :href="appleCalendarUrl" class="group flex items-start p-3 rounded-lg hover:bg-gray-50 border border-gray-200 hover:border-indigo-300 transition-all cursor-pointer">
                    <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-gray-50 text-gray-500 group-hover:bg-white group-hover:shadow-sm">
                      <CalendarIcon class="h-6 w-6" />
                    </div>
                    <div class="ml-4 flex-1">
                      <h4 class="text-sm font-medium text-gray-900">Autre application</h4>
                      <p class="text-xs text-gray-500 mt-0.5">Ouvrir dans l'application par défaut</p>
                    </div>
                  </a>
                </div>

                <!-- Generic / Manual Copy Section -->
                <div class="mt-6 pt-4 border-t border-gray-100">
                  <h4 class="text-sm font-medium text-gray-900 mb-2">Ou copier le lien manuellement</h4>
                  <div class="flex items-center gap-2">
                      <input 
                      type="text" 
                      :value="url" 
                      readonly 
                      class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 bg-gray-50 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                      />
                      <button 
                      @click="copyUrl"
                      class="whitespace-nowrap inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-indigo-600 shadow-sm ring-1 ring-inset ring-indigo-200 hover:bg-indigo-50"
                      >
                        <span v-if="copied">Copié!</span>
                        <span v-else>Copier le lien ICS</span>
                      </button>
                  </div>
                  <p class="mt-2 text-xs text-gray-500">
                    Collez ce lien dans votre logiciel de calendrier (Outlook, Thunderbird, etc.)
                  </p>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'
import { CalendarIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import GoogleIcon from './GoogleIcon.vue'

const props = defineProps({
  url: {
    type: String,
    required: true
  },
  calendarName: {
    type: String,
    default: 'MiNET Calendar'
  }
})

const isOpen = ref(false)
const copied = ref(false)

const closeModal = () => {
  isOpen.value = false
}

const copyUrl = () => {
  navigator.clipboard.writeText(props.url)
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

// 1. Apple Calendar (webcal protocol)
const appleCalendarUrl = computed(() => {
  if (!props.url) return '#'
  return props.url.replace(/^https?:\/\//, 'webcal://')
})

// 2. Google Calendar
const googleCalendarUrl = computed(() => {
  if (!props.url) return '#'
  const cid = encodeURIComponent(props.url.replace(/^https?:\/\//, 'webcal://'))
  return `https://www.google.com/calendar/render?cid=${cid}`
})

defineExpose({
  open: () => {
    isOpen.value = true
  }
})

</script>
