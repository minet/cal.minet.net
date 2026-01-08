<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Groupes de l'organisation</h1>
          <p class="mt-2 text-sm text-gray-600">{{ organization?.name }}</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          Nouveau groupe
        </button>
      </div>
    </header>

    <div v-if="loading" class="text-center py-12">
      <p class="text-sm text-gray-500">Chargement...</p>
    </div>

    <div v-else class="space-y-4">
      <div v-if="groups.length === 0" class="bg-white shadow-sm rounded-lg p-12 text-center">
        <p class="text-sm text-gray-500">Aucun groupe pour le moment</p>
        <button
          @click="showCreateModal = true"
          class="mt-4 text-sm text-indigo-600 hover:text-indigo-700"
        >
          Créer le premier groupe
        </button>
      </div>

      <div
        v-for="group in groups"
        :key="group.id"
        class="bg-white shadow-sm rounded-lg p-6"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900">{{ group.name }}</h3>
            <p v-if="group.description" class="text-sm text-gray-600 mt-1">{{ group.description }}</p>
            <p class="text-xs text-gray-500 mt-2">{{ group.member_count }} membre(s)</p>
          </div>
          <div class="flex space-x-2">
            <button
              @click="selectedGroup = group.id; loadGroupMembers(group.id)"
              class="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700"
            >
              Gérer membres
            </button>
            <button
              @click="deleteGroup(group.id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-700"
            >
              Supprimer
            </button>
          </div>
        </div>

        <!-- Members List (when expanded) -->
        <div v-if="selectedGroup === group.id" class="mt-4 border-t pt-4">
          <h4 class="text-sm font-medium text-gray-900 mb-3">Membres du groupe</h4>
          
          <!-- Add Member Form -->
          <div class="mb-4">
            <UserSearchSelector
              placeholder="Rechercher un utilisateur..."
              :filter="(user) => !isUserInGroup(user)"
              @select="(user) => addMember(group.id, user)"
            />
          </div>

          <!-- Members List -->
          <div v-if="groupMembers.length === 0" class="text-center py-4">
            <p class="text-sm text-gray-500">Aucun membre</p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="member in groupMembers"
              :key="member.membership_id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center space-x-3">
                <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden">
                  <img v-if="member.profile_picture_url" :src="member.profile_picture_url" :alt="getFullName(member)" class="h-full w-full object-cover" />
                  <span v-else class="text-gray-600 font-medium text-xs">
                    {{ getInitials(getFullName(member)) }}
                  </span>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ getFullName(member) }}</p>
                  <p class="text-xs text-gray-500">{{ member.email }}</p>
                </div>
              </div>
              <button
                @click="removeMember(group.id, member.user_id)"
                class="px-3 py-1 text-sm text-red-600 hover:text-red-700"
              >
                Retirer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Group Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Créer un nouveau groupe</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Nom</label>
            <input
              v-model="newGroup.name"
              type="text"
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
              placeholder="Ex: Bureau, CA, Membres actifs..."
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Description (optionnel)</label>
            <textarea
              v-model="newGroup.description"
              rows="3"
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
            />
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-3">
          <button
            @click="showCreateModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-800"
          >
            Annuler
          </button>
          <button
            @click="createGroup"
            :disabled="!newGroup.name"
            class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-500 disabled:opacity-50"
          >
            Créer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { PlusIcon } from '@heroicons/vue/24/outline'
import UserSearchSelector from '../components/UserSearchSelector.vue'
import api from '../utils/api'

const route = useRoute()
const orgId = route.params.id

const organization = ref(null)
const groups = ref([])
const groupMembers = ref([])
const loading = ref(true)
const selectedGroup = ref(null)
const showCreateModal = ref(false)
const newGroup = ref({
  name: '',
  description: ''
})

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

const isUserInGroup = (user) => {
  return groupMembers.value.some(member => member.user_id === user.id)
}

const loadOrganization = async () => {
  try {
    const response = await api.get(`/organizations/${orgId}`)
    organization.value = response.data
  } catch (error) {
    console.error('Failed to load organization:', error)
  }
}

const loadGroups = async () => {
  try {
    const response = await api.get(`/organizations/${orgId}/groups`)
    groups.value = response.data
  } catch (error) {
    console.error('Failed to load groups:', error)
  } finally {
    loading.value = false
  }
}

const loadGroupMembers = async (groupId) => {
  try {
    const response = await api.get(`/groups/${groupId}/members`)
    groupMembers.value = response.data
  } catch (error) {
    console.error('Failed to load group members:', error)
  }
}

const createGroup = async () => {
  try {
    await api.post(`/organizations/${orgId}/groups`, newGroup.value)
    newGroup.value = { name: '', description: '' }
    showCreateModal.value = false
    await loadGroups()
  } catch (error) {
    console.error('Failed to create group:', error)
    alert(error.response?.data?.detail || 'Erreur lors de la création du groupe')
  }
}

const deleteGroup = async (groupId) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer ce groupe ?')) return
  
  try {
    await api.delete(`/groups/${groupId}`)
    await loadGroups()
    if (selectedGroup.value === groupId) {
      selectedGroup.value = null
    }
  } catch (error) {
    console.error('Failed to delete group:', error)
    alert(error.response?.data?.detail || 'Erreur lors de la suppression')
  }
}

const addMember = async (groupId, user) => {
  try {
    await api.post(`/groups/${groupId}/members`, {
      user_email: user.email
    })
    await loadGroupMembers(groupId)
    await loadGroups() // Refresh member counts
  } catch (error) {
    console.error('Failed to add member:', error)
    alert(error.response?.data?.detail || 'Erreur lors de l\'ajout du membre')
  }
}

const removeMember = async (groupId, userId) => {
  if (!confirm('Retirer ce membre du groupe ?')) return
  
  try {
    await api.delete(`/groups/${groupId}/members/${userId}`)
    await loadGroupMembers(groupId)
    await loadGroups() // Refresh member counts
  } catch (error) {
    console.error('Failed to remove member:', error)
    alert(error.response?.data?.detail || 'Erreur lors du retrait')
  }
}

onMounted(async () => {
  await Promise.all([loadOrganization(), loadGroups()])
})
</script>
