<template>
  <img
    v-if="resolvedSrc"
    :src="resolvedSrc"
    :srcset="srcset || undefined"
    :sizes="sizesAttr"
    :alt="alt"
    :class="imgClass"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue'
import { resolveMediaUrl, buildSrcset } from '../utils/media'
import type { StoredFileRead } from '../api/types'

const props = defineProps({
  storedFile: { type: Object as () => StoredFileRead | null, default: null },
  fallbackUrl: { type: String as PropType<string | null>, default: null },
  displayWidth: { type: Number, default: 640 },
  alt: { type: String, default: '' },
  imgClass: { type: String, default: '' },
  sizesAttr: { type: String, default: '100vw' },
})

const resolvedSrc = computed(() =>
  resolveMediaUrl(props.storedFile, props.displayWidth) ?? props.fallbackUrl
)
const srcset = computed(() => buildSrcset(props.storedFile))
</script>
