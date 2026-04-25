<template>
  <!-- Render each block -->
  <div class="org-description prose prose-sm max-w-none text-gray-700">
    <template v-for="(block, i) in blocks" :key="i">
      <div v-if="block.type === 'member'" class="my-3 not-prose">
        <MemberCard :member="block.member" class="w-fit" />
      </div>

      <!-- Image block: ![alt](url) – only allowed org images are rendered -->
      <div v-else-if="block.type === 'image'" class="my-4 not-prose">
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
    type: Array as () => Array<{ user_id: string; full_name?: string | null; [key: string]: any }>,
    default: () => []
  },
  // Only images whose URL is in this list will be rendered
  allowedImageUrls: {
    type: Array as () => string[],
    default: () => []
  }
})

// Build a lookup for members by user_id and full_name
const memberByUserId = computed(() => {
  const map: Record<string, any> = {}
  for (const m of props.members) {
    map[m.user_id] = m
  }
  return map
})

const memberByName = computed(() => {
  const map: Record<string, any> = {}
  for (const m of props.members) {
    if (m.full_name) {
      map[m.full_name.toLowerCase()] = m
    }
  }
  return map
})

const allowedImageUrlSet = computed(() => new Set(props.allowedImageUrls))

// Parse description into blocks: text, member, or image
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
    // Check for member line: @[user_id] or @[Full Name]
    const memberMatch = line.match(/^@\[([^\]]+)\]\s*$/)
    if (memberMatch) {
      flushText()
      const key = memberMatch[1].trim()
      const member = memberByUserId.value[key] || memberByName.value[key.toLowerCase()]
      if (member) {
        result.push({ type: 'member', member })
      } else {
        // Fallback: render as text
        textBuffer.push(line)
      }
      continue
    }

    // Check for image line: ![alt](url)
    const imageMatch = line.match(/^!\[([^\]]*)\]\(([^)]+)\)\s*$/)
    if (imageMatch) {
      const alt = imageMatch[1]
      const url = imageMatch[2]
      if (allowedImageUrlSet.value.has(url)) {
        flushText()
        result.push({ type: 'image', alt, url })
        continue
      }
      // Not in allowed list – render as text
    }

    textBuffer.push(line)
  }

  flushText()
  return result
})

// Very lightweight markdown renderer for text blocks
function renderMarkdown(text: string) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-semibold text-gray-900 mt-3 mb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-semibold text-gray-900 mt-4 mb-1">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold text-gray-900 mt-4 mb-2">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-gray-100 rounded px-1 text-sm">$1</code>')
    .replace(/^[-*] (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^---$/gm, '<hr class="my-4 border-gray-200" />')
    .replace(/\n/g, '<br />')
}
</script>
