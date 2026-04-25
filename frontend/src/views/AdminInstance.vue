<template>
  <div class="px-4 py-6 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Options de l'instance</h1>
        <p class="mt-2 text-sm text-gray-700">Gérez les paramètres globaux de l'instance et exportez des données.</p>
      </div>
    </div>

    <div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- LDAP Sync Section -->
      <div class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-base font-semibold leading-6 text-gray-900">Synchronisation LDAP</h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <p>Mettez à jour la base de données des utilisateurs à partir du LDAP et nettoyez les comptes orphelins (RGPD).</p>
          </div>
          <div class="mt-5">
            <button @click="showSyncModal = true" type="button"
              class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
              <ArrowPathIcon class="-ml-0.5 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
              Synchroniser LDAP
            </button>
          </div>
        </div>
      </div>

      <!-- Export Section -->
      <div class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-base font-semibold leading-6 text-gray-900">Export des événements</h3>
          <div class="mt-2 max-w-xl text-sm text-gray-500">
            <p>Exportez tous les événements publics approuvés entre deux dates au format ODS (LibreOffice Calc).</p>
          </div>
          <div class="mt-5 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div class="relative">
              <label for="start_date" class="block text-sm font-medium text-gray-700 mb-1 flex items-center">
                <CalendarIcon class="h-4 w-4 mr-1.5 text-gray-400" />
                Date de début
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <input type="date" v-model="exportForm.start_date" id="start_date"
                  class="block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 transition-all hover:ring-gray-400" />
              </div>
            </div>
            <div class="relative">
              <label for="end_date" class="block text-sm font-medium text-gray-700 mb-1 flex items-center">
                <CalendarIcon class="h-4 w-4 mr-1.5 text-gray-400" />
                Date de fin
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <input type="date" v-model="exportForm.end_date" id="end_date"
                  class="block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 transition-all hover:ring-gray-400" />
              </div>
            </div>
          </div>
          <div class="mt-6 flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100">
            <div class="flex items-center text-sm text-gray-600">
              <DocumentTextIcon class="h-5 w-5 mr-2 text-indigo-500" />
              <span>Format: ODS (LibreOffice / Excel)</span>
            </div>
            <button @click="handleExport" :disabled="exporting || !exportForm.start_date || !exportForm.end_date" type="button"
              class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 transition-all active:scale-95">
              <DocumentArrowDownIcon class="-ml-0.5 mr-2 h-5 w-5" aria-hidden="true" />
              {{ exporting ? 'Export en cours...' : 'Générer l\'export' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Changelog Section -->
    <div class="mt-8">
      <div class="sm:flex sm:items-center mb-4">
        <div class="sm:flex-auto">
          <h2 class="text-lg font-semibold text-gray-900">Changelog</h2>
          <p class="mt-1 text-sm text-gray-500">Gérez les messages de nouveautés affichés aux utilisateurs.</p>
        </div>
        <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button @click="openCreateModal" type="button"
            class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            <PlusIcon class="-ml-0.5 mr-1.5 h-5 w-5" />
            Nouveau message
          </button>
        </div>
      </div>

      <div class="bg-white shadow sm:rounded-lg overflow-hidden">
        <div v-if="loadingChangelogs" class="px-6 py-10 text-center text-sm text-gray-400">Chargement...</div>
        <div v-else-if="changelogEntries.length === 0" class="px-6 py-10 text-center text-sm text-gray-400">
          Aucun message pour l'instant.
        </div>
        <table v-else class="min-w-full divide-y divide-gray-300">
          <thead class="bg-gray-50">
            <tr>
              <th class="py-3 pl-4 pr-3 text-left text-xs font-semibold text-gray-900 sm:pl-6">Titre</th>
              <th class="px-3 py-3 text-left text-xs font-semibold text-gray-900">Audience</th>
              <th class="px-3 py-3 text-left text-xs font-semibold text-gray-900">Date</th>
              <th class="relative py-3 pl-3 pr-4 sm:pr-6"><span class="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="entry in changelogEntries" :key="entry.id">
              <td class="py-3 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{ entry.title }}</td>
              <td class="whitespace-nowrap px-3 py-3 text-sm text-gray-500">{{ audienceLabel(entry.audience) }}</td>
              <td class="whitespace-nowrap px-3 py-3 text-sm text-gray-500">{{ formatDate(entry.created_at) }}</td>
              <td class="whitespace-nowrap py-3 pl-3 pr-4 text-right text-sm font-medium sm:pr-6 space-x-3">
                <button @click="openEditModal(entry)" class="text-indigo-600 hover:text-indigo-900">Modifier</button>
                <button @click="deleteEntry(entry.id)" class="text-red-600 hover:text-red-900">Supprimer</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Changelog Create/Edit Modal -->
    <TransitionRoot as="template" :show="showChangelogModal">
      <Dialog as="div" class="relative z-50" @close="showChangelogModal = false">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>
        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4">
            <TransitionChild as="template" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel class="relative w-full max-w-2xl transform rounded-lg bg-white p-6 shadow-xl transition-all">
                <DialogTitle as="h3" class="text-base font-semibold text-gray-900 mb-4">
                  {{ editingEntry ? 'Modifier le message' : 'Nouveau message' }}
                </DialogTitle>

                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Titre</label>
                    <input v-model="changelogForm.title" type="text"
                      class="block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm" />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Audience</label>
                    <select v-model="changelogForm.audience"
                      class="block w-full rounded-md border-0 py-2 px-3 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm">
                      <option value="all">Tout le monde</option>
                      <option value="org_viewer_plus">Membres d'au moins une organisation</option>
                      <option value="org_member_plus">Membres actifs (éditeur ou admin)</option>
                      <option value="org_admin_plus">Admins d'organisation uniquement</option>
                      <option value="treasury">Accès trésorerie uniquement</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Contenu (Markdown)</label>
                    <div class="flex items-center gap-2 mb-2 p-2 bg-gray-50 rounded-t-lg border border-b-0 border-gray-200">
                      <label class="flex items-center gap-1 cursor-pointer text-xs font-medium text-indigo-600 hover:text-indigo-800 px-2 py-1 rounded border border-gray-200 bg-white hover:bg-gray-50 transition-colors">
                        <PhotoIcon class="h-4 w-4" />
                        Ajouter une image
                        <input type="file" accept="image/*" class="hidden" @change="uploadChangelogImage" ref="changelogFileInput" />
                      </label>
                      <span v-if="uploadingImage" class="text-xs text-gray-400">Envoi...</span>
                    </div>
                    <textarea v-model="changelogForm.content" rows="10"
                      class="block w-full rounded-b-lg border border-gray-200 px-3 py-2 text-gray-900 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm font-mono leading-relaxed resize-y" />
                    <p class="mt-1 text-xs text-gray-400">
                      Syntaxe : <code>**gras**</code>, <code>*italique*</code>, <code>- liste</code>, <code>![alt](url)</code>
                    </p>
                  </div>
                </div>

                <div class="mt-6 flex justify-end gap-3">
                  <button type="button" @click="showChangelogModal = false"
                    class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    Annuler
                  </button>
                  <button type="button" @click="saveEntry" :disabled="savingEntry"
                    class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50">
                    {{ savingEntry ? 'Enregistrement...' : 'Enregistrer' }}
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
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel
                class="relative transform rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                    <ArrowPathIcon class="h-6 w-6 text-indigo-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Synchroniser LDAP
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">Mettre à jour la base de données des utilisateurs à partir du
                        serveur LDAP de l'école. Entrez vos identifiants scolaires (ils ne seront pas stockés, seulement utilisés une fois pour importer les données) :</p>
                      <div class="mt-4 space-y-4 text-left">
                        <TextInput v-model="syncForm.username" label="LDAP Username (uid)" placeholder="uid" />
                        <TextInput v-model="syncForm.password" label="LDAP Password" type="password" />
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 sm:col-start-2"
                    @click="syncLdap" :disabled="syncing">
                    {{ syncing ? 'Synchronisation...' : 'Synchroniser' }}
                  </button>
                  <button type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="showSyncModal = false">
                    Annuler
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Orphans Modal -->
    <TransitionRoot as="template" :show="showOrphansModal">
      <Dialog as="div" class="relative z-50" @close="closeOrphansModal">
        <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="template" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel
                class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
                <div>
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                    <TrashIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      Comptes orphelins détectés
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500 mb-4 text-left">
                        Les utilisateurs suivants ne sont plus présents dans l'annuaire et ne sont pas exemptés. S'il
                        s'agit d'étudiants, il faut les supprimer pour respecter le RGPD. Attention à ne pas supprimer
                        les membres de l'administration. Pour éviter de faire cette erreur, vous pouvez aller dans leur
                        page d'utilisateur et activer l'option <strong>"Utilisateur permanent"</strong>.
                      </p>
                      <div class="max-h-60 overflow-y-auto ring-1 ring-black ring-opacity-5 sm:rounded-lg">
                        <table class="min-w-full divide-y divide-gray-300 text-left">
                          <thead class="bg-gray-50 sticky top-0">
                            <tr>
                              <th class="py-2 pl-4 pr-3 text-sm font-semibold text-gray-900">Email</th>
                              <th class="px-3 py-2 text-sm font-semibold text-gray-900">Nom</th>
                              <th class="px-3 py-2 text-right text-sm font-semibold text-gray-900">Action</th>
                            </tr>
                          </thead>
                          <tbody class="divide-y divide-gray-200 bg-white">
                            <tr v-for="orphan in orphanedUsers" :key="orphan.id">
                              <td class="whitespace-nowrap py-2 pl-4 pr-3 text-sm text-gray-500">{{ orphan.email }}</td>
                              <td class="whitespace-nowrap px-3 py-2 text-sm text-gray-500">{{ orphan.full_name || 'N/A'
                              }}</td>
                              <td class="relative whitespace-nowrap py-2 pl-3 pr-4 text-right text-sm font-medium">
                                <button @click="deleteOrphan(orphan.id)" :disabled="deletingOrphans.includes(orphan.id)"
                                  class="text-red-600 hover:text-red-900 disabled:opacity-50">
                                  {{ deletingOrphans.includes(orphan.id) ? 'Suppression...' : 'Supprimer' }}
                                </button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:col-start-2 disabled:opacity-50"
                    @click="deleteAllOrphans" :disabled="isDeletingAllOrphans || orphanedUsers.length === 0">
                    {{ isDeletingAllOrphans ? 'En cours...' : 'Tout supprimer' }}
                  </button>
                  <button type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="closeOrphansModal">
                    Fermer
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

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'
import type { ChangelogAudience, ChangelogEntryRead, UserRead } from '@/api/types'
import TextInput from '../components/TextInput.vue'
import {
  Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot
} from '@headlessui/vue'
import { ArrowPathIcon, DocumentArrowDownIcon, TrashIcon, CalendarIcon, DocumentTextIcon, PlusIcon, PhotoIcon } from '@heroicons/vue/24/outline'

// LDAP Sync State
const showSyncModal = ref(false)
const showOrphansModal = ref(false)
const syncing = ref(false)
const syncForm = ref({ username: '', password: '' })
const orphanedUsers = ref<UserRead[]>([])
const deletingOrphans = ref<string[]>([])
const isDeletingAllOrphans = ref(false)

// Calculate default date range: last August 15th to next August 15th
const now = new Date()
let startYear = now.getFullYear()
// If we are before August 15th of the current year, the "last" August 15th was in the previous year
if (now.getMonth() < 7 || (now.getMonth() === 7 && now.getDate() < 15)) {
  startYear--
}
const defaultStart = new Date(startYear, 7, 15) // August is index 7
const defaultEnd = new Date(startYear + 1, 7, 15)

// Export State
const exporting = ref(false)
const exportForm = ref({
  start_date: defaultStart.toISOString().split('T')[0],
  end_date: defaultEnd.toISOString().split('T')[0]
})

const syncLdap = async () => {
  if (!syncForm.value.username || !syncForm.value.password) return
  syncing.value = true
  try {
    const housekeepingResponse = await api.admin.housekeeping()
    console.log(housekeepingResponse.message)

    await api.admin.sync_ldap_users(syncForm.value)

    // Reset form and close first modal
    showSyncModal.value = false
    syncForm.value.password = ''

    // Now look for orphaned users
    orphanedUsers.value = await api.admin.get_ldap_orphaned_users()

    if (orphanedUsers.value.length > 0) {
      showOrphansModal.value = true
    } else {
      alert('Synchronisation et nettoyage réussis. Aucun compte orphelin trouvé.')
    }
  } catch (e: unknown) {
    console.error(e)
    const detail = (e as any).response?.data?.detail || (e as Error).message
    alert('Erreur: ' + detail)
  } finally {
    syncing.value = false
  }
}

const closeOrphansModal = () => {
  showOrphansModal.value = false
}

const deleteOrphan = async (id: string) => {
  deletingOrphans.value.push(id)
  try {
    await api.users.delete_user(id)
    orphanedUsers.value = orphanedUsers.value.filter(u => u.id !== id)
    if (orphanedUsers.value.length === 0) {
      alert('Tous les comptes orphelins ont été supprimés.')
      closeOrphansModal()
    }
  } catch (error: unknown) {
    console.error('Failed to delete user', error)
    alert('Failed to delete user: ' + ((error as any).response?.data?.detail || (error as Error).message))
  } finally {
    deletingOrphans.value = deletingOrphans.value.filter(i => i !== id)
  }
}

const deleteAllOrphans = async () => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer tous ces utilisateurs ?')) return

  isDeletingAllOrphans.value = true
  const currentOrphans = [...orphanedUsers.value]

  for (const orphan of currentOrphans) {
    await deleteOrphan(orphan.id)
  }

  isDeletingAllOrphans.value = false
}

const handleExport = async () => {
  if (!exportForm.value.start_date || !exportForm.value.end_date) return
  
  exporting.value = true
  try {
    const blob = await api.events.export({
      start_date: new Date(exportForm.value.start_date).toISOString(),
      end_date: new Date(exportForm.value.end_date).toISOString()
    })

    // Create a download link for the blob
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `export_evenements_${exportForm.value.start_date}_${exportForm.value.end_date}.ods`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Export failed:', error)
    alert('Erreur lors de l\'exportation des événements')
  } finally {
    exporting.value = false
  }
}

// ─── Changelog ────────────────────────────────────────────────────────────────

const changelogEntries = ref<ChangelogEntryRead[]>([])
const loadingChangelogs = ref(false)
const showChangelogModal = ref(false)
const editingEntry = ref<ChangelogEntryRead | null>(null)
const savingEntry = ref(false)
const uploadingImage = ref(false)
const changelogFileInput = ref<HTMLInputElement | null>(null)

const changelogForm = ref({
  title: '',
  content: '',
  audience: 'all' as ChangelogAudience,
  image_urls: [] as string[],
})

const loadChangelogs = async () => {
  loadingChangelogs.value = true
  try {
    changelogEntries.value = await api.changelog.list()
  } catch (e) {
    console.error(e)
  } finally {
    loadingChangelogs.value = false
  }
}

onMounted(loadChangelogs)

const openCreateModal = () => {
  editingEntry.value = null
  changelogForm.value = { title: '', content: '', audience: 'all', image_urls: [] }
  showChangelogModal.value = true
}

const openEditModal = (entry: ChangelogEntryRead) => {
  editingEntry.value = entry
  changelogForm.value = {
    title: entry.title,
    content: entry.content,
    audience: entry.audience,
    image_urls: entry.image_urls ? [...entry.image_urls] : [],
  }
  showChangelogModal.value = true
}

const saveEntry = async () => {
  if (!changelogForm.value.title.trim() || !changelogForm.value.content.trim()) return
  savingEntry.value = true
  try {
    const payload = {
      title: changelogForm.value.title,
      content: changelogForm.value.content,
      audience: changelogForm.value.audience,
      image_urls: changelogForm.value.image_urls.length > 0 ? changelogForm.value.image_urls : undefined,
    }
    if (editingEntry.value) {
      const updated = await api.changelog.update(editingEntry.value.id, payload)
      const idx = changelogEntries.value.findIndex(e => e.id === editingEntry.value!.id)
      if (idx >= 0) changelogEntries.value[idx] = updated
    } else {
      const created = await api.changelog.create(payload)
      changelogEntries.value.unshift(created)
    }
    showChangelogModal.value = false
  } catch (e: any) {
    alert('Erreur: ' + (e.response?.data?.detail || e.message))
  } finally {
    savingEntry.value = false
  }
}

const deleteEntry = async (id: string) => {
  if (!confirm('Supprimer ce message de changelog ?')) return
  try {
    await api.changelog.delete(id)
    changelogEntries.value = changelogEntries.value.filter(e => e.id !== id)
  } catch (e: any) {
    alert('Erreur: ' + (e.response?.data?.detail || e.message))
  }
}

const uploadChangelogImage = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.upload.upload_image(formData)
    changelogForm.value.image_urls.push(res.url)
    const altName = file.name.replace(/\.[^.]+$/, '')
    changelogForm.value.content += `\n![${altName}](${res.url})\n`
  } catch (e: any) {
    alert("Erreur lors de l'upload: " + (e.response?.data?.detail || e.message))
  } finally {
    uploadingImage.value = false
    if (changelogFileInput.value) changelogFileInput.value.value = ''
  }
}

const audienceLabel = (audience: ChangelogAudience) => {
  const labels: Record<ChangelogAudience, string> = {
    all: 'Tous',
    org_viewer_plus: 'Membres',
    org_member_plus: 'Éditeurs+',
    org_admin_plus: 'Admins',
    treasury: 'Trésorerie',
  }
  return labels[audience] ?? audience
}

const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
</script>
