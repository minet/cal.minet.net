/**
 * Loads the static documentation guides bundled under `src/docs/*.md`.
 *
 * Each guide is a markdown file with YAML frontmatter describing its scope and
 * the permission required to act on it. Discovery (`accessibleDocs`) is filtered
 * by the current user's highest permission; individual guides remain reachable
 * by slug (the article page renders them with a warning when unauthorized).
 */
import { computed, ref } from 'vue'
import fm from 'front-matter'
import { api } from '@/api'
import type { MembershipWithOrganization } from '@/api/types'
import { useAuth } from './useAuth'
import {
  canAccess,
  computeHighestAccess,
  type DocAudience,
  type DocScope,
} from '@/utils/docsAccess'

export interface DocFrontmatter {
  title?: string
  scope?: DocScope
  audience?: DocAudience
  category?: string
  order?: number
  summary?: string
}

export interface Doc {
  slug: string
  title: string
  scope: DocScope
  audience: DocAudience
  category: string
  order: number
  summary: string
  body: string
}

// Eagerly import and parse every guide once at module load.
const rawModules = import.meta.glob('../docs/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>

const allDocs: Doc[] = Object.entries(rawModules)
  .map(([path, raw]) => {
    const slug = (path.split('/').pop() ?? '').replace(/\.md$/, '')
    const { attributes, body } = fm<DocFrontmatter>(raw)
    return {
      slug,
      title: attributes.title ?? slug,
      scope: attributes.scope ?? 'application',
      audience: attributes.audience ?? 'all',
      category: attributes.category ?? 'Divers',
      order: attributes.order ?? 0,
      summary: attributes.summary ?? '',
      body,
    } satisfies Doc
  })
  .sort((a, b) => a.order - b.order || a.title.localeCompare(b.title, 'fr'))

// The current user's memberships, loaded once per session and shared across pages.
const memberships = ref<MembershipWithOrganization[]>([])
const membershipsLoaded = ref(false)
let loadingPromise: Promise<void> | null = null

async function ensureMemberships(): Promise<void> {
  if (membershipsLoaded.value) return
  if (loadingPromise) return loadingPromise
  loadingPromise = (async () => {
    try {
      memberships.value = await api.users.get_user_memberships()
    } catch (e) {
      console.error('Failed to load memberships for docs:', e)
      memberships.value = []
    } finally {
      membershipsLoaded.value = true
    }
  })()
  return loadingPromise
}

export function useDocs() {
  const { user } = useAuth()

  const access = computed(() => computeHighestAccess(user.value, memberships.value))

  /** Guides the user is allowed to act on — drives the documentation index. */
  const accessibleDocs = computed(() => allDocs.filter((d) => canAccess(d.audience, access.value)))

  /** Any existing guide by slug, regardless of access (null only if unknown). */
  function getDoc(slug: string): Doc | null {
    return allDocs.find((d) => d.slug === slug) ?? null
  }

  return {
    allDocs,
    accessibleDocs,
    getDoc,
    access,
    memberships,
    membershipsLoaded,
    ensureMemberships,
  }
}
