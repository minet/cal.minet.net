<template>
  <div class="max-w-2xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Create Organization</h1>
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
                <label for="description" class="block text-sm font-medium leading-6 text-gray-900">Description</label>
                <div class="mt-2">
                  <textarea id="description" name="description" rows="3" v-model="form.description" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
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
                  hint="Sélectionnez une organisation parente pour créer une sous-organisation."
                />
              </div>

              <div class="col-span-full">
                <ImageUpload v-model="form.logo_url" label="Logo de l'organisation (optionnel)" />
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

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import ImageUpload from '../components/ImageUpload.vue'
import Dropdown from '../components/Dropdown.vue'
import api from '../utils/api'

const router = useRouter()
const { user } = useAuth()

const form = reactive({
  name: '',
  slug: '',
  description: '',
  type: 'association',
  logo_url: null,
  parent_id: null
})

const parentOrganizations = ref([])
const error = ref('')
const loading = ref(false)

const loadParentOrganizations = async () => {
  if (!user.value?.is_superadmin) {
    router.push('/organizations')
    return
  }

  try {
    const response = await api.get('/organizations/')
    parentOrganizations.value = response.data
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
    
    await api.post('/organizations/', form)
    router.push('/organizations')
  } catch (err) {
    console.error('Failed to create organization:', err)
    error.value = err.response?.data?.detail || 'Échec de la création de l\'organisation'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadParentOrganizations()
})
</script>
