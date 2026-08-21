<template>
  <!-- Render each block -->
  <div class="org-description prose prose-sm max-w-none text-gray-700" @click="handleLinkClick">
    <template v-for="(block, i) in blocks" :key="i">
      <div v-if="block.type === 'member'" class="my-3 not-prose">
        <MemberCard :member="block.member" class="w-fit" />
      </div>

      <!-- Image block: ![alt](url) – allowed org images are rendered -->
      <div v-else-if="block.type === 'image'" class="my-4 not-prose flex flex-col items-center">
        <img :src="block.url" :alt="block.alt" class="rounded-xl max-w-full shadow-sm border border-gray-100" />
        <p v-if="block.alt" class="text-xs text-gray-400 mt-1 text-center">{{ block.alt }}</p>
      </div>

      <!-- Plain markdown text block -->
      <div v-else-if="block.type === 'text'" v-html="renderMarkdown(block.content)" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import MemberCard from './MemberCard.vue'

type Block =
  | { type: 'text'; content: string }
  | { type: 'member'; member: any }
  | { type: 'image'; alt: string; url: string }

const props = defineProps({
  description: {
    type: String,
    default: ''
  },
  members: {
    type: Array as () => Array<{ user_id: string; full_name?: string | null; email?: string | null; [key: string]: any }>,
    default: () => []
  },
  // Only images whose URL is in this list will be rendered.
  allowedImageUrls: {
    type: Array as () => string[],
    default: () => []
  }
})

const router = useRouter()

// Images are handled only by the allow-listed block parser below. Keeping the
// markdown-it image rule disabled prevents an unapproved image from falling
// through to the generic renderer.
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
}).disable('image')

// Configure external links to open in a new tab with rel="noopener noreferrer"
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

const allowedImageUrlSet = computed(() => new Set(props.allowedImageUrls))

function isAllowedImage(url: string): boolean {
  return Boolean(url) && allowedImageUrlSet.value.has(url)
}

// Find member by user_id, membership id, full_name, email, or email username
function findMember(rawKey: string): any | undefined {
  if (!rawKey) return undefined
  const key = rawKey.trim()
  const lowerKey = key.toLowerCase()

  // 1. Direct ID / user_id match
  const byId = props.members.find(m => m.user_id === key || m.id === key)
  if (byId) return byId

  // 2. Exact match by full_name (case-insensitive)
  const byName = props.members.find(m => m.full_name && m.full_name.trim().toLowerCase() === lowerKey)
  if (byName) return byName

  // 3. Exact match by email (case-insensitive)
  const byEmail = props.members.find(m => m.email && m.email.trim().toLowerCase() === lowerKey)
  if (byEmail) return byEmail

  // 4. Match by email username part (e.g. "john.doe" from "john.doe@domain.com")
  const byUsername = props.members.find(m => {
    if (!m.email) return false
    const username = m.email.split('@')[0]
    return username.toLowerCase() === lowerKey
  })
  if (byUsername) return byUsername

  return undefined
}

// Parse description into blocks: text, member card, or image
const blocks = computed(() => {
  if (!props.description) return []

  const lines = props.description.split('\n')
  const result: Block[] = []
  let textBuffer: string[] = []

  const flushText = () => {
    if (textBuffer.length > 0) {
      result.push({ type: 'text', content: textBuffer.join('\n') })
      textBuffer = []
    }
  }

  for (const line of lines) {
    const trimmed = line.trim()

    // Standalone member line: @[user_id], @[Full Name], @[email]
    const bracketMatch = trimmed.match(/^@\[([^\]]+)\]$/)
    if (bracketMatch) {
      const member = findMember(bracketMatch[1])
      if (member) {
        flushText()
        result.push({ type: 'member', member })
        continue
      }
    }

    // Standalone bare member line: @user_id, @Full Name, @email, @username
    const bareMatch = trimmed.match(/^@([^\s@]+(?: [^\s@]+)*)$/)
    if (bareMatch) {
      const member = findMember(bareMatch[1])
      if (member) {
        flushText()
        result.push({ type: 'member', member })
        continue
      }
    }

    // Standalone image line: ![alt](url)
    const imageMatch = trimmed.match(/^!\[([^\]]*)\]\(([^)]+)\)$/)
    if (imageMatch) {
      const alt = imageMatch[1]
      const url = imageMatch[2]
      if (isAllowedImage(url)) {
        flushText()
        result.push({ type: 'image', alt, url })
        continue
      }
      // Not allowed – render as text
    }

    textBuffer.push(line)
  }

  flushText()
  return result
})

// Replace inline member mentions (@[Name] or @username) with links to profile
function preprocessInlineMembers(content: string): string {
  const isUuid = (str: string) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str.trim())

  // 1. Bracketed mentions: @[key]
  let text = content.replace(/@\[([^\]]+)\]/g, (match, key) => {
    const member = findMember(key)
    if (member) {
      const displayName = member.full_name || member.email
      return `[@${displayName}](/users/${member.user_id})`
    }
    if (isUuid(key)) {
      return `[@Membre](/users/${key.trim()})`
    }
    return match
  })

  // 2. Bare mentions: @username or @email or @user_id (preceded by start or whitespace/punctuation)
  text = text.replace(/(^|[^\w/])@([a-zA-Z0-9._-]+(?:@[a-zA-Z0-9._-]+)?)/g, (match, prefix, key) => {
    const member = findMember(key)
    if (member) {
      const displayName = member.full_name || member.email
      return `${prefix}[@${displayName}](/users/${member.user_id})`
    }
    if (isUuid(key)) {
      return `${prefix}[@Membre](/users/${key.trim()})`
    }
    return match
  })

  return text
}

// Markdown renderer for text blocks using markdown-it
function renderMarkdown(text: string): string {
  if (!text) return ''
  const preprocessed = preprocessInlineMembers(text)
  return md.render(preprocessed)
}

// Internal links (/users/..., /organizations/...) navigate via the router
function handleLinkClick(event: MouseEvent) {
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
  if (href && href.startsWith('/') && router) {
    event.preventDefault()
    router.push(href)
  }
}
</script>

<style scoped>
.org-description :deep(a) {
  color: #4f46e5;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.org-description :deep(a:hover) {
  color: #4338ca;
}
.org-description :deep(h1) {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}
.org-description :deep(h2) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-top: 0.75rem;
  margin-bottom: 0.375rem;
}
.org-description :deep(h3) {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin-top: 0.5rem;
  margin-bottom: 0.25rem;
}
.org-description :deep(p) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.org-description :deep(ul) {
  list-style-type: disc;
  padding-left: 1.25rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.org-description :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.25rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.org-description :deep(li) {
  margin-top: 0.125rem;
  margin-bottom: 0.125rem;
}
.org-description :deep(code) {
  background: #f3f4f6;
  border-radius: 0.25rem;
  padding: 0.1rem 0.25rem;
  font-size: 0.875em;
  font-family: monospace;
}
.org-description :deep(hr) {
  border-color: #e5e7eb;
  margin-top: 1rem;
  margin-bottom: 1rem;
}
</style>
