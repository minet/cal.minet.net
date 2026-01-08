<template>
  <div class="max-w-4xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Tags de l'organisation</h1>
          <p class="mt-2 text-sm text-gray-600">{{ organization?.name }}</p>
        </div>
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          Nouveau tag
        </button>
      </div>
    </header>

    <div class="bg-white shadow-sm rounded-lg p-6">
      <div v-if="loading" class="text-center py-12">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <div v-else-if="tags.length === 0" class="text-center py-12">
        <p class="text-sm text-gray-500">Aucun tag pour le moment</p>
        <button
          @click="showCreateModal = true"
          class="mt-4 text-sm text-indigo-600 hover:text-indigo-700"
        >
          Créer le premier tag
        </button>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="tag in tags"
          :key="tag.id"
          class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
        >
          <div class="flex items-center space-x-4 flex-1">
            <div
              class="h-8 w-8 rounded-full border-2"
              :style="{ backgroundColor: tag.color + '30', borderColor: tag.color }"
            />
            <div class="flex-1">
              <TextInput
                v-if="editingTag === tag.id"
                v-model="tag.name"
                @keyup.enter="saveTag(tag)"
                @keyup.esc="editingTag = null"
              />
              <span v-else class="text-sm font-medium text-gray-900">{{ tag.name }}</span>
            </div>
            <input
              v-if="editingTag === tag.id"
              v-model="tag.color"
              type="color"
              class="h-10 w-20 rounded border-gray-300"
            />
          </div>
          <div class="flex items-center space-x-2">
            <button
              v-if="editingTag === tag.id"
              @click="saveTag(tag)"
              class="px-3 py-1 text-sm text-green-600 hover:text-green-700"
            >
              Sauver
            </button>
            <button
              v-else
              @click="editingTag = tag.id"
              class="px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700"
            >
              Modifier
            </button>
            <button
              @click="deleteTag(tag.id)"
              class="px-3 py-1 text-sm text-red-600 hover:text-red-700"
            >
              Supprimer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Créer un nouveau tag</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Nom</label>
            <input
              v-model="newTag.name"
              type="text"
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm"
              placeholder="Ex: Culture, Sport, Soirée..."
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Couleur</label>
            <input
              v-model="newTag.color"
              type="color"
              class="h-10 w-full rounded border-gray-300"
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
            @click="createTag"
            :disabled="!newTag.name"
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
import TextInput from '../components/TextInput.vue'
import api from '../utils/api'

const route = useRoute()
const orgId = route.params.id

const organization = ref(null)
const tags = ref([])
const loading = ref(true)
const editingTag = ref(null)
const showCreateModal = ref(false)
const newTag = ref({
  name: '',
  color: '#6366f1'
})

const loadOrganization = async () => {
  try {
    const response = await api.get(`/organizations/${orgId}`)
    organization.value = response.data
  } catch (error) {
    console.error('Failed to load organization:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await api.get(`/organizations/${orgId}/tags`)
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
  } finally {
    loading.value = false
  }
}

const createTag = async () => {
  try {
    await api.post(`/organizations/${orgId}/tags`, newTag.value)
    newTag.value = { name: '', color: '#6366f1' }
    showCreateModal.value = false
    await loadTags()
  } catch (error) {
    console.error('Failed to create tag:', error)
  }
}

const saveTag = async (tag) => {
  try {
    await api.put(`/tags/${tag.id}`, {
      name: tag.name,
      color: tag.color
    })
    editingTag.value = null
  } catch (error) {
    console.error('Failed to update tag:', error)
  }
}

const deleteTag = async (tagId) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer ce tag ?')) return
  
  try {
    await api.delete(`/tags/${tagId}`)
    await loadTags()
  } catch (error) {
    console.error('Failed to delete tag:', error)
  }
}

onMounted(async () => {
  await Promise.all([loadOrganization(), loadTags()])
})
</script>
