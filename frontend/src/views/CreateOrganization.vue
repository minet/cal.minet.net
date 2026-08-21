<template>
  <div class="max-w-2xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <DocsHint path="/creer-une-organisation" search="Créer une organisation">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Create Organization</h1>
        </DocsHint>
      </div>
    </header>

    <div class="bg-white shadow-sm rounded-lg p-6">
      <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>
      
      <form @submit.prevent="createOrg">
        <div class="space-y-12">
          <div class="border-b border-gray-900/10 pb-12">
            <div class="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
              <div class="sm:col-span-4">
                <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Organization Name</label>
                <div class="mt-2">
                  <div class="flex rounded-md shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
                    <input type="text" name="name" id="name" v-model="form.name" class="block flex-1 border-0 bg-transparent py-1.5 pl-3 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6" placeholder="BDE" />
                  </div>
                </div>
              </div>

              <div class="col-span-full">
                <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">Description</label>
                <OrgDescriptionEditor
                  v-model="form.description"
                  placeholder="Description de l'organisation..."
                  :rows="6"
                />
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
                  hint="Sélectionnez une organisation parente pour créer une sous-organisation."
                />
              </div>

              <div class="col-span-full border border-gray-200 rounded-md p-4">
                <div class="flex h-6 items-center flex-row">
                  <input
                    id="enableDeleteAfter"
                    name="enableDeleteAfter"
                    type="checkbox"
                    v-model="enableDeleteAfter"
                    class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                  />
                  <div class="ml-3 text-sm leading-6">
                    <label for="enableDeleteAfter" class="font-medium text-gray-900">Suppression automatique</label>
                    <p class="text-gray-500">Si activé, l'organisation sera supprimée automatiquement après la date indiquée.</p>
                  </div>
                </div>

                <div v-if="enableDeleteAfter" class="mt-4">
                    <label for="delete_after" class="block text-sm font-medium leading-6 text-gray-900">Date de suppression</label>
                    <div class="mt-2 text-gray-600">
                        <input
                            type="datetime-local"
                            id="delete_after"
                            required
                            v-model="form.delete_after"
                            class="block rounded-md border-0 py-1.5 px-3 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                        />
                    </div>
                </div>
              </div>

              <div class="col-span-full">
                <ImageUpload v-model="form.logo_url" @update:stored-file-id="id => form.logo_file_id = id" label="Logo de l'organisation (optionnel)" crop />
              </div>
            </div>
          </div>
        </div>

        <div class="mt-6 flex flex-col-reverse sm:flex-row items-center justify-end gap-x-6 gap-y-3 sm:gap-y-0">
          <router-link to="/organizations" class="w-full text-center sm:w-auto text-sm font-semibold leading-6 text-gray-900">Cancel</router-link>
          <button type="submit" :disabled="loading" class="w-full sm:w-auto rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50">
            {{ loading ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import ImageUpload from '../components/ImageUpload.vue'
import Dropdown from '../components/Dropdown.vue'
import OrgDescriptionEditor from '../components/OrgDescriptionEditor.vue'
import { api } from '@/api'
import { OrganizationType } from '@/api/types'
import type { OrganizationRead } from '@/api/types'

const router = useRouter()
const { user } = useAuth()

const form = reactive<{
  name: string
  slug: string
  description: string
  type: OrganizationType
  logo_url: string | null
  logo_file_id: string | null
  parent_id: string | null
  delete_after: string | null
}>({
  name: '',
  slug: '',
  description: '',
  type: OrganizationType.ASSOCIATION,
  logo_url: null,
  logo_file_id: null,
  parent_id: null,
  delete_after: null
})

const enableDeleteAfter = ref(false)

const parentOrganizations = ref<OrganizationRead[]>([])
const error = ref('')
const loading = ref(false)

const loadParentOrganizations = async () => {
  if (!user.value?.is_superadmin) {
    router.push('/organizations')
    return
  }

  try {
    parentOrganizations.value = await api.organizations.list_organizations()
  } catch (err) {
    console.error('Failed to load parent organizations:', err)
  }
}

const createOrg = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // Generate slug from name
    form.slug = form.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
    
    await api.organizations.create_organization({
      name: form.name,
      slug: form.slug || undefined,
      description: form.description || undefined,
      type: form.type,
      parent_id: form.parent_id ?? undefined,
      logo_file_id: form.logo_file_id ?? undefined,
    })
    router.push('/organizations')
  } catch (err) {
    console.error('Failed to create organization:', err)
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Échec de la création de l\'organisation'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadParentOrganizations()
})
</script>
