<template>
  <SlotWrapper />

  <Teleport to="body">
    <Transition name="docs-hint-fade">
      <a
        v-if="visible"
        :href="href"
        target="_blank"
        rel="noopener noreferrer"
        class="docs-hint-popup"
        :style="popupStyle"
        @mouseenter="cancelHide"
        @mouseleave="scheduleHide"
        @click="onPopupClick"
      >
        <QuestionMarkCircleIcon class="docs-hint-popup__icon" />
        <span class="docs-hint-popup__text">
          <span class="docs-hint-popup__title">Ouvrir l'aide</span>
          <span v-if="search" class="docs-hint-popup__sub">« {{ search }} »</span>
        </span>
      </a>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, cloneVNode, Fragment, h, mergeProps, useAttrs, useSlots } from 'vue'
import { QuestionMarkCircleIcon } from '@heroicons/vue/24/outline'

// We attach our listeners (and forward fallthrough attrs) onto the wrapped element
// ourselves, so disable Vue's automatic attribute inheritance to avoid double-applying
// or losing them when DocsHint is a component's root (it renders a Teleport too).
defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    /** Docs path or slug — e.g. "/bienvenue", "bienvenue" or "/docs/bienvenue". */
    path: string
    /** Optional term to locate and highlight inside the target guide. */
    search?: string
    /** Delay in milliseconds before the popup appears on sustained hover. */
    delay?: number
  }>(),
  { search: '', delay: 1500 },
)

const rootEl = ref<HTMLElement | null>(null)
const visible = ref(false)
const pos = ref({ x: 0, y: 0 })
const mouse = { x: 0, y: 0 }

let showTimer: ReturnType<typeof setTimeout> | null = null
let hideTimer: ReturnType<typeof setTimeout> | null = null

function toSlug(path: string): string {
  return path.trim().replace(/^\//, '').replace(/^docs\//, '').replace(/^\//, '')
}

const href = computed(() => {
  const base = `/docs/${toSlug(props.path)}`
  return props.search ? `${base}?highlight=${encodeURIComponent(props.search)}` : base
})

const popupStyle = computed(() => ({
  left: `${pos.value.x}px`,
  top: `${pos.value.y}px`,
}))

function clearShow(): void {
  if (showTimer) {
    clearTimeout(showTimer)
    showTimer = null
  }
}

function clearHide(): void {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

function show(): void {
  const width = 230
  const height = 64
  const gap = 14
  let x = mouse.x + gap
  let y = mouse.y + gap
  if (x + width > window.innerWidth) x = Math.max(8, window.innerWidth - width - 8)
  if (y + height > window.innerHeight) y = Math.max(8, mouse.y - height - gap)
  pos.value = { x, y }
  visible.value = true
}

function onMouseOver(event: MouseEvent): void {
  mouse.x = event.clientX
  mouse.y = event.clientY
  clearHide()
  if (visible.value || showTimer) return
  showTimer = setTimeout(() => {
    showTimer = null
    show()
  }, props.delay)
}

function onMouseMove(event: MouseEvent): void {
  mouse.x = event.clientX
  mouse.y = event.clientY
}

function onMouseOut(event: MouseEvent): void {
  const related = event.relatedTarget as Node | null
  if (related && rootEl.value?.contains(related)) return
  clearShow()
  scheduleHide()
}

function cancelHide(): void {
  clearHide()
}

function scheduleHide(): void {
  clearHide()
  hideTimer = setTimeout(() => {
    visible.value = false
  }, 300)
}

function onPopupClick(): void {
  visible.value = false
}

// -----------------------------------------------------------------------------
// Renderless Wrapper: Grabs the inner element and attaches events to it
// -----------------------------------------------------------------------------
const slots = useSlots()
const attrs = useAttrs()

const SlotWrapper = () => {
  const children = slots.default?.()
  if (!children) return null

  let attached = false

  const mapNodes = (vnodes: any[]): any[] => {
    return vnodes.map(node => {
      if (attached) return node

      // 1. Unwrap Fragments safely (Vue creates these for slots sometimes)
      if (node.type === Fragment) {
        return h(Fragment, node.props || null, mapNodes(node.children as any[]))
      }

      // 2. Look for the first valid HTML Element ('string') or Vue Component ('object' / 'function')
      if (typeof node.type === 'string' || typeof node.type === 'object' || typeof node.type === 'function') {
        attached = true
        // 3. Inject our events + ref, and forward any fallthrough attributes (class, style…)
        //    so wrapping an element stays visually transparent for its parent.
        return cloneVNode(node, mergeProps(attrs, {
          ref: (el: any) => {
            if (!el) {
              rootEl.value = null
              return
            }
            rootEl.value = el instanceof Element ? el : el.$el || null
          },
          onMouseover: onMouseOver,
          onMouseout: onMouseOut,
          onMousemove: onMouseMove,
        }), true)
      }

      return node
    })
  }

  return mapNodes(children)
}

onBeforeUnmount(() => {
  clearShow()
  clearHide()
})
</script>

<style scoped>
/* All base wrapper classes have been removed */

.docs-hint-popup {
  position: fixed;
  z-index: 9999;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 230px;
  padding: 0.45rem 0.7rem;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.6rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  color: #1f2937;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.docs-hint-popup:hover {
  border-color: #a5b4fc;
}
.docs-hint-popup__icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: #6366f1;
}
.docs-hint-popup__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
  line-height: 1.2;
}
.docs-hint-popup__title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #4338ca;
}
.docs-hint-popup__sub {
  font-size: 0.7rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.docs-hint-fade-enter-active,
.docs-hint-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.docs-hint-fade-enter-from,
.docs-hint-fade-leave-to {
  opacity: 0;
  transform: translateY(-2px);
}
</style>