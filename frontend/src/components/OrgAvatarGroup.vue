<template>
  <div v-if="allOrgs.length > 0" class="max-w-full min-w-0">
    <!-- Single organization in pill mode -->
    <div
      v-if="singleMode === 'pill' && allOrgs.length === 1"
      class="inline-flex items-center rounded-full bg-white/60 px-1.5 py-0.5 backdrop-blur-sm max-w-full min-w-0"
    >
      <img
        v-if="getOrgLogo(allOrgs[0], 32)"
        :src="getOrgLogo(allOrgs[0], 32)!"
        :alt="allOrgs[0].name"
        class="mr-1 h-3 w-3 rounded-full object-cover shrink-0"
      />
      <span
        v-else
        class="mr-1 h-3 w-3 rounded-full flex items-center justify-center text-[8px] font-bold shrink-0"
        :style="{
          backgroundColor: allOrgs[0].color_secondary || '#f0f9ff',
          color: allOrgs[0].color_primary || '#0369a1'
        }"
      >
        {{ allOrgs[0].name?.charAt(0) || '?' }}
      </span>
      <span
        class="text-[10px] font-medium leading-none truncate max-w-[100px]"
        :style="{ color: allOrgs[0].color_primary || '#4f46e5' }"
      >
        {{ allOrgs[0].name }}
      </span>
    </div>

    <!-- Stack of organization avatars -->
    <div
      v-else
      class="flex items-center shrink-0 max-w-full"
    >
      <template v-for="(org, index) in visibleOrgs" :key="org.id ? `${org.id}_${index}` : index">
        <div
          :class="[
            'rounded-full overflow-hidden bg-white shrink-0 flex items-center justify-center transition-all duration-150',
            sizeClass,
            ringClass
          ]"
          :style="index > 0 ? { marginLeft: `${computedMargin}px` } : undefined"
          :title="org.name"
        >
          <img
            v-if="getOrgLogo(org, mediaSize)"
            :src="getOrgLogo(org, mediaSize)!"
            :alt="org.name"
            class="h-full w-full object-cover"
          />
          <span
            v-else
            :class="['w-full h-full flex items-center justify-center font-bold', textSizeClass]"
            :style="{
              backgroundColor: org.color_secondary || '#f0f9ff',
              color: org.color_primary || '#0369a1'
            }"
          >
            {{ org.name?.charAt(0) || '?' }}
          </span>
        </div>
      </template>

      <!-- Overflow indicator (+N) if more than effective max -->
      <div
        v-if="remainingCount > 0"
        :class="[
          'rounded-full overflow-hidden flex items-center justify-center font-bold shrink-0 bg-gray-100 text-gray-700 select-none shadow-sm transition-all duration-150',
          sizeClass,
          ringClass,
          textSizeClass
        ]"
        :style="{ marginLeft: `${computedMargin}px` }"
        :title="remainingTitle"
      >
        +{{ remainingCount }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { resolveMediaUrl } from '../utils/media'

interface OrganizationLike {
  id?: string
  name: string
  logo_file?: any
  logo_url?: string | null
  color_primary?: string | null
  color_secondary?: string | null
}

const props = withDefaults(
  defineProps<{
    organization?: OrganizationLike | null
    guestOrganizations?: OrganizationLike[] | null
    max?: number
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
    singleMode?: 'avatar' | 'pill'
  }>(),
  {
    organization: null,
    guestOrganizations: () => [],
    max: undefined,
    size: 'sm',
    singleMode: 'avatar'
  }
)

const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

const onWindowResize = () => {
  if (typeof window !== 'undefined') {
    windowWidth.value = window.innerWidth
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    windowWidth.value = window.innerWidth
    window.addEventListener('resize', onWindowResize)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', onWindowResize)
  }
})

const allOrgs = computed<OrganizationLike[]>(() => {
  const list: OrganizationLike[] = []
  const seen = new Set<string>()

  if (props.organization) {
    list.push(props.organization)
    if (props.organization.id) seen.add(props.organization.id)
  }

  if (props.guestOrganizations && Array.isArray(props.guestOrganizations)) {
    for (const guest of props.guestOrganizations) {
      if (guest) {
        if (!guest.id || !seen.has(guest.id)) {
          list.push(guest)
          if (guest.id) seen.add(guest.id)
        }
      }
    }
  }

  return list
})

// Responsive max calculation based on screen size and avatar size
const effectiveMax = computed(() => {
  let responsiveMax = 4
  const w = windowWidth.value
  const s = props.size

  if (w < 640) {
    // Mobile (< 640px)
    switch (s) {
      case 'xs': responsiveMax = 3; break
      case 'sm': responsiveMax = 4; break
      case 'md': responsiveMax = 3; break
      case 'lg': responsiveMax = 3; break
      case 'xl': responsiveMax = 3; break
    }
  } else if (w < 1024) {
    // Tablet (640px - 1024px)
    switch (s) {
      case 'xs': responsiveMax = 4; break
      case 'sm': responsiveMax = 5; break
      case 'md': responsiveMax = 4; break
      case 'lg': responsiveMax = 4; break
      case 'xl': responsiveMax = 4; break
    }
  } else if (w < 1280) {
    // Desktop (1024px - 1280px)
    switch (s) {
      case 'xs': responsiveMax = 5; break
      case 'sm': responsiveMax = 6; break
      case 'md': responsiveMax = 5; break
      case 'lg': responsiveMax = 5; break
      case 'xl': responsiveMax = 5; break
    }
  } else {
    // Large screens (>= 1280px)
    switch (s) {
      case 'xs': responsiveMax = 6; break
      case 'sm': responsiveMax = 8; break
      case 'md': responsiveMax = 6; break
      case 'lg': responsiveMax = 6; break
      case 'xl': responsiveMax = 6; break
    }
  }

  if (props.max && props.max > 0) {
    return Math.min(props.max, responsiveMax)
  }

  return responsiveMax
})

const visibleOrgs = computed(() => {
  if (allOrgs.value.length <= effectiveMax.value) {
    return allOrgs.value
  }
  return allOrgs.value.slice(0, effectiveMax.value)
})

const remainingOrgs = computed(() => {
  if (allOrgs.value.length <= effectiveMax.value) {
    return []
  }
  return allOrgs.value.slice(effectiveMax.value)
})

const remainingCount = computed(() => remainingOrgs.value.length)

const remainingTitle = computed(() => {
  const names = remainingOrgs.value.map(o => o.name).filter(Boolean).join(', ')
  return `+${remainingCount.value} : ${names}`
})

const totalRenderedItems = computed(() => {
  return visibleOrgs.value.length + (remainingCount.value > 0 ? 1 : 0)
})

function getBaseMargin(size: 'xs' | 'sm' | 'md' | 'lg' | 'xl', count: number): number {
  switch (size) {
    case 'xs':
      if (count <= 2) return -4
      if (count <= 3) return -4
      if (count <= 4) return -5
      if (count <= 5) return -6
      return -7
    case 'sm':
      if (count <= 2) return -6
      if (count <= 3) return -6
      if (count <= 4) return -7
      if (count <= 5) return -8
      if (count <= 6) return -9
      if (count <= 7) return -10
      return -11
    case 'md':
      if (count <= 2) return -8
      if (count <= 3) return -9
      if (count <= 4) return -10
      if (count <= 5) return -12
      return -14
    case 'lg':
      if (count <= 2) return -10
      if (count <= 3) return -12
      if (count <= 4) return -14
      if (count <= 5) return -16
      return -18
    case 'xl':
      if (count <= 2) return -12
      if (count <= 3) return -14
      if (count <= 4) return -16
      if (count <= 5) return -18
      return -20
    default:
      return -6
  }
}

const computedMargin = computed(() => {
  const count = totalRenderedItems.value
  if (count <= 1) return 0
  return getBaseMargin(props.size, count)
})

const getOrgLogo = (org: OrganizationLike, sizePx: number) => {
  return (resolveMediaUrl(org.logo_file, sizePx) ?? org.logo_url) ?? null
}

const mediaSize = computed(() => {
  switch (props.size) {
    case 'xs':
    case 'sm':
      return 32
    case 'md':
    case 'lg':
    case 'xl':
    default:
      return 64
  }
})

const sizeClass = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'h-4 w-4'
    case 'sm':
      return 'h-5 w-5'
    case 'md':
      return 'h-8 w-8'
    case 'lg':
      return 'h-10 w-10'
    case 'xl':
      return 'h-12 w-12'
    default:
      return 'h-5 w-5'
  }
})

const textSizeClass = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'text-[8px] leading-none'
    case 'sm':
      return 'text-[9px] leading-none'
    case 'md':
      return 'text-xs'
    case 'lg':
      return 'text-sm'
    case 'xl':
      return 'text-base'
    default:
      return 'text-[9px]'
  }
})

const ringClass = computed(() => {
  switch (props.size) {
    case 'xs':
    case 'sm':
      return 'ring-1 ring-white'
    case 'md':
    case 'lg':
      return 'ring-2 ring-white'
    case 'xl':
      return 'border-4 border-white'
    default:
      return 'ring-1 ring-white'
  }
})
</script>
