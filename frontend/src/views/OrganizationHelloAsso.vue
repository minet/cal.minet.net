<template>
  <div class="max-w-2xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <DocsHint path="/configurer-helloasso" search="Connecter HelloAsso">
          <h1 class="text-3xl font-bold tracking-tight text-gray-900">Connexion HelloAsso</h1>
        </DocsHint>
        <p class="mt-2 text-sm text-gray-600">{{ organization?.name }}</p>
      </div>
    </header>

    <div v-if="error" class="rounded-md bg-red-50 p-4 mb-6">
      <p class="text-sm text-red-800">{{ error }}</p>
    </div>

    <div v-if="success" class="rounded-md bg-green-50 p-4 mb-6">
      <p class="text-sm text-green-800">{{ success }}</p>
    </div>

    <div class="bg-white shadow-sm rounded-lg p-6">
      <div v-if="loading" class="text-center py-6">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <template v-else>
        <!-- Connected state -->
        <div v-if="status?.connected" class="space-y-6">
          <div class="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
            <CheckCircleIcon class="h-6 w-6 text-green-600 flex-shrink-0" />
            <div>
              <p class="text-sm font-medium text-green-900">Compte HelloAsso configuré</p>
              <p class="text-sm text-green-700">
                Slug : <code class="font-mono">{{ status.helloasso_slug }}</code>
                &nbsp;·&nbsp;
                Client ID : <code class="font-mono">{{ status.api_client_id }}</code>
              </p>
            </div>
          </div>

          <!-- Export checkouts -->
          <div class="border-t pt-4">
            <h3 class="text-sm font-medium text-gray-900 mb-3">Exporter les paiements</h3>
            <p class="text-xs text-gray-600 mb-3">Téléchargez un fichier ODS contenant tous les paiements de votre organisation et des organisations enfants sur la période sélectionnée.</p>
            <div class="space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Date début</label>
                  <input
                    v-model="exportDateStart"
                    type="date"
                    class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Date fin</label>
                  <input
                    v-model="exportDateEnd"
                    type="date"
                    class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                </div>
              </div>
              <button
                @click="downloadCheckoutsExport"
                :disabled="exportingCheckouts"
                class="w-full rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
              >
                {{ exportingCheckouts ? 'Téléchargement…' : 'Télécharger ODS' }}
              </button>
            </div>
          </div>

          <!-- Update credentials -->
          <div>
            <h3 class="text-sm font-medium text-gray-900 mb-3">Mettre à jour les identifiants</h3>
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Slug HelloAsso</label>
                <input
                  v-model="form.helloasso_slug"
                  type="text"
                  placeholder="ex: mon-association"
                  class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Client ID</label>
                <input
                  v-model="form.api_client_id"
                  type="text"
                  placeholder="Votre client_id HelloAsso"
                  class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Client Secret</label>
                <input
                  v-model="form.api_client_secret"
                  type="password"
                  placeholder="Laissez vide pour ne pas changer"
                  class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
                <p class="mt-1 text-xs text-gray-400">Le secret n'est jamais affiché. Entrez-en un nouveau pour le remplacer.</p>
              </div>
              <button
                @click="saveCredentials"
                :disabled="!canSave || saving"
                class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
              >
                {{ saving ? 'Enregistrement…' : 'Mettre à jour' }}
              </button>
            </div>
          </div>

          <!-- Disconnect -->
          <div class="border-t pt-4">
            <button
              @click="deleteCredentials"
              :disabled="deleting"
              class="rounded-md bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 ring-1 ring-inset ring-red-300 hover:bg-red-100 disabled:opacity-50 transition-colors"
            >
              Supprimer les identifiants HelloAsso
            </button>
            <p class="mt-1 text-xs text-gray-500">
              Les identifiants chiffrés seront supprimés. Les formulaires de paiement déjà approuvés resteront visibles mais ne pourront plus être utilisés pour initier ou valider de nouveaux paiements.
            </p>
          </div>

        </div>

        <!-- Not connected state -->
        <div v-else class="space-y-6">
          <div class="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
            <ExclamationCircleIcon class="h-6 w-6 text-gray-400 flex-shrink-0" />
            <div>
              <p class="text-sm font-medium text-gray-900">Aucun compte HelloAsso configuré</p>
              <p class="text-sm text-gray-500">
                Renseignez les clés API de votre organisation HelloAsso pour permettre aux membres de proposer des formulaires de paiement.
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-medium text-gray-900 mb-1">Où trouver vos clés API ?</h3>
            <ul class="list-disc list-inside text-sm text-gray-600 space-y-1">
              <li>Connectez-vous à votre espace HelloAsso</li>
              <li>Rendez-vous dans <strong>Paramètres → API</strong></li>
              <li>Créez une application et copiez le <em>client_id</em> et le <em>client_secret</em></li>
              <li>Notez votre slug : visible dans l'URL de votre espace HelloAsso</li>
            </ul>
          </div>

          <!-- New credentials form -->
          <div class="space-y-3">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Slug HelloAsso</label>
              <input
                v-model="form.helloasso_slug"
                type="text"
                placeholder="ex: mon-association"
                class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Client ID</label>
              <input
                v-model="form.api_client_id"
                type="text"
                placeholder="Votre client_id HelloAsso"
                class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Client Secret</label>
              <input
                v-model="form.api_client_secret"
                type="password"
                placeholder="Votre client_secret HelloAsso"
                class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              />
            </div>
            <button
              @click="saveCredentials"
              :disabled="!canSaveNew || saving"
              class="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 transition-colors"
            >
              <LinkIcon class="h-4 w-4" />
              {{ saving ? 'Vérification…' : 'Enregistrer les identifiants' }}
            </button>
            <p class="text-xs text-gray-400">Les identifiants seront validés puis chiffrés avant stockage.</p>
          </div>
        </div>
      </template>
    </div>

    <!-- Pending forms from child orgs -->
    <div v-if="pendingForms.length > 0" class="bg-white shadow-sm rounded-lg p-6 mt-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">
        Formulaires en attente de validation
        <span class="ml-2 inline-flex items-center rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-800">
          {{ pendingForms.length }}
        </span>
      </h2>

      <ul class="divide-y divide-gray-200">
        <li v-for="form in pendingForms" :key="form.id" class="py-4">
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <router-link
                :to="`/events/${form.event_id}`"
                class="text-sm font-medium text-indigo-600 hover:underline truncate block"
              >
                {{ eventTitles[form.event_id] || form.event_id }}
              </router-link>
              <p class="text-sm text-gray-600">{{ form.item_name }} — {{ (form.total_amount_cents / 100).toFixed(2) }}&nbsp;€</p>
              <p class="text-xs text-gray-400 mt-0.5">Proposé le {{ formatDate(form.created_at) }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button
                @click="approveForm(form)"
                :disabled="processingFormId === form.id"
                class="rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-500 disabled:opacity-50 transition-colors"
              >
                Approuver
              </button>
              <button
                @click="openRejectDialog(form)"
                :disabled="processingFormId === form.id"
                class="rounded-md bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-700 ring-1 ring-inset ring-red-300 hover:bg-red-100 disabled:opacity-50 transition-colors"
              >
                Refuser
              </button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Reject dialog -->
    <div v-if="showRejectDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Motif du refus</h3>
        <textarea
          v-model="rejectMessage"
          rows="4"
          placeholder="Expliquez pourquoi ce formulaire est refusé..."
          class="block w-full rounded-md border-0 px-3 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
        />
        <div class="mt-4 flex justify-end gap-3">
          <button
            @click="showRejectDialog = false; rejectMessage = ''"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          >
            Annuler
          </button>
          <button
            @click="confirmReject"
            :disabled="!rejectMessage || !!processingFormId"
            class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 disabled:opacity-50"
          >
            Refuser
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CheckCircleIcon, ExclamationCircleIcon, LinkIcon } from '@heroicons/vue/24/outline'
import { api, httpClient } from '@/api'
import type { HelloAssoStatus, OrganizationRead, PaymentFormRead } from '@/api/types'

const route = useRoute()
const orgId = route.params.id as string

const organization = ref<OrganizationRead | null>(null)
const status = ref<HelloAssoStatus | null>(null)
const pendingForms = ref<PaymentFormRead[]>([])
const eventTitles = ref<Record<string, string>>({})
const loading = ref(true)
const error = ref('')
const success = ref('')
const saving = ref(false)
const deleting = ref(false)
const processingFormId = ref<string | null>(null)
const showRejectDialog = ref(false)
const rejectMessage = ref('')
const formToReject = ref<PaymentFormRead | null>(null)

const form = ref({
  helloasso_slug: '',
  api_client_id: '',
  api_client_secret: '',
})

// Export state
const exportDateStart = ref('')
const exportDateEnd = ref('')
const exportingCheckouts = ref(false)

// For update (connected state): require at least slug + client_id
const canSave = computed(() =>
  form.value.helloasso_slug.trim() && form.value.api_client_id.trim()
)
// For new connection: all three fields required
const canSaveNew = computed(() =>
  form.value.helloasso_slug.trim() && form.value.api_client_id.trim() && form.value.api_client_secret.trim()
)

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })

// Initialize default dates (current academic year: Aug 15 -> Aug 15)
const initializeExportDates = () => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const aug15ThisYear = new Date(currentYear, 7, 15) // August 15 (month is 0-indexed)

  let startDate
  let endDate
  if (now < aug15ThisYear) {
    startDate = new Date(currentYear - 1, 7, 15)
    endDate = aug15ThisYear
  } else {
    startDate = aug15ThisYear
    endDate = new Date(currentYear + 1, 7, 15)
  }

  exportDateStart.value = startDate.toISOString().split('T')[0]
  exportDateEnd.value = endDate.toISOString().split('T')[0]
}

const downloadCheckoutsExport = async () => {
  if (exportingCheckouts.value) return
  exportingCheckouts.value = true
  error.value = ''
  try {
    const params: { date_start?: string; date_end?: string } = {}
    if (exportDateStart.value) params.date_start = exportDateStart.value
    if (exportDateEnd.value) params.date_end = exportDateEnd.value
    
    const responseData = await api.helloasso.export_checkouts(orgId, params)
    
    // Create a download link and trigger download
    const url = window.URL.createObjectURL(responseData)
    const link = document.createElement('a')
    link.href = url
    
    let filename = 'checkouts.ods'
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    success.value = 'Export téléchargé avec succès.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de télécharger l\'export'
  } finally {
    exportingCheckouts.value = false
  }
}

const loadOrganization = async () => {
  try {
    organization.value = await api.organizations.get_organization(orgId)
  } catch (err) {
    console.error('Failed to load organization:', err)
  }
}

const loadStatus = async () => {
  try {
    const res = await api.helloasso.helloasso_status(orgId)
    status.value = res
    if (res.helloasso_slug) {
      form.value.helloasso_slug = res.helloasso_slug
    }
    if (res.api_client_id) {
      form.value.api_client_id = res.api_client_id
    }
    // Initialize export dates when status is loaded and connected
    if (res.connected) {
      initializeExportDates()
    }
  } catch (err) {
    console.error('Failed to load HelloAsso status:', err)
  }
}

const loadPendingForms = async () => {
  try {
    const res = await api.helloasso.get_pending_forms(orgId)
    pendingForms.value = res
    for (const f of res) {
      if (!eventTitles.value[f.event_id]) {
        try {
          const eventRes = await api.events.get_event(f.event_id)
          eventTitles.value[f.event_id] = eventRes.title
        } catch {
          eventTitles.value[f.event_id] = 'Événement inconnu'
        }
      }
    }
  } catch (err) {
    if ((err as { response?: { status?: number } })?.response?.status !== 403) {
      console.error('Failed to load pending forms:', err)
    }
  }
}

const saveCredentials = async () => {
  if (!canSave.value && !canSaveNew.value) return
  saving.value = true
  error.value = ''
  try {
    const payload = {
      helloasso_slug: form.value.helloasso_slug.trim(),
      api_client_id: form.value.api_client_id.trim(),
      api_client_secret: form.value.api_client_secret.trim(),
    }
    // If updating and secret is empty, we can't submit (server requires it for validation)
    if (!payload.api_client_secret) {
      error.value = 'Le client secret est requis pour valider les identifiants.'
      return
    }
    await api.helloasso.set_credentials(orgId, payload)
    form.value.api_client_secret = ''
    await loadStatus()
    success.value = 'Identifiants HelloAsso enregistrés.'
    setTimeout(() => { success.value = '' }, 4000)
  } catch (err) {
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible d\'enregistrer les identifiants'
  } finally {
    saving.value = false
  }
}

const deleteCredentials = async () => {
  const msg =
    'Supprimer les identifiants HelloAsso ?\n\n' +
    'Les membres ne pourront plus initier de paiements. ' +
    'Tous les formulaires de paiement actifs de cette organisation seront automatiquement fermés.'

  if (!confirm(msg)) return
  deleting.value = true
  error.value = ''
  try {
    const res = await api.helloasso.delete_credentials(orgId)
    form.value = { helloasso_slug: '', api_client_id: '', api_client_secret: '' }
    await loadStatus()

    let resultMsg = 'Identifiants supprimés.'
    if (res.forms_closed > 0) {
      resultMsg += ` ${res.forms_closed} formulaire(s) de paiement ont été fermés.`
    }
    success.value = resultMsg
    setTimeout(() => {
      success.value = ''
    }, 5000)
    alert(resultMsg)
  } catch (err) {
    error.value =
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      'Impossible de supprimer les identifiants'
  } finally {
    deleting.value = false
  }
}

const approveForm = async (f: PaymentFormRead) => {
  processingFormId.value = f.id
  error.value = ''
  try {
    await api.helloasso.approve_payment_form(f.event_id)
    await loadPendingForms()
    success.value = 'Formulaire approuvé.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible d\'approuver le formulaire'
  } finally {
    processingFormId.value = null
  }
}

const openRejectDialog = (f: PaymentFormRead) => {
  formToReject.value = f
  rejectMessage.value = ''
  showRejectDialog.value = true
}

const confirmReject = async () => {
  if (!formToReject.value || !rejectMessage.value) return
  processingFormId.value = formToReject.value.id
  error.value = ''
  try {
    await api.helloasso.reject_payment_form(formToReject.value.event_id, {
      rejection_message: rejectMessage.value
    })
    showRejectDialog.value = false
    rejectMessage.value = ''
    formToReject.value = null
    await loadPendingForms()
    success.value = 'Formulaire refusé.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Impossible de refuser le formulaire'
  } finally {
    processingFormId.value = null
  }
}

onMounted(async () => {
  await Promise.all([loadOrganization(), loadStatus()])
  loading.value = false
  loadPendingForms()
})
</script>
