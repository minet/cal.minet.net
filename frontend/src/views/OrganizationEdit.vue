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

              
              <div class="col-span-full">
                <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">Liens personnalisés</label>
                <div class="space-y-3">
                  <div v-for="(link, index) in links" :key="index" class="grid grid-cols-1 gap-3 sm:flex sm:items-center">
                    <div class="hidden sm:block flex-none cursor-move text-gray-400">
                      <span class="text-xs">{{ index + 1 }}.</span>
                    </div>
                    <input 
                      v-model="link.name" 
                      type="text" 
                      placeholder="Nom (ex: Site web)" 
                      class="block w-full sm:w-1/3 rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    />
                    <input 
                      v-model="link.url" 
                      type="url" 
                      placeholder="URL (https://...)" 
                      class="block w-full sm:flex-1 rounded-md border-0 py-1.5 pl-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    />
                    <button type="button" @click="removeLink(index)" class="inline-flex items-center justify-center p-2 text-sm text-red-600 hover:text-red-800 sm:w-auto border border-red-200 rounded sm:border-0">
                      <TrashIcon class="h-5 w-5" />
                      <span class="ml-2 sm:hidden">Supprimer</span>
                    </button>
                  </div>
                  <button type="button" @click="addLink" class="text-sm text-indigo-600 hover:text-indigo-800 font-semibold flex items-center">
                    <PlusIcon class="h-4 w-4 mr-1" /> Ajouter un lien
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-col-reverse sm:flex-row items-center justify-end gap-x-6 gap-y-3 sm:gap-y-0">
          <router-link 
            :to="`/organizations/${organization.id}`"
            class="w-full text-center sm:w-auto text-sm font-semibold leading-6 text-gray-900"
          >
            Annuler
          </router-link>
          <button 
            type="submit" 
            :disabled="loading"
            class="w-full sm:w-auto rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
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
import { TrashIcon, PlusIcon } from '@heroicons/vue/24/outline'

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
const links = ref([])
const deletedLinkIds = ref([])

const addLink = () => {
  links.value.push({ name: '', url: '', order: links.value.length + 1 })
}

const removeLink = (index) => {
  const link = links.value[index]
  if (link.id) {
    deletedLinkIds.value.push(link.id)
  }
  links.value.splice(index, 1)
}

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
    
    // Load links
    if (organization.value.organization_links) {
        links.value = organization.value.organization_links.map(l => ({...l}))
    } else {
        links.value = []
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
    
    // Handle links
    // 1. Delete removed links
    for (const id of deletedLinkIds.value) {
        await api.delete(`/organization-links/${id}`)
    }
    
    // 2. Add/Update links
    for (const [index, link] of links.value.entries()) {
        const linkData = { ...link, order: index + 1 }
        if (link.id) {
            await api.put(`/organization-links/${link.id}`, linkData)
        } else {
            if (link.name && link.url) {
                await api.post(`/organizations/${route.params.id}/links`, linkData)
            }
        }
    }

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
