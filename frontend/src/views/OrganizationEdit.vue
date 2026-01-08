<template>
  <div class="max-w-2xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Modifier l'organisation</h1>
      </div>
    </header>

    <div class="bg-white shadow-sm rounded-lg p-6">
      <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>
      
      <form v-if="organization" @submit.prevent="updateOrg">
        <div class="space-y-12">
          <div class="border-b border-gray-900/10 pb-12">
            <div class="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div class="sm:col-span-4">
                <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Nom de l'organisation</label>
                <div class="mt-2">
                  <input 
                    type="text" 
                    name="name" 
                    id="name" 
                    required
                    v-model="form.name" 
                    class="block w-full rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" 
                    placeholder="MINE T" 
                  />
                </div>
              </div>

              <div class="col-span-full">
                <label for="description" class="block text-sm font-medium leading-6 text-gray-900">Description</label>
                <div class="mt-2">
                  <textarea 
                    id="description" 
                    name="description" 
                    rows="3" 
                    v-model="form.description" 
                    class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  ></textarea>
                </div>
              </div>

              <div class="sm:col-span-3">
                <Dropdown
                  v-model="form.type"
                  label="Type"
                  :options="[
                    { value: 'association', label: 'Association' },
                    { value: 'club', label: 'Club' },
                    { value: 'liste', label: 'Liste' },
                    { value: 'administration', label: 'Administration' },
                    { value: 'gate', label: 'GATE' }
                  ]"
                />
              </div>

              <div class="col-span-full">
                <Dropdown
                  v-model="form.parent_id"
                  label="Organisation parente (optionnel)"
                  :options="[
                    { value: null, label: 'Aucune' },
                    ...parentOrganizations.map(org => ({ value: org.id, label: org.name }))
                  ]"
                  hint="Vous pouvez uniquement définir une organisation parente si vous en êtes admin"
                />
              </div>

              <div class="col-span-full">
                <ImageUpload v-model="form.logo_url" label="Logo de l'organisation (optionnel)" />
              </div>

              <div class="sm:col-span-4">
                <label for="color" class="block text-sm font-medium leading-6 text-gray-900">Couleur de l'organisation</label>
                <div class="mt-2 flex items-center gap-x-3">
                  <input 
                    type="color" 
                    id="color" 
                    name="color" 
                    v-model="form.color_hex"
                    class="h-10 w-20 rounded border border-gray-300 p-1 cursor-pointer"
                  />
                  <span class="text-sm text-gray-500">{{ form.color_hex }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex items-center justify-end gap-x-6">
          <router-link 
            :to="`/organizations/${organization.id}`"
            class="text-sm font-semibold leading-6 text-gray-900"
          >
            Annuler
          </router-link>
          <button 
            type="submit" 
            :disabled="loading"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
          >
            {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import ImageUpload from '../components/ImageUpload.vue'
import Dropdown from '../components/Dropdown.vue'
import api from '../utils/api'
import { hexToOklch, oklchToHex } from '../utils/colorUtils'

const router = useRouter()
const route = useRoute()
const { user } = useAuth()
const organization = ref(null)
const parentOrganizations = ref([])
const form = reactive({
  name: '',
  slug: '',
  description: '',
  type: 'association',
  logo_url: null,
  parent_id: null,
  color_hex: '#000000'
})
const error = ref('')
const loading = ref(false)

const loadParentOrganizations = async () => {
  try {
    // Load memberships where user is ORG_ADMIN
    const response = await api.get('/users/me/memberships')
    parentOrganizations.value = response.data
      .filter(m => m.role === 'org_admin')
      .map(m => m.organization)
      .filter(org => org !== null && org.id !== route.params.id) // Exclude current org
    
    // If user is superadmin, load all organizations
    if (user.value?.is_superadmin) {
      const allOrgsResponse = await api.get('/organizations/')
      parentOrganizations.value = allOrgsResponse.data.filter(org => org.id !== route.params.id)
    }
  } catch (err) {
    console.error('Failed to load parent organizations:', err)
  }
}

const loadOrganization = async () => {
  try {
    const response = await api.get(`/organizations/${route.params.id}`)
    organization.value = response.data
    
    // Pre-fill form
    form.name = organization.value.name
    form.slug = organization.value.slug
    form.description = organization.value.description || ''
    form.type = organization.value.type
    form.logo_url = organization.value.logo_url
    form.parent_id = organization.value.parent_id
    
    // Set color from saved values or default
    if (organization.value.color_chroma !== null && organization.value.color_hue !== null) {
        // Use a fixed luminance for editing representation, e.g. 0.6
        form.color_hex = oklchToHex(0.6, organization.value.color_chroma, organization.value.color_hue)
    }
    
    // Check permissions
    const permResponse = await api.get(`/organizations/${route.params.id}/can-edit`)
    if (!permResponse.data.can_edit) {
      error.value = "Vous n'avez pas la permission de modifier cette organisation"
    }
  } catch (err) {
    console.error('Failed to load organization:', err)
    error.value = err.response?.data?.detail || 'Échec du chargement de l\'organisation'
  }
}

const updateOrg = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Generate slug from name if changed
    if (!form.slug || form.slug !== organization.value.slug) {
      form.slug = form.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    }
    
    // Convert hex back to OKLCH
    const oklch = hexToOklch(form.color_hex)
    const payload = {
        ...form,
        color_chroma: oklch ? oklch.C : null,
        color_hue: oklch ? oklch.h : null
    }

    await api.put(`/organizations/${route.params.id}`, payload)
    router.push(`/organizations/${route.params.id}`)
  } catch (err) {
    console.error('Failed to update organization:', err)
    error.value = err.response?.data?.detail || 'Échec de la mise à jour de l\'organisation'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOrganization()
  loadParentOrganizations()
})
</script>
