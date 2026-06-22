<template>
  <DocsHint path="/decouvrir-evenements" search="à la une">
  <div
    class="relative overflow-hidden rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 group cursor-pointer h-64 sm:h-80"
    @click="router.push(`/events/${event.id}`)"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <!-- Background: video or image -->
    <div class="absolute inset-0">
      <video
        v-if="event.video_file || event.video_url"
        ref="videoEl"
        :src="event.video_file?.url ?? event.video_url"
        :poster="resolveMediaUrl(event.poster_file, 960) ?? event.poster_url ?? undefined"
        muted
        loop
        playsinline
        preload="metadata"
        class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
      />
      <MediaImage
        v-else-if="event.poster_file || event.poster_url"
        :stored-file="event.poster_file"
        :fallback-url="event.poster_url"
        :display-width="960"
        sizes="(max-width: 1024px) 100vw, 66vw"
        img-class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
        alt=""
      />
      <div v-else class="h-full w-full bg-gradient-to-br from-indigo-500 to-purple-600" />

      <!-- Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
    </div>

    <!-- Content -->
    <div class="absolute inset-x-0 bottom-0 p-6 sm:p-8">
      <div class="flex items-center gap-x-2 text-indigo-300 text-sm font-medium mb-2">
        <span v-if="event.organization" class="px-2 py-0.5 rounded-full bg-white/10 backdrop-blur-sm border border-white/20">
          {{ event.organization.name }}
        </span>
        <span>{{ formatLocalDate(new Date(event.start_time)) }}</span>
      </div>
      <h3 class="text-2xl sm:text-3xl font-bold text-white mb-2 line-clamp-2 drop-shadow-lg">
        {{ event.title }}
      </h3>
      <p v-if="event.location" class="text-gray-300 text-sm flex items-center">
        <MapPinIcon class="h-4 w-4 mr-1" />
        {{ event.location }}
      </p>
    </div>

    <!-- Glowing border -->
    <div class="absolute inset-0 rounded-2xl ring-1 ring-inset ring-white/10 group-hover:ring-indigo-400/50 transition-colors" />
  </div>
  </DocsHint>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { MapPinIcon } from '@heroicons/vue/24/outline'
import { formatLocalDate } from '../utils/dateUtils'
import { resolveMediaUrl } from '../utils/media.js'
import MediaImage from './MediaImage.vue'

const props = defineProps({
  event: { type: Object, required: true }
})

const router = useRouter()
const videoEl = ref<HTMLVideoElement | null>(null)

// Evaluated once — these don't change during a session
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const isSmallPhone = window.matchMedia('(max-width: 480px)').matches
const canAutoplay = !!(props.event.video_file || props.event.video_url) && !prefersReducedMotion && !isSmallPhone

// Start autoplay as soon as the <video> element is mounted (it's always present when video_url is set)
watch(videoEl, (el) => {
  if (el && canAutoplay) el.play().catch(() => {})
})

onMounted(() => {
  if (canAutoplay) videoEl.value?.play().catch(() => {})
})

onBeforeUnmount(() => {
  videoEl.value?.pause()
})

// On hover: start video if not already autoplaying
const onMouseEnter = () => {
  if (!canAutoplay && videoEl.value) videoEl.value.play().catch(() => {})
}

// On leave: only pause if we're NOT in autoplay mode
const onMouseLeave = () => {
  if (!canAutoplay && videoEl.value) {
    videoEl.value.pause()
    videoEl.value.currentTime = 0
  }
}
</script>
