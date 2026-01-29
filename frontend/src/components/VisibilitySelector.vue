<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-3">Visibilité de l'événement</label>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Draft Card -->
      <button
        type="button"
        @click="selectVisibility('draft')"
        :class="[
          'relative flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-200',
          visibility === 'draft'
            ? 'border-amber-500 bg-gradient-to-br from-amber-50 to-orange-50 shadow-lg shadow-amber-100'
            : 'border-gray-200 hover:border-amber-300 hover:shadow-md bg-white'
        ]"
      >
        <div :class="[
          'flex h-14 w-14 items-center justify-center rounded-xl mb-3 transition-all duration-200',
          visibility === 'draft' 
            ? 'bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg' 
            : 'bg-gray-100'
        ]">
          <DocumentTextIcon :class="[
            'h-7 w-7',
            visibility === 'draft' ? 'text-white' : 'text-gray-500'
          ]" />
        </div>
        <h3 :class="[
          'text-sm font-semibold mb-1',
          visibility === 'draft' ? 'text-amber-900' : 'text-gray-900'
        ]">
          Brouillon
        </h3>
        <p class="text-xs text-gray-500 text-center leading-relaxed">
          Visible uniquement par les membres de l'organisation
        </p>
        <div v-if="visibility === 'draft'" class="absolute top-3 right-3">
          <CheckCircleIcon class="h-5 w-5 text-amber-500" />
        </div>
      </button>

      <!-- Private Card -->
      <button
        type="button"
        @click="selectVisibility('private')"
        :class="[
          'relative flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-200',
          visibility === 'private'
            ? 'border-violet-500 bg-gradient-to-br from-violet-50 to-purple-50 shadow-lg shadow-violet-100'
            : 'border-gray-200 hover:border-violet-300 hover:shadow-md bg-white'
        ]"
      >
        <div :class="[
          'flex h-14 w-14 items-center justify-center rounded-xl mb-3 transition-all duration-200',
          visibility === 'private' 
            ? 'bg-gradient-to-br from-violet-500 to-purple-500 shadow-lg' 
            : 'bg-gray-100'
        ]">
          <LockClosedIcon :class="[
            'h-7 w-7',
            visibility === 'private' ? 'text-white' : 'text-gray-500'
          ]" />
        </div>
        <h3 :class="[
          'text-sm font-semibold mb-1',
          visibility === 'private' ? 'text-violet-900' : 'text-gray-900'
        ]">
          Privé
        </h3>
        <p class="text-xs text-gray-500 text-center leading-relaxed">
          Visible uniquement par les membres du groupe sélectionné et les admins de l'organisation
        </p>
        <div v-if="visibility === 'private'" class="absolute top-3 right-3">
          <CheckCircleIcon class="h-5 w-5 text-violet-500" />
        </div>
      </button>

      <!-- Public Card -->
      <button
        type="button"
        @click="selectVisibility('public_pending')"
        :class="[
          'relative flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-200',
          isPublic
            ? 'border-emerald-500 bg-gradient-to-br from-emerald-50 to-teal-50 shadow-lg shadow-emerald-100'
            : 'border-gray-200 hover:border-emerald-300 hover:shadow-md bg-white'
        ]"
      >
        <div :class="[
          'flex h-14 w-14 items-center justify-center rounded-xl mb-3 transition-all duration-200',
          isPublic 
            ? 'bg-gradient-to-br from-emerald-500 to-teal-500 shadow-lg' 
            : 'bg-gray-100'
        ]">
          <GlobeAltIcon :class="[
            'h-7 w-7',
            isPublic ? 'text-white' : 'text-gray-500'
          ]" />
        </div>
        <h3 :class="[
          'text-sm font-semibold mb-1',
          isPublic ? 'text-emerald-900' : 'text-gray-900'
        ]">
          Public
        </h3>
        <p class="text-xs text-gray-500 text-center leading-relaxed">
          Visible par tous les utilisateurs (nécessite approbation)
        </p>
        <div v-if="isPublic" class="absolute top-3 right-3">
          <CheckCircleIcon class="h-5 w-5 text-emerald-500" />
        </div>
      </button>
    </div>

    <!-- Approval Notice (shown for public pending) -->
    <div v-if="isPending" class="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <ClockIcon class="h-5 w-5 text-blue-500 mt-0.5" />
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-blue-900">Approbation requise</h4>
          <p class="text-xs text-blue-700 mt-1">
            Les événements publics doivent être approuvés par le BDE et l'administration. Une fois approuvé, les dates seront verrouillées. Les évenements publics approuvés seront ajoutés au menu de la semaine et au calendrier associatif.
          </p>
        </div>
      </div>
    </div>

    <!-- Approved Badge -->
    <div v-if="isApproved" class="mt-4 p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-200">
      <div class="flex items-center gap-3">
        <div class="flex-shrink-0">
          <CheckBadgeIcon class="h-5 w-5 text-emerald-500" />
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-emerald-900">Approuvé</h4>
          <p class="text-xs text-emerald-700 mt-1">
            Cet événement a été approuvé. Les dates ne peuvent plus être modifiées.
          </p>
        </div>
      </div>
    </div>

    <!-- Rejected Notice -->
    <div v-if="isRejected" class="mt-4 p-4 bg-gradient-to-r from-red-50 to-rose-50 rounded-xl border border-red-200">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0">
          <ExclamationCircleIcon class="h-5 w-5 text-red-500 mt-0.5" />
        </div>
        <div class="flex-1">
          <h4 class="text-sm font-medium text-red-900">Refusé</h4>
          <p v-if="rejectionMessage" class="text-xs text-red-700 mt-1">
            {{ rejectionMessage }}
          </p>
          <p class="text-xs text-red-600 mt-2">
            Vous pouvez modifier l'événement et le soumettre à nouveau.
          </p>
        </div>
      </div>
    </div>

    <!-- Hide Details Toggle (shown for public visibility) -->
    <div v-if="isPublic" class="mt-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h4 class="text-sm font-medium text-gray-900">Masquer les détails</h4>
          <p class="text-xs text-gray-500 mt-1">
            Seuls le titre, les dates et l'organisation seront visibles aux non-membres
          </p>
        </div>
        <button
          type="button"
          @click.stop="toggleHideDetails"
          :class="[
            'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2',
            hideDetails ? 'bg-emerald-500' : 'bg-gray-200'
          ]"
        >
          <span :class="[
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
            hideDetails ? 'translate-x-5' : 'translate-x-0'
          ]" />
        </button>
      </div>
    </div>



    <!-- Group Selector for Private Visibility -->
    <div v-if="visibility === 'private'" class="mt-4">
      <GroupSelector
        v-model="localGroupId"
        :organization-id="organizationId"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { 
  DocumentTextIcon, 
  LockClosedIcon, 
  GlobeAltIcon, 
  CheckCircleIcon,
  ClockIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { CheckBadgeIcon } from '@heroicons/vue/24/solid'
import GroupSelector from './GroupSelector.vue'

const props = defineProps({
  visibility: {
    type: String,
    default: 'public_pending'
  },
  groupId: {
    type: String,
    default: null
  },

  hideDetails: {
    type: Boolean,
    default: false
  },
  rejectionMessage: {
    type: String,
    default: null
  },
  organizationId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:visibility', 'update:groupId', 'update:hideDetails'])

const localGroupId = ref(props.groupId)
const hideDetails = ref(props.hideDetails)

const isPublic = computed(() => {
  return ['public_pending', 'public_rejected', 'public_approved'].includes(props.visibility)
})

const isPending = computed(() => props.visibility === 'public_pending')
const isApproved = computed(() => props.visibility === 'public_approved')
const isRejected = computed(() => props.visibility === 'public_rejected')

const selectVisibility = (value) => {
  emit('update:visibility', value)
  
  // If not private, clear group
  if (value !== 'private') {
    emit('update:groupId', null)
    localGroupId.value = null
  }
  
  // If not public, clear related flags
  if (!['public_pending', 'public_rejected', 'public_approved'].includes(value)) {
    emit('update:hideDetails', false)
    hideDetails.value = false
  }
}



const toggleHideDetails = () => {
  const newValue = !hideDetails.value
  hideDetails.value = newValue
  emit('update:hideDetails', newValue)
}

watch(localGroupId, (newValue) => {
  emit('update:groupId', newValue)
})

watch(() => props.groupId, (newValue) => {
  localGroupId.value = newValue
})



watch(() => props.hideDetails, (newValue) => {
  hideDetails.value = newValue
})
</script>
