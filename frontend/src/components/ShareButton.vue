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
                                class="block w-full rounded-md border-0 py-1.5 pr-32 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(viewLink)" 
                              />
                               <div class="absolute right-1 top-1 bottom-1 flex gap-1">
                                <button 
                                    class="px-2.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded text-xs font-semibold transition-colors flex items-center"
                                    @click="openQrPreview('view')"
                                    title="QR Code"
                                >
                                    <QrCodeIcon class="h-4 w-4" />
                                </button>
                                <button 
                                    class="px-2.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                    @click="copy(viewLink)"
                                >
                                    <span v-if="copied === viewLink" class="flex items-center">
                                        <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                    </span>
                                    <span v-else>Copier</span>
                                </button>
                               </div>
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
                                class="block w-full rounded-md border-0 py-1.5 pr-32 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-purple-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(subscribeLink)" 
                              />
                               <div class="absolute right-1 top-1 bottom-1 flex gap-1">
                                <button 
                                    class="px-2.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded text-xs font-semibold transition-colors flex items-center"
                                    @click="openQrPreview('subscribe')"
                                    title="QR Code"
                                >
                                    <QrCodeIcon class="h-4 w-4" />
                                </button>
                                <button 
                                    class="px-2.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                    @click="copy(subscribeLink)"
                                >
                                    <span v-if="copied === subscribeLink" class="flex items-center">
                                        <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                    </span>
                                    <span v-else>Copier</span>
                                </button>
                               </div>
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
                                class="block w-full rounded-md border-0 py-1.5 pr-32 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-rose-600 sm:text-xs sm:leading-6 bg-white"
                                readonly 
                                @click="copy(countdownLink)" 
                              />
                               <div class="absolute right-1 top-1 bottom-1 flex gap-1">
                                <button 
                                    class="px-2.5 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded text-xs font-semibold transition-colors flex items-center"
                                    @click="openQrPreview('countdown')"
                                    title="QR Code"
                                >
                                    <QrCodeIcon class="h-4 w-4" />
                                </button>
                                <button 
                                    class="px-2.5 bg-rose-50 text-rose-700 hover:bg-rose-100 rounded text-xs font-semibold transition-colors flex items-center" 
                                    @click="copy(countdownLink)"
                                >
                                 <span v-if="copied === countdownLink" class="flex items-center">
                                    <CheckIcon class="h-3 w-3 mr-1" /> Copié
                                 </span>
                                 <span v-else>Copier</span>
                               </button>
                               </div>
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

    <!-- QR Preview Modal -->
    <TransitionRoot as="template" :show="qrPreviewOpen">
        <Dialog as="div" class="relative z-[60]" @close="closeQrPreview">
             <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
            </TransitionChild>

            <div class="fixed inset-0 z-10 overflow-y-auto">
                <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
                    <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
                        <DialogPanel class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-sm sm:p-6">
                             <div>
                                <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 mb-4">
                                    <QrCodeIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                                </div>
                                <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900 text-center mb-4">QR Code</DialogTitle>
                                
                                <div class="flex justify-center mb-4 p-4 bg-white rounded-xl border border-gray-100 shadow-inner overflow-hidden relative" style="width: 334px; height: 334px; margin: 0 auto;">
                                     <div style="width: 300px; height: 300px;" class="flex items-center justify-center overflow-hidden">
                                         <!-- Scale down the large canvas to fit 300px -->
                                         <QRCodeVue3
                                             ref="qrcodeComponent"
                                             v-bind="qrOptions"
                                             :key="`${includeLogo}-${monochrome}-${qrLinkUrl}-${qrResolution}-${qrFormat}-${qrDotType}`"
                                             style="max-width: 100%; max-height: 100%; height: auto !important; width: auto !important;"
                                         />
                                     </div>
                                </div>

                                <div class="space-y-4 mb-6">
                                     <!-- Toggles -->
                                    <div class="flex items-center justify-between gap-4">
                                        <SwitchGroup as="div" class="flex items-center">
                                            <Switch v-model="includeLogo" :disabled="!organization?.logo_url" :class="[includeLogo ? 'bg-indigo-600' : 'bg-gray-200', !organization?.logo_url ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2']">
                                                <span aria-hidden="true" :class="[includeLogo ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
                                            </Switch>
                                            <SwitchLabel as="span" class="ml-3 text-sm font-medium text-gray-900">Logo</SwitchLabel>
                                        </SwitchGroup>

                                        <SwitchGroup as="div" class="flex items-center">
                                            <Switch v-model="monochrome" :class="[monochrome ? 'bg-indigo-600' : 'bg-gray-200', 'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2']">
                                                <span aria-hidden="true" :class="[monochrome ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out']" />
                                            </Switch>
                                            <SwitchLabel as="span" class="ml-3 text-sm font-medium text-gray-900">Monochrome</SwitchLabel>
                                        </SwitchGroup>
                                    </div>
                                    
                                    <!-- Configuration Grid -->
                                    <div class="grid grid-cols-2 gap-4">
                                        
                                        <!-- Resolution -->
                                        <div>
                                            <Listbox v-model="qrResolution">
                                                <ListboxLabel class="block text-xs font-medium text-gray-700 mb-1">Résolution</ListboxLabel>
                                                <div class="relative">
                                                    <ListboxButton class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-xs sm:leading-6">
                                                        <span class="block truncate">{{ qrResolution }}px</span>
                                                        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                                                            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                                                        </span>
                                                    </ListboxButton>

                                                    <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
                                                        <ListboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                                            <ListboxOption as="template" v-for="res in [256, 512, 1024, 2048, 4096]" :key="res" :value="res" v-slot="{ active, selected }">
                                                                <li :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                                                                    <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">{{ res }}px</span>
                                                                    <span v-if="selected" :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                                                                        <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                                                    </span>
                                                                </li>
                                                            </ListboxOption>
                                                        </ListboxOptions>
                                                    </transition>
                                                </div>
                                            </Listbox>
                                        </div>

                                        <!-- Format -->
                                        <div>
                                            <Listbox v-model="qrFormat">
                                                <ListboxLabel class="block text-xs font-medium text-gray-700 mb-1">Format</ListboxLabel>
                                                <div class="relative">
                                                    <ListboxButton class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-xs sm:leading-6">
                                                        <span class="block truncate">{{ qrFormat.toUpperCase() }}</span>
                                                        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                                                        <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                                                        </span>
                                                    </ListboxButton>

                                                    <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
                                                        <ListboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                                            <ListboxOption as="template" v-for="fmt in ['png', 'jpeg', 'webp']" :key="fmt" :value="fmt" v-slot="{ active, selected }">
                                                                <li :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                                                                    <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">{{ fmt.toUpperCase() }}</span>
                                                                    <span v-if="selected" :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                                                                        <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                                                    </span>
                                                                </li>
                                                            </ListboxOption>
                                                        </ListboxOptions>
                                                    </transition>
                                                </div>
                                            </Listbox>
                                        </div>

                                        <!-- Style -->
                                        <div class="col-span-2">
                                             <Listbox v-model="qrDotType">
                                                <ListboxLabel class="block text-xs font-medium text-gray-700 mb-1">Style</ListboxLabel>
                                                <div class="relative">
                                                    <ListboxButton class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-600 sm:text-xs sm:leading-6">
                                                        <span class="block truncate">
                                                            {{ 
                                                                {
                                                                    'square': 'Carré',
                                                                    'dots': 'Points',
                                                                    'rounded': 'Arrondi',
                                                                    'classy': 'Classique',
                                                                    'classy-rounded': 'Classique Arrondi',
                                                                    'extra-rounded': 'Très Arrondi'
                                                                }[qrDotType] || qrDotType 
                                                            }}
                                                        </span>
                                                        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                                                            <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                                                        </span>
                                                    </ListboxButton>

                                                    <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100" leave-to-class="opacity-0">
                                                        <ListboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                                            <ListboxOption as="template" v-for="option in [
                                                                { value: 'square', label: 'Carré' },
                                                                { value: 'dots', label: 'Points' },
                                                                { value: 'rounded', label: 'Arrondi' },
                                                                { value: 'classy', label: 'Classique' },
                                                                { value: 'classy-rounded', label: 'Classique Arrondi' },
                                                                { value: 'extra-rounded', label: 'Très Arrondi' }
                                                            ]" :key="option.value" :value="option.value" v-slot="{ active, selected }">
                                                                <li :class="[active ? 'bg-indigo-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                                                                    <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">{{ option.label }}</span>
                                                                    <span v-if="selected" :class="[active ? 'text-white' : 'text-indigo-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                                                                        <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                                                    </span>
                                                                </li>
                                                            </ListboxOption>
                                                        </ListboxOptions>
                                                    </transition>
                                                </div>
                                            </Listbox>
                                        </div>
                                    </div>

                                </div>

                                <button 
                                    type="button" 
                                    class="inline-flex w-full justify-center items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                    @click="downloadQr"
                                >
                                    <ArrowDownTrayIcon class="h-5 w-5 mr-2" />
                                    Télécharger
                                </button>
                                

                             </div>
                             <div class="mt-5 sm:mt-6">
                                <button type="button" class="inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50" @click="closeQrPreview">
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
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot, Listbox, ListboxButton, ListboxLabel, ListboxOption, ListboxOptions, Switch, SwitchGroup, SwitchLabel } from '@headlessui/vue'
import { 
    ShareIcon, 
    XMarkIcon, 
    LinkIcon, 
    BellIcon, 
    ClockIcon, 
    CheckIcon,
    QrCodeIcon,
    ArrowDownTrayIcon,
    ChevronUpDownIcon
} from '@heroicons/vue/24/outline';
import QRCodeVue3 from 'qrcode-vue3';
import { computed } from 'vue';

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
    },
    organization: {
        type: Object,
        default: null
    },
    guestOrganizations: {
        type: Array,
        default: () => []
    }
});

const isOpen = ref(false);
const loading = ref(false);
const viewLink = ref(null);
const subscribeLink = ref(null);
const countdownLink = ref(null);
const copied = ref(null);

const qrPreviewOpen = ref(false);
const qrLinkType = ref(null); // 'view', 'subscribe', 'countdown'
const qrLinkUrl = ref(null);
const qrcodeComponent = ref(null);

const includeLogo = ref(true);
const monochrome = ref(false);
const qrResolution = ref(1024);
const qrFormat = ref('png');
const qrDotType = ref('square');

const openModal = () => {
    isOpen.value = true;
}

const closeModal = () => {
    isOpen.value = false;
}

const openQrPreview = async (type) => {
    qrLinkType.value = type;
    
    // Ensure link exists
    let url = null;
    if (type === 'view') url = viewLink.value;
    else if (type === 'subscribe') url = subscribeLink.value;
    else if (type === 'countdown') url = countdownLink.value;

    if (!url) {
        await generateLink(type);
        if (type === 'view') url = viewLink.value;
        else if (type === 'subscribe') url = subscribeLink.value;
        else if (type === 'countdown') url = countdownLink.value;
    }
    
    qrLinkUrl.value = url;
    qrPreviewOpen.value = true;
}

const closeQrPreview = () => {
    qrPreviewOpen.value = false;
}

const downloadQr = () => {
    const downloadButton = document.querySelector('.hidden-dl-btn');
    if (downloadButton) {
        downloadButton.click();
    } else {
        console.error('Download button not found');
    }
}

const qrOptions = computed(() => {
    const mainColor = monochrome.value 
        ? '#000000' 
        : (props.organization?.color_primary || '#4f46e5'); // Indigo default

    const guestColors = (props.guestOrganizations || []).map(g => 
        g.color_primary || '#4f46e5'
    );
    
    // Build gradient stops
    const colorStops = [{ offset: 0, color: mainColor }];
    if (!monochrome.value && guestColors.length > 0) {
        guestColors.forEach((c, i) => {
            colorStops.push({ offset: (i + 1) / (guestColors.length), color: c });
        });
    } else {
        colorStops.push({ offset: 1, color: mainColor });
    }

    return {
        width: qrResolution.value,
        height: qrResolution.value,
        value: qrLinkUrl.value,
        image: (includeLogo.value && props.organization?.logo_url) ? props.organization.logo_url : undefined,
        qrOptions: { typeNumber: 0, mode: 'Byte', errorCorrectionLevel: 'H' },
        imageOptions: { hideBackgroundDots: true, imageSize: 0.4, margin: 5 },
        dotsOptions: {
            type: qrDotType.value,
            color: mainColor,
            gradient: {
              type: 'linear',
              rotation: 45,
              colorStops: colorStops,
            },
        },
        backgroundOptions: { color: '#ffffff' },
        cornersSquareOptions: { type: qrDotType.value, color: mainColor },
        cornersDotOptions: { type: qrDotType.value, color: mainColor },
        download: true, // We keep this true so the lib prepares download capability
        downloadOptions: { name: 'qr_' + qrLinkType.value, extension: qrFormat.value },
        downloadButton: 'hidden-dl-btn' // Logic to hide default button
    }
});


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

<style>
.hidden-dl-btn {
    display: none !important;
}
</style>
