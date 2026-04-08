<template>
  <router-link :to="`/users/${member.user_id}`"
    class="flex flex-col items-center p-4 rounded-xl border transition-all text-center group bg-white" :class="[
      ['org_admin', 'superadmin'].includes(member.role)
        ? 'border-gray-100 shadow-md shadow-blue-500/40 hover:shadow-lg hover:shadow-blue-500/60'
        : member.role === 'org_member'
          ? 'border-gray-100 shadow-md shadow-green-500/40 hover:shadow-lg hover:shadow-green-500/60'
          : 'border-gray-100 hover:border-indigo-100 hover:shadow-md'
    ]">
    <UserAvatar :src="resolveMediaUrl(member.profile_picture_file, 128) ?? member.profile_picture_url" :name="member.full_name || member.email" size="xl"
      class="mb-3 shadow-sm group-hover:scale-105 transition-transform duration-300" />
    <p class="text-sm font-medium text-gray-900 line-clamp-2 w-full">{{ member.full_name || member.email }}</p>
    <p v-if="member.title" class="text-xs text-indigo-600 mt-1 line-clamp-2 w-full">{{ member.title }}</p>

    <!-- Phone number -->
    <a v-if="member.phone_number" :href="`tel:${member.phone_number}`" @click.prevent.stop="() => { }"
      class="flex items-center justify-center gap-1 mt-2 text-xs text-gray-500 hover:text-gray-700"
      :title="member.phone_number">
      <PhoneIcon class="h-3 w-3 shrink-0" />
      <span class="truncate max-w-[8rem]">{{ member.phone_number }}</span>
    </a>

    <!-- Social link icons -->
    <div v-if="member.links && member.links.length > 0" class="flex items-center justify-center gap-2 mt-2 flex-wrap">
      <a v-for="link in member.links" :key="link.id" :href="link.url" target="_blank"
        @click.prevent.stop="openLink(link.url)"
        class="flex items-center justify-center h-6 w-6 rounded-full hover:scale-110 transition-transform"
        :title="link.name">
        <img v-if="getSocialIcon(link.url)" :src="getSocialIcon(link.url)" class="h-4 w-4 object-contain" />
        <LinkIcon v-else class="h-4 w-4 text-gray-500" />
      </a>
    </div>
  </router-link>
</template>

<script setup>
import UserAvatar from './UserAvatar.vue'
import { LinkIcon, PhoneIcon } from '@heroicons/vue/24/outline'
import { getSocialIcon } from '../utils/social'
import { resolveMediaUrl } from '../utils/media.js'

defineProps({
  member: {
    type: Object,
    required: true
    // Expected: { user_id, full_name, email, profile_picture_url, phone_number, title, role, links }
  }
})

function openLink(url) {
  window.open(url, '_blank', 'noopener,noreferrer')
}
</script>
