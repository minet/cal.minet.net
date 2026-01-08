<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Gestion des membres</h1>
        <p class="mt-2 text-sm text-gray-600">{{ organization?.name }}</p>
      </div>
    </header>

    <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
      <p class="text-sm text-red-800">{{ error }}</p>
    </div>

    <!-- Add Member Form -->
    <div class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Ajouter un membre</h2>
      <div class="flex gap-3">
        <div class="flex-1">
          <UserSearchSelector
            placeholder="Rechercher un utilisateur par nom ou email..."
            @select="onUserSelect"
          />
        </div>
        <Dropdown
          v-model="newMemberRole"
          :options="[
            { value: 'org_viewer', label: 'Lecteur' },
            { value: 'org_member', label: 'Membre' },
            { value: 'org_admin', label: 'Administrateur' }
          ]"
        />
      </div>
    </div>

    <!-- Members List -->
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div v-if="loadingMembers" class="text-center py-12">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <div v-else-if="members.length === 0" class="text-center py-12">
        <p class="text-sm text-gray-500">Aucun membre</p>
      </div>

      <ul v-else class="divide-y divide-gray-200">
        <li v-for="member in members" :key="member.id" class="p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                <img v-if="member.profile_picture_url" :src="member.profile_picture_url" :alt="getFullName(member)" class="h-full w-full object-cover" />
                <span v-else class="text-gray-600 font-medium text-sm">
                  {{ getInitials(getFullName(member)) }}
                </span>
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ getFullName(member) }}
                </p>
                <p class="text-xs text-gray-500">{{ member.email }}</p>
              </div>
            </div>

            <div class="flex items-center space-x-3">
              <Dropdown
                :model-value="member.role"
                @update:model-value="updateMemberRole(member, $event)"
                :disabled="member.user_id === currentUserId"
                :options="[
                  { value: 'org_viewer', label: 'Lecteur' },
                  { value: 'org_member', label: 'Membre' },
                  { value: 'org_admin', label: 'Administrateur' }
                ]"
              />

              <button
                @click="removeMember(member)"
                :disabled="member.user_id === currentUserId && isLastAdmin(member)"
                class="text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                :title="member.user_id === currentUserId && isLastAdmin(member) ? 'Impossible de retirer le dernier administrateur' : 'Retirer ce membre'"
              >
                <TrashIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { TrashIcon } from '@heroicons/vue/24/outline'
import UserSearchSelector from '../components/UserSearchSelector.vue'
import Dropdown from '../components/Dropdown.vue'
import api from '../utils/api'

const route = useRoute()
const { user } = useAuth()
const organization = ref(null)
const members = ref([])
const selectedUser = ref(null)
const newMemberRole = ref('org_member')
const loading = ref(false)
const loadingMembers = ref(false)
const error = ref('')

const currentUserId = computed(() => user.value?.id)

const getFullName = (member) => {
  if (member.full_name) {
    return member.full_name
  }
  return member.email
}

const getInitials = (name) => {
  return name
    .split(/\s+/)
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

const isLastAdmin = (member) => {
  if (member.role !== 'org_admin') return false
  const adminCount = members.value.filter(m => m.role === 'org_admin').length
  return adminCount <= 1
}

const loadOrganization = async () => {
  try {
    const response = await api.get(`/organizations/${route.params.id}`)
    organization.value = response.data
  } catch (err) {
    console.error('Failed to load organization:', err)
    error.value = 'Impossible de charger l\'organisation'
  }
}

const loadMembers = async () => {
  loadingMembers.value = true
  try {
    const response = await api.get(`/organizations/${route.params.id}/members`)
    members.value = response.data
  } catch (err) {
    console.error('Failed to load members:', err)
    error.value = 'Impossible de charger les membres'
  } finally {
    loadingMembers.value = false
  }
}

const onUserSelect = async (user) => {
  selectedUser.value = user
  await addMember()
}

const addMember = async () => {
  if (!selectedUser.value) return
  
  loading.value = true
  error.value = ''

  try {
    await api.post(`/organizations/${route.params.id}/members`, null, {
      params: {
        email: selectedUser.value.email,
        role: newMemberRole.value
      }
    })
    
    selectedUser.value = null
    newMemberRole.value = 'org_member'
    await loadMembers()
  } catch (err) {
    console.error('Failed to add member:', err)
    error.value = err.response?.data?.detail || 'Impossible d\'ajouter le membre'
  } finally {
    loading.value = false
  }
}

const updateMemberRole = async (member, newRole) => {
  try {
    await api.put(
      `/organizations/${route.params.id}/members/${member.id}`,
      null,
      { params: { role: newRole } }
    )
    await loadMembers()
  } catch (err) {
    console.error('Failed to update role:', err)
    error.value = err.response?.data?.detail || 'Impossible de modifier le rôle'
  }
}

const removeMember = async (member) => {
  if (!confirm(`Êtes-vous sûr de vouloir retirer ${member.full_name || member.email} ?`)) {
    return
  }

  try {
    await api.delete(`/organizations/${route.params.id}/members/${member.id}`)
    await loadMembers()
  } catch (err) {
    console.error('Failed to remove member:', err)
    error.value = err.response?.data?.detail || 'Impossible de retirer le membre'
  }
}

onMounted(() => {
  loadOrganization()
  loadMembers()
})
</script>
