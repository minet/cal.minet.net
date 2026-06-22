<template>
  <div class="max-w-3xl mx-auto">
    <router-link
      to="/docs"
      class="inline-flex items-center text-sm text-gray-500 hover:text-gray-800 mb-6"
    >
      <ChevronLeftIcon class="h-4 w-4 mr-1" />
      Documentation
    </router-link>

    <!-- Unknown guide -->
    <div v-if="!doc" class="text-center py-16 text-gray-400">
      <BookOpenIcon class="h-10 w-10 mx-auto mb-3 text-gray-300" />
      <p>Ce guide est introuvable.</p>
    </div>

    <article v-else>
      <header class="mb-6">
        <h1 class="text-2xl font-semibold text-gray-900">{{ doc.title }}</h1>
        <div class="mt-3 flex flex-wrap gap-2">
          <span
            class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
            :class="scopeBadgeClass(doc.scope)"
          >
            {{ scopeLabel(doc.scope) }}
          </span>
          <span
            class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
            :class="audienceBadgeClass(doc.audience)"
          >
            {{ audienceLabel(doc.audience) }}
          </span>
        </div>
      </header>

      <!-- No access: warning banner -->
      <div
        v-if="!hasAccess"
        class="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 flex gap-3"
      >
        <ExclamationTriangleIcon class="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
        <div class="text-sm text-amber-800">
          <p class="font-medium">Vous n'avez pas accès à cette fonctionnalité.</p>
          <p class="mt-0.5">
            Cette action nécessite la permission&nbsp;:
            <strong>{{ audienceLabel(doc.audience) }}</strong>. Le guide reste consultable à
            titre informatif.
          </p>
        </div>
      </div>

      <!-- Organisation-related: where the user can act -->
      <div
        v-if="orgs.length > 0"
        class="mb-6 rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3 flex gap-3"
      >
        <BuildingOfficeIcon class="h-5 w-5 text-indigo-500 shrink-0 mt-0.5" />
        <div class="text-sm text-indigo-800">
          <p class="font-medium">Vous pouvez effectuer cette action dans&nbsp;:</p>
          <ul class="mt-1 space-y-0.5">
            <li v-for="org in orgs" :key="org.id">
              <router-link
                :to="`/organizations/${org.id}`"
                class="underline hover:text-indigo-900"
              >
                {{ org.name }}
              </router-link>
            </li>
          </ul>
        </div>
      </div>

      <!-- Rendered markdown -->
      <div ref="bodyEl" class="doc-body" v-html="renderedHtml" @click="onBodyClick"></div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import {
  BookOpenIcon,
  BuildingOfficeIcon,
  ChevronLeftIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'
import { useDocs } from '@/composables/useDocs'
import {
  audienceBadgeClass,
  audienceLabel,
  canAccess,
  qualifyingOrgs,
  scopeBadgeClass,
  scopeLabel,
} from '@/utils/docsAccess'

const route = useRoute()
const router = useRouter()
const { getDoc, access, memberships, ensureMemberships } = useDocs()

// Images placed next to the docs (src/docs/**) resolved to their bundled URL,
// so authors can reference them with a relative path like ![](images/foo.png).
const assetUrls = import.meta.glob('../docs/**/*.{png,jpg,jpeg,gif,svg,webp,avif}', {
  eager: true,
  query: '?url',
  import: 'default',
}) as Record<string, string>

function resolveAsset(src: string): string {
  if (!src) return src
  // Leave absolute URLs, root-relative paths and data URIs untouched.
  if (/^(https?:)?\/\//i.test(src) || src.startsWith('/') || src.startsWith('data:')) {
    return src
  }
  const clean = src.replace(/^\.\//, '')
  return assetUrls[`../docs/${clean}`] ?? src
}

// html: false escapes raw HTML, so the rendered output is safe for v-html.
const md = new MarkdownIt({ html: false, linkify: true, breaks: false })

// Rewrite relative image sources to their bundled URL.
const defaultImageRule = md.renderer.rules.image
md.renderer.rules.image = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const i = token.attrIndex('src')
  if (i >= 0 && token.attrs) {
    token.attrs[i][1] = resolveAsset(token.attrs[i][1])
  }
  return defaultImageRule
    ? defaultImageRule(tokens, idx, options, env, self)
    : self.renderToken(tokens, idx, options)
}

// Open external links in a new tab.
const defaultLinkOpenRule = md.renderer.rules.link_open
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  const i = token.attrIndex('href')
  const href = i >= 0 && token.attrs ? token.attrs[i][1] : ''
  if (/^https?:\/\//i.test(href)) {
    token.attrSet('target', '_blank')
    token.attrSet('rel', 'noopener noreferrer')
  }
  return defaultLinkOpenRule
    ? defaultLinkOpenRule(tokens, idx, options, env, self)
    : self.renderToken(tokens, idx, options)
}

// Turn [[slug]] (or [[slug|libellé]]) into a link to the matching guide,
// using the target guide's title as the link text when no label is given.
function preprocessWikiLinks(body: string): string {
  return body.replace(
    /\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]/g,
    (_match, slug: string, label?: string) => {
      const targetSlug = slug.trim()
      const target = getDoc(targetSlug)
      const text = (label ?? target?.title ?? targetSlug).trim()
      return `[${text}](/docs/${targetSlug})`
    },
  )
}

const doc = computed(() => getDoc(String(route.params.slug)))

const hasAccess = computed(() => (doc.value ? canAccess(doc.value.audience, access.value) : true))

const orgs = computed(() =>
  doc.value ? qualifyingOrgs(doc.value.audience, memberships.value) : [],
)

const renderedHtml = computed(() =>
  doc.value ? md.render(preprocessWikiLinks(doc.value.body)) : '',
)

// Internal links (/docs/..., /organizations/...) navigate via the router
// instead of triggering a full page reload.
function onBodyClick(event: MouseEvent) {
  if (
    event.defaultPrevented ||
    event.button !== 0 ||
    event.metaKey ||
    event.ctrlKey ||
    event.shiftKey ||
    event.altKey
  ) {
    return
  }
  const anchor = (event.target as HTMLElement).closest('a')
  const href = anchor?.getAttribute('href')
  if (href && href.startsWith('/')) {
    event.preventDefault()
    if (href !== route.fullPath) router.push(href)
  }
}

const bodyEl = ref<HTMLElement | null>(null)

/** The term to highlight, taken from the `?highlight=` query parameter. */
const highlightQuery = computed(() => {
  const raw = route.query.highlight
  const value = Array.isArray(raw) ? raw[0] : raw
  return (value ?? '').toString().trim()
})

/** Remove any previously inserted <mark> wrappers, restoring plain text. */
function clearHighlights(root: HTMLElement): void {
  const marks = root.querySelectorAll('mark.doc-highlight')
  marks.forEach((mark) => {
    const text = document.createTextNode(mark.textContent ?? '')
    mark.replaceWith(text)
  })
  root.normalize()
}

/** Wrap every case-insensitive occurrence of `term` in a <mark>; return the first. */
function applyHighlights(root: HTMLElement, term: string): HTMLElement | null {
  if (!term) return null
  const needle = term.toLowerCase()
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue || !node.nodeValue.toLowerCase().includes(needle)) {
        return NodeFilter.FILTER_REJECT
      }
      const tag = node.parentElement?.tagName
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'MARK') {
        return NodeFilter.FILTER_REJECT
      }
      return NodeFilter.FILTER_ACCEPT
    },
  })

  const textNodes: Text[] = []
  let current = walker.nextNode()
  while (current) {
    textNodes.push(current as Text)
    current = walker.nextNode()
  }

  let first: HTMLElement | null = null
  for (const node of textNodes) {
    const text = node.nodeValue ?? ''
    const lower = text.toLowerCase()
    const fragment = document.createDocumentFragment()
    let cursor = 0
    let match = lower.indexOf(needle)
    while (match !== -1) {
      if (match > cursor) {
        fragment.appendChild(document.createTextNode(text.slice(cursor, match)))
      }
      const mark = document.createElement('mark')
      mark.className = 'doc-highlight'
      mark.textContent = text.slice(match, match + term.length)
      fragment.appendChild(mark)
      if (!first) first = mark
      cursor = match + term.length
      match = lower.indexOf(needle, cursor)
    }
    if (cursor < text.length) {
      fragment.appendChild(document.createTextNode(text.slice(cursor)))
    }
    node.parentNode?.replaceChild(fragment, node)
  }
  return first
}

/** Re-run highlighting for the current term and scroll to the first match. */
async function refreshHighlights(): Promise<void> {
  await nextTick()
  const root = bodyEl.value
  if (!root) return
  clearHighlights(root)
  const first = applyHighlights(root, highlightQuery.value)
  if (first) {
    first.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

onMounted(() => {
  ensureMemberships()
  refreshHighlights()
})

// Re-highlight when the guide or the search term changes.
watch([() => doc.value?.slug, highlightQuery], () => {
  refreshHighlights()
})
</script>

<style scoped>
.doc-body {
  color: #374151;
  font-size: 0.95rem;
  line-height: 1.7;
}
.doc-body :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 1.5rem 0 0.75rem;
}
.doc-body :deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 1.5rem 0 0.5rem;
}
.doc-body :deep(h3) {
  font-size: 1.05rem;
  font-weight: 600;
  color: #111827;
  margin: 1.25rem 0 0.5rem;
}
.doc-body :deep(p) {
  margin: 0.75rem 0;
}
.doc-body :deep(mark.doc-highlight) {
  background: #fde68a;
  color: inherit;
  padding: 0.05rem 0.1rem;
  border-radius: 0.2rem;
  scroll-margin-top: 5rem;
}
.doc-body :deep(ul),
.doc-body :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}
.doc-body :deep(ul) {
  list-style: disc;
}
.doc-body :deep(ol) {
  list-style: decimal;
}
.doc-body :deep(li) {
  margin: 0.25rem 0;
}
.doc-body :deep(a) {
  color: #4f46e5;
  text-decoration: underline;
  cursor: pointer;
}
.doc-body :deep(a:hover) {
  color: #3730a3;
}
.doc-body :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1rem 0;
}
.doc-body :deep(figure) {
  margin: 1rem 0;
}
.doc-body :deep(figcaption) {
  font-size: 0.8rem;
  color: #6b7280;
  text-align: center;
  margin-top: 0.25rem;
}
.doc-body :deep(strong) {
  font-weight: 600;
  color: #111827;
}
.doc-body :deep(code) {
  background: #f3f4f6;
  border-radius: 0.25rem;
  padding: 0.1rem 0.3rem;
  font-size: 0.85em;
}
.doc-body :deep(pre) {
  background: #f3f4f6;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  overflow-x: auto;
  margin: 0.75rem 0;
}
.doc-body :deep(pre code) {
  background: transparent;
  padding: 0;
}
.doc-body :deep(blockquote) {
  border-left: 3px solid #e5e7eb;
  padding-left: 1rem;
  color: #6b7280;
  margin: 0.75rem 0;
}
.doc-body :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1.5rem 0;
}
.doc-body :deep(table) {
  border-collapse: collapse;
  margin: 0.75rem 0;
  width: 100%;
}
.doc-body :deep(th),
.doc-body :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.4rem 0.6rem;
  text-align: left;
}
.doc-body :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}
</style>
