<template>
  <div class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Utilisateurs</h1>
        <p class="mt-2 text-sm text-gray-700">Gérez les utilisateurs de l'application.</p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button @click="showInviteModal = true" type="button" class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
          Inviter un utilisateur
        </button>
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
                    {{ user.full_name || 'Sans nom' }}
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

    <!-- Invite Modal -->
    <TransitionRoot as="template" :show="showInviteModal">
      <Dialog as="div" class="relative z-50" @close="showInviteModal = false">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                    <UserPlusIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Inviter un utilisateur</DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">Un email sera envoyé à l'utilisateur avec ses identifiants de connexion.</p>
                      <div class="mt-4 space-y-4 text-left">
                        <TextInput v-model="inviteForm.email" label="Email" type="email" placeholder="email@exemple.com" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import UserAvatar from '../components/UserAvatar.vue'
import TextInput from '../components/TextInput.vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { UserPlusIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const users = ref([])
const showInviteModal = ref(false)
const inviting = ref(false)
const inviteForm = ref({
  email: ''
})

const loadUsers = async () => {
  try {
    const response = await api.get('/users/')
    users.value = response.data
  } catch (error) {
    console.error('Failed to load users', error)
  }
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
