<template>
  <router-link :to="`/users/${member.user_id}`"
    class="flex flex-col items-center p-4 rounded-xl border transition-all text-center group bg-white" :class="[
      ['org_admin', 'superadmin'].includes(member.role) ? 'border-gray-100 shadow-md shadow-blue-500/40 hover:shadow-lg hover:shadow-blue-500/60' :
        member.role === 'org_member' ? 'border-gray-100 shadow-md shadow-green-500/40 hover:shadow-lg hover:shadow-green-500/60' :
          'border-gray-100 hover:border-indigo-100 hover:shadow-md'
    ]">
    <UserAvatar :src="member.profile_picture_url" :name="member.full_name || member.email" size="xl"
      class="mb-3 shadow-sm group-hover:scale-105 transition-transform duration-300" />
    <p class="text-sm font-medium text-gray-900 line-clamp-2 w-full">{{ member.full_name || member.email }}</p>
    <p v-if="member.title" class="text-xs text-indigo-600 mt-1 line-clamp-2 w-full">{{ member.title }}</p>
  </router-link>
</template>

<script setup>
import UserAvatar from './UserAvatar.vue'

defineProps({
  member: {
    type: Object,
    required: true
    // Expected: { user_id, full_name, email, profile_picture_url, title, role }
  }
})
</script>
