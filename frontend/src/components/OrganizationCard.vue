<template>
  <router-link
    v-if="clickable"
    :to="`/organizations/${organization.id}`"
    class="block"
  >
    <div :class="cardClasses">
      <div class="flex items-center space-x-3">
        <!-- Logo -->
        <div 
          v-if="organization.logo_url" 
          :class="logoContainerClasses"
          :style="{ backgroundColor: organization.color_secondary || '#f3f4f6' }"
        >
          <img :src="organization.logo_url" :alt="organization.name" class="w-full h-full object-cover rounded" />
        </div>
        <div 
          v-else 
          :class="logoContainerClasses"
          :style="{ backgroundColor: organization.color_secondary || '#f3f4f6' }"
        >
          <BuildingOfficeIcon 
            :class="logoIconClasses" 
            class="text-gray-400"
            :style="{ color: organization.color_primary || '#9ca3af' }"
          />
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2">
            <h3 :class="nameClasses" class="truncate">{{ organization.name }}</h3>
            <span v-if="showType" :class="typeBadgeClasses">
              {{ typeLabel }}
            </span>
          </div>
          
          <!-- Parent Organization -->
          <div v-if="showParent && organization.parent" class="flex items-center space-x-1 mt-1">            <div class="flex items-center space-x-1" :class="parentTextClasses">
              <div class="h-3 w-3 flex-shrink-0">
                <img 
                  v-if="organization.parent.logo_url" 
                  :src="organization.parent.logo_url" 
                  :alt="organization.parent.name"
                  class="w-full h-full object-cover rounded-sm"
                />
                <BuildingOfficeIcon v-else class="h-3 w-3 text-gray-400" />
              </div>
              <span class="truncate">{{ organization.parent.name }}</span>
            </div>
          </div>
        </div>
        <slot name="side" />
      </div>
    </div>
  </router-link>

  <div v-else :class="cardClasses">
    <div class="flex items-center space-x-3">
      <!-- Logo -->
      <div 
        v-if="organization.logo_url" 
        :class="logoContainerClasses"
      >
        <img :src="organization.logo_url" :alt="organization.name" class="w-full h-full object-cover rounded" />
      </div>
      <div 
        v-else 
        :class="logoContainerClasses"
        :style="{ backgroundColor: organization.color_secondary || '#f3f4f6' }"
      >
        <BuildingOfficeIcon 
          :class="logoIconClasses" 
          class="text-gray-400"
          :style="{ color: organization.color_primary || '#9ca3af' }"
        />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center space-x-2">
          <h3 :class="nameClasses" class="truncate">{{ organization.name }}</h3>
          <span v-if="showType" :class="typeBadgeClasses">
            {{ typeLabel }}
          </span>
        </div>
        
        <!-- Parent Organization -->
        <div v-if="showParent && organization.parent" class="flex items-center space-x-1 mt-1">
          <div class="flex items-center space-x-1" :class="parentTextClasses">
            <div class="h-3 w-3 flex-shrink-0">
              <img 
                v-if="organization.parent.logo_url" 
                :src="organization.parent.logo_url" 
                :alt="organization.parent.name"
                class="w-full h-full object-cover rounded-sm"
              />
              <BuildingOfficeIcon v-else class="h-3 w-3 text-gray-400" />
            </div>
            <span class="truncate">{{ organization.parent.name }}</span>
          </div>
        </div>
      </div>
      <slot name="side" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { BuildingOfficeIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  organization: {
    type: Object,
    required: true
  },
  showParent: {
    type: Boolean,
    default: false
  },
  showType: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: true
  },
  noBorder: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md', // 'sm', 'md', 'lg'
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const typeLabels = {
  association: 'Association',
  club: 'Club',
  liste: 'Liste',
  administration: 'Administration',
  gate: 'GATE'
}

const typeLabel = computed(() => typeLabels[props.organization.type] || props.organization.type)

const cardClasses = computed(() => {
  const base = 'rounded-lg'
  const border = props.noBorder ? '' : 'border border-gray-200'
  const padding = {
    sm: 'p-2',
    md: 'px-4 py-3',
    lg: 'p-6'
  }
  const hover = props.clickable ? 'hover:bg-gray-50 transition-colors' : ''
  
  return [base, border, padding[props.size], hover].join(' ')
})

const logoContainerClasses = computed(() => {
  const sizes = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  }
  
  return `flex-shrink-0 ${sizes[props.size]} rounded bg-gray-100 flex items-center justify-center overflow-hidden`
})

const logoIconClasses = computed(() => {
  const sizes = {
    sm: 'h-5 w-5',
    md: 'h-7 w-7',
    lg: 'h-9 w-9'
  }
  
  return sizes[props.size]
})



const nameClasses = computed(() => {
  const sizes = {
    sm: 'text-sm font-medium',
    md: 'text-base font-semibold',
    lg: 'text-lg font-bold'
  }
  
  return `${sizes[props.size]} text-gray-900`
})

const typeBadgeClasses = computed(() => {
  const sizes = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-xs px-2 py-0.5',
    lg: 'text-sm px-2 py-1'
  }
  
  return `${sizes[props.size]} rounded-full bg-indigo-100 text-indigo-700 font-medium`
})

const parentTextClasses = computed(() => {
  const sizes = {
    sm: 'text-xs',
    md: 'text-xs',
    lg: 'text-sm'
  }
  
  return `${sizes[props.size]} text-gray-500`
})
</script>
