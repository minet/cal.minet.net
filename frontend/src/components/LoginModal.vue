<template>
  <div v-if="isOpen" class="relative z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity backdrop-blur-sm" @click="close"></div>
    <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <div class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6" @click.stop>
          <div>
            <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
              <UserIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
            </div>
            <div class="mt-3 text-center sm:mt-5">
              <h3 class="text-base font-semibold leading-6 text-gray-900" id="modal-title">
                {{ title }}
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  {{ description }}
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
            <button 
              type="button" 
              class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2" 
              @click="goToLogin"
            >
              Se connecter
            </button>
            <button 
              type="button" 
              class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0" 
              @click="close"
            >
              {{ cancelText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { UserIcon } from '@heroicons/vue/24/outline'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Connexion requise'
  },
  description: {
    type: String,
    default: 'Vous devez être connecté pour effectuer cette action.'
  },
  cancelText: {
    type: String,
    default: 'Annuler'
  }
})

const emit = defineEmits(['close'])

const router = useRouter()
const route = useRoute()

const close = () => {
  emit('close')
}

const goToLogin = () => {
  // Store redirect URL
  localStorage.setItem('auth_redirect_url', route.fullPath)
  router.push('/login')
}
</script>
