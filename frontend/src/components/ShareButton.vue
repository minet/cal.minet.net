<template>
  <div>
    <ActionPanelButton
        :block="block"
        :variant="variant"
        :icon="ShareIcon"
        @click="openModal"
    >
      Partager
    </ActionPanelButton>

    <TransitionRoot as="template" :show="isOpen">
      <Dialog as="div" class="relative z-50" @close="closeModal">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                    <ShareIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Partager</DialogTitle>
                    <div class="mt-4 space-y-4">
                      
                      <!-- View Link -->
                      <div v-if="itemType !== 'tag'" class="bg-gray-50 rounded-lg p-3 text-left border border-gray-100">
                           <div class="flex items-center justify-between mb-2">
                               <div class="flex items-center">
                                    <LinkIcon class="h-4 w-4 text-indigo-500 mr-2" />
                                    <span class="text-sm font-medium text-gray-900">Lien de consultation</span>
                               </div>
                           </div>
                           
                           <div v-if="viewLink" class="relative flex items-center">
                              <input 
                                type="text" 
                                :value="viewLink" 
                                class="block w-full rounded-md border-0 py-1.5 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(viewLink)" 
                              />
                               <button 
                                class="absolute right-1 top-1 bottom-1 px-2.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                @click="copy(viewLink)"
                              >
                                 <span v-if="copied === viewLink" class="flex items-center">
                                    <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                 </span>
                                 <span v-else>Copier</span>
                              </button>
                           </div>
                            <button v-else @click="generateLink('view')" class="mt-1 w-full flex items-center justify-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" :disabled="loading">
                                Générer
                            </button>
                      </div>

                      <!-- Subscribe Link -->
                      <div class="bg-gray-50 rounded-lg p-3 text-left border border-gray-100">
                           <div class="flex items-center justify-between mb-2">
                               <div class="flex items-center">
                                    <BellIcon class="h-4 w-4 text-purple-500 mr-2" />
                                    <span class="text-sm font-medium text-gray-900">S'abonner / Ajouter</span>
                               </div>
                           </div>
                           
                           <div v-if="subscribeLink" class="relative flex items-center">
                              <input 
                                type="text" 
                                :value="subscribeLink" 
                                class="block w-full rounded-md border-0 py-1.5 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(subscribeLink)" 
                              />
                               <button 
                                class="absolute right-1 top-1 bottom-1 px-2.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                @click="copy(subscribeLink)"
                              >
                                 <span v-if="copied === subscribeLink" class="flex items-center">
                                    <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                 </span>
                                 <span v-else>Copier</span>
                              </button>
                           </div>
                            <button v-else @click="generateLink('subscribe')" class="mt-1 w-full flex items-center justify-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-purple-700 bg-purple-100 hover:bg-purple-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500" :disabled="loading">
                                Générer
                            </button>
                      </div>

                      <!-- Countdown Link -->
                       <div v-if="itemType === 'event'" class="bg-gray-50 rounded-lg p-3 text-left border border-gray-100">
                           <div class="flex items-center justify-between mb-2">
                               <div class="flex items-center">
                                    <ClockIcon class="h-4 w-4 text-rose-500 mr-2" />
                                    <span class="text-sm font-medium text-gray-900">Compte à rebours</span>
                               </div>
                           </div>
                           
                           <div v-if="countdownLink" class="relative flex items-center">
                              <input 
                                type="text" 
                                :value="countdownLink" 
                                class="block w-full rounded-md border-0 py-1.5 pr-20 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-rose-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(countdownLink)" 
                              />
                               <button 
                                class="absolute right-1 top-1 bottom-1 px-2.5 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                @click="copy(countdownLink)"
                              >
                                 <span v-if="copied === countdownLink" class="flex items-center">
                                    <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                 </span>
                                 <span v-else>Copier</span>
                              </button>
                           </div>
                            <button v-else @click="generateLink('countdown')" class="mt-1 w-full flex items-center justify-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-rose-700 bg-rose-100 hover:bg-rose-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500" :disabled="loading">
                                Générer
                            </button>
                      </div>


                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6">
                  <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" @click="closeModal">
                    Fermer
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

<script setup>
import { ref } from 'vue';
import api from '../utils/api'; 
import ActionPanelButton from './ActionPanelButton.vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { 
    ShareIcon, 
    XMarkIcon, 
    LinkIcon, 
    BellIcon, 
    ClockIcon, 
    CheckIcon 
} from '@heroicons/vue/24/outline';

const props = defineProps({
    itemId: {
        type: String,
        required: true
    },
    itemType: {
        type: String,
        required: true // 'event', 'organization', 'tag'
    },
    block: {
        type: Boolean,
        default: false
    },
    variant: {
        type: String,
        default: 'default'
    }
});

const isOpen = ref(false);
const loading = ref(false);
const viewLink = ref(null);
const subscribeLink = ref(null);
const countdownLink = ref(null);
const copied = ref(null);

const openModal = () => {
    isOpen.value = true;
}

const closeModal = () => {
    isOpen.value = false;
}

const generateLink = async (actionType) => {
    loading.value = true;
    try {
        const response = await api.post('/short-links/', {
            item_type: props.itemType,
            item_id: props.itemId,
            action_type: actionType
        });
        
        if (actionType === 'view') viewLink.value = response.data.url;
        else if (actionType === 'subscribe') subscribeLink.value = response.data.url;
        else if (actionType === 'countdown') countdownLink.value = response.data.url;
        
    } catch (err) {
        console.error(err);
        alert("Erreur lors de la génération du lien.");
    } finally {
        loading.value = false;
    }
};

const copy = (text) => {
    navigator.clipboard.writeText(text);
    copied.value = text;
    setTimeout(() => {
        copied.value = null;
    }, 2000);
};

defineExpose({ openModal });
</script>
