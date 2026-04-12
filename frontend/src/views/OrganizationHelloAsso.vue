<template>
  <div class="max-w-2xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Connexion HelloAsso</h1>
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

          <!-- Webhook URL -->
          <div v-if="status.webhook_url" class="rounded-lg border border-gray-200 p-4">
            <p class="text-sm font-medium text-gray-900 mb-1">URL de webhook</p>
            <p class="text-xs text-gray-500 mb-2">
              Copiez cette URL dans votre espace HelloAsso (<strong>Paramètres → API → Notifications</strong>) pour recevoir les confirmations de paiement.
            </p>
            <div class="flex items-center gap-2">
              <code class="flex-1 text-xs bg-gray-50 border border-gray-200 rounded px-3 py-2 break-all select-all">{{ status.webhook_url }}</code>
              <button
                @click="copyWebhookUrl"
                class="flex-shrink-0 px-3 py-2 text-xs font-medium rounded-md bg-gray-100 hover:bg-gray-200 transition-colors"
                :title="copied ? 'Copié !' : 'Copier'"
              >
                {{ copied ? '✓' : 'Copier' }}
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
              Les identifiants chiffrés seront supprimés. Les formulaires de paiement déjà approuvés resteront visibles.
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
            :disabled="!rejectMessage || processingFormId"
            class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 disabled:opacity-50"
          >
            Refuser
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CheckCircleIcon, ExclamationCircleIcon, LinkIcon } from '@heroicons/vue/24/outline'
import api from '../utils/api'

const route = useRoute()
const orgId = route.params.id

const organization = ref(null)
const status = ref(null)
const pendingForms = ref([])
const eventTitles = ref({})
const loading = ref(true)
const error = ref('')
const success = ref('')
const saving = ref(false)
const deleting = ref(false)
const processingFormId = ref(null)
const showRejectDialog = ref(false)
const rejectMessage = ref('')
const formToReject = ref(null)

const copied = ref(false)

const form = ref({
  helloasso_slug: '',
  api_client_id: '',
  api_client_secret: '',
})

// For update (connected state): require at least slug + client_id
const canSave = computed(() =>
  form.value.helloasso_slug.trim() && form.value.api_client_id.trim()
)
// For new connection: all three fields required
const canSaveNew = computed(() =>
  form.value.helloasso_slug.trim() && form.value.api_client_id.trim() && form.value.api_client_secret.trim()
)

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })

const copyWebhookUrl = async () => {
  try {
    await navigator.clipboard.writeText(status.value?.webhook_url || '')
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback: select the text for manual copy
  }
}

const loadOrganization = async () => {
  try {
    const res = await api.get(`/organizations/${orgId}`)
    organization.value = res.data
  } catch (err) {
    console.error('Failed to load organization:', err)
  }
}

const loadStatus = async () => {
  try {
    const res = await api.get(`/helloasso/status/${orgId}`)
    status.value = res.data
    if (res.data.helloasso_slug) {
      form.value.helloasso_slug = res.data.helloasso_slug
    }
    if (res.data.api_client_id) {
      form.value.api_client_id = res.data.api_client_id
    }
  } catch (err) {
    console.error('Failed to load HelloAsso status:', err)
  }
}

const loadPendingForms = async () => {
  try {
    const res = await api.get(`/helloasso/pending-forms/${orgId}`)
    pendingForms.value = res.data
    for (const f of res.data) {
      if (!eventTitles.value[f.event_id]) {
        try {
          const eventRes = await api.get(`/events/${f.event_id}`)
          eventTitles.value[f.event_id] = eventRes.data.title
        } catch {
          eventTitles.value[f.event_id] = 'Événement inconnu'
        }
      }
    }
  } catch (err) {
    if (err.response?.status !== 403) {
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
    await api.put(`/helloasso/credentials/${orgId}`, payload)
    form.value.api_client_secret = ''
    await loadStatus()
    success.value = 'Identifiants HelloAsso enregistrés.'
    setTimeout(() => { success.value = '' }, 4000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible d\'enregistrer les identifiants'
  } finally {
    saving.value = false
  }
}

const deleteCredentials = async () => {
  if (!confirm('Supprimer les identifiants HelloAsso ? Les membres ne pourront plus initier de paiements.')) return
  deleting.value = true
  error.value = ''
  try {
    await api.delete(`/helloasso/credentials/${orgId}`)
    form.value = { helloasso_slug: '', api_client_id: '', api_client_secret: '' }
    await loadStatus()
    success.value = 'Identifiants supprimés.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de supprimer les identifiants'
  } finally {
    deleting.value = false
  }
}

const approveForm = async (f) => {
  processingFormId.value = f.id
  error.value = ''
  try {
    await api.post(`/helloasso/events/${f.event_id}/payment-form/approve`)
    await loadPendingForms()
    success.value = 'Formulaire approuvé.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible d\'approuver le formulaire'
  } finally {
    processingFormId.value = null
  }
}

const openRejectDialog = (f) => {
  formToReject.value = f
  rejectMessage.value = ''
  showRejectDialog.value = true
}

const confirmReject = async () => {
  if (!formToReject.value || !rejectMessage.value) return
  processingFormId.value = formToReject.value.id
  error.value = ''
  try {
    await api.post(`/helloasso/events/${formToReject.value.event_id}/payment-form/reject`, {
      rejection_message: rejectMessage.value
    })
    showRejectDialog.value = false
    rejectMessage.value = ''
    formToReject.value = null
    await loadPendingForms()
    success.value = 'Formulaire refusé.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Impossible de refuser le formulaire'
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
