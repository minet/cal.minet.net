<template>
  <div class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Utilisateurs</h1>
        <p class="mt-2 text-sm text-gray-700">Gérez les utilisateurs de l'application.</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none flex gap-2">
        <button @click="showSyncModal = true" type="button" class="block rounded-md bg-white px-3 py-2 text-center text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
          <ArrowPathIcon class="-ml-0.5 mr-1.5 h-5 w-5 inline-block text-gray-400" aria-hidden="true" />
          Sync LDAP
        </button>
        <button @click="showInviteModal = true" type="button" class="block w-full sm:w-auto rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          Inviter un utilisateur
        </button>
      </div>
    </div>

    <!-- Search -->
    <div class="mt-6 flex sm:justify-start">
        <div class="relative rounded-md shadow-sm max-w-sm w-full">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
            </div>
            <input type="text" v-model="searchQuery" class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="Rechercher un utilisateur..." />
        </div>
    </div>
    
    <!-- Users List -->
    <div class="mt-8 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <table class="min-w-full divide-y divide-gray-300">
            <thead>
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">Nom</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Email</th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Rôle</th>
                <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 cursor-pointer" @click="openUser(user.id)">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">
                  <div class="flex items-center">
                    <UserAvatar :src="user.profile_picture_url" :name="user.full_name || user.email" size="sm" class="mr-3"/>
                    {{ user.full_name || 'Jamais connecté' }}
                  </div>
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ user.email }}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  <span v-if="user.is_superadmin" class="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-700/10">Superadmin</span>
                  <span v-else class="inline-flex items-center rounded-md bg-gray-50 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Utilisateur</span>
                </td>
                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                  <span class="text-indigo-600 hover:text-indigo-900">Voir<span class="sr-only">, {{ user.full_name }}</span></span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
      <div class="flex flex-1 justify-between sm:hidden">
        <button @click="changePage(page - 1)" :disabled="page <= 1" class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">Précédent</button>
        <button @click="changePage(page + 1)" :disabled="page >= pages" class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">Suivant</button>
      </div>
      <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            Affichage de
            <span class="font-medium">{{ (page - 1) * size + 1 }}</span>
            à
            <span class="font-medium">{{ Math.min(page * size, total) }}</span>
            sur
            <span class="font-medium">{{ total }}</span>
            résultats
          </p>
        </div>
        <div>
          <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
            <button @click="changePage(page - 1)" :disabled="page <= 1" class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed">
              <span class="sr-only">Précédent</span>
              <ChevronLeftIcon class="h-5 w-5" aria-hidden="true" />
            </button>
            <button @click="changePage(page + 1)" :disabled="page >= pages" class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed">
              <span class="sr-only">Suivant</span>
              <ChevronRightIcon class="h-5 w-5" aria-hidden="true" />
            </button>
          </nav>
        </div>
      </div>
    </div>

    <!-- Invite Modal -->
    <TransitionRoot as="template" :show="showInviteModal">
      <Dialog as="div" class="relative z-50" @close="showInviteModal = false">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                    <UserPlusIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Inviter un utilisateur</DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">Recherchez un utilisateur dans l'annuaire LDAP ou saisissez un email.</p>
                      <div class="mt-4 space-y-4 text-left">
                        <Combobox as="div" v-model="selectedLdapUser" @update:modelValue="onLdapUserSelect">
                          <ComboboxLabel class="block text-sm font-medium leading-6 text-gray-900">Rechercher LDAP</ComboboxLabel>
                          <div class="relative mt-2">
                            <ComboboxInput class="w-full rounded-md border-0 bg-white py-1.5 pl-3 pr-10 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" @change="ldapQuery = $event.target.value" :displayValue="(user) => user?.full_name" placeholder="Nom, email ou uid..." />
                            <ComboboxButton class="absolute inset-y-0 right-0 flex items-center px-2">
                              <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                            </ComboboxButton>

                            <ComboboxOptions v-if="ldapUsers.length > 0" class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                              <ComboboxOption v-for="user in ldapUsers" :key="user.id" :value="user" as="template" v-slot="{ active, selected }">
                                <li :class="['relative cursor-default select-none py-2 pl-3 pr-9', active ? 'bg-indigo-600 text-white' : 'text-gray-900']">
                                  <div class="flex flex-col">
                                    <span :class="['block truncate', selected && 'font-semibold']">
                                      {{ user.full_name }}
                                    </span>
                                    <span :class="['block truncate text-xs', active ? 'text-indigo-200' : 'text-gray-500']">
                                      {{ user.email }} ({{ user.uid }})
                                    </span>
                                  </div>

                                  <span v-if="selected" :class="['absolute inset-y-0 right-0 flex items-center pr-4', active ? 'text-white' : 'text-indigo-600']">
                                    <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                  </span>
                                </li>
                              </ComboboxOption>
                            </ComboboxOptions>
                          </div>
                        </Combobox>

                        <TextInput v-model="inviteForm.email" label="Email (invitation)" type="email" placeholder="email@exemple.com" />
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2" @click="inviteUser" :disabled="inviting">
                    {{ inviting ? 'Envoi...' : 'Inviter' }}
                  </button>
                  <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0" @click="showInviteModal = false" ref="cancelButtonRef">
                    Annuler
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Sync Modal -->
    <TransitionRoot as="template" :show="showSyncModal">
      <Dialog as="div" class="relative z-50" @close="showSyncModal = false">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                    <ArrowPathIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Synchroniser LDAP</DialogTitle>
                    <div class="mt-2">
                       <p class="text-sm text-gray-500">Mettre à jour la base de données des utilisateurs à partir du LDAP.</p>
                       <div class="mt-4 space-y-4 text-left">
                         <TextInput v-model="syncForm.username" label="LDAP Username (uid)" placeholder="uid" />
                         <TextInput v-model="syncForm.password" label="LDAP Password" type="password" />
                       </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="button" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2" @click="syncLdap" :disabled="syncing">
                    {{ syncing ? 'Synchronisation...' : 'Synchroniser' }}
                  </button>
                  <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0" @click="showSyncModal = false">
                    Annuler
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import UserAvatar from '../components/UserAvatar.vue'
import TextInput from '../components/TextInput.vue'
import { 
  Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot,
  Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption, ComboboxLabel
} from '@headlessui/vue'
import { UserPlusIcon, ArrowPathIcon, CheckIcon, ChevronUpDownIcon, ChevronLeftIcon, ChevronRightIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const users = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const pages = ref(0)
const searchQuery = ref('')
const showInviteModal = ref(false)
const showSyncModal = ref(false)

const syncing = ref(false)
const syncForm = ref({ username: '', password: '' })

const inviting = ref(false)
const inviteForm = ref({
  email: ''
})

// LDAP Search
const ldapQuery = ref('')
const ldapUsers = ref([])
const selectedLdapUser = ref(null)

watch(ldapQuery, async (newQuery) => {
  if (newQuery.length < 2) {
    ldapUsers.value = []
    return
  }
  try {
    const response = await api.get('/admin/ldap/users', { params: { q: newQuery } })
    ldapUsers.value = response.data
  } catch (error) {
    console.error('LDAP search error', error)
  }
})

const onLdapUserSelect = (user) => {
  if (user) {
    inviteForm.value.email = user.email
  }
}

const syncLdap = async () => {
    if(!syncForm.value.username || !syncForm.value.password) return
    syncing.value = true
    try {
        await api.post('/admin/ldap/sync', syncForm.value)
        showSyncModal.value = false
        alert('Synchronisation réussie')
        
        // Reset form
        syncForm.value.password = ''
    } catch (e) {
        console.error(e)
        // Extract error details safely
        const detail = e.response?.data?.detail || e.message
        alert('Erreur: ' + detail)
    } finally {
        syncing.value = false
    }
}

const loadUsers = async () => {
  try {
    const params = {
      page: page.value,
      size: size.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    const response = await api.get('/users/', { params })
    users.value = response.data.items
    total.value = response.data.total
    pages.value = response.data.pages
  } catch (error) {
    console.error('Failed to load users', error)
  }
}

let searchTimeout = null
watch(searchQuery, () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadUsers()
  }, 300)
})

const changePage = (newPage) => {
  if (newPage < 1 || newPage > pages.value) return
  page.value = newPage
  loadUsers()
}

const openUser = (id) => {
  router.push(`/users/${id}`)
}

const inviteUser = async () => {
  if (!inviteForm.value.email) return
  
  inviting.value = true
  try {
    const response = await api.post('/users/invite', inviteForm.value)
    showInviteModal.value = false
    // Navigate to the user page
    router.push(`/users/${response.data.id}`)
  } catch (error) {
    console.error('Failed to invite user', error)
    alert('Erreur lors de l\'invitation')
  } finally {
    inviting.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>
