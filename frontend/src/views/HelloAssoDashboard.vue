<template>
  <div class="max-w-5xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex items-center gap-3">
        <CreditCardIcon class="h-7 w-7 text-green-600" />
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-gray-900">Paiements HelloAsso</h1>
          <p class="text-sm text-gray-500 mt-0.5">Formulaires de paiement de vos organisations</p>
        </div>
      </div>
    </header>

    <div v-if="loading" class="bg-white shadow-sm rounded-lg p-8 text-center text-sm text-gray-500">
      Chargement…
    </div>

    <div v-else-if="items.length === 0" class="bg-white shadow-sm rounded-lg p-8 text-center text-sm text-gray-500">
      Aucun formulaire de paiement pour vos organisations.
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="bg-white shadow-sm rounded-lg overflow-hidden"
      >
        <!-- Card header -->
        <div class="px-5 py-4 flex items-start gap-4 border-b border-gray-100">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <router-link :to="`/events/${item.event_id}`" class="text-sm font-semibold text-indigo-600 hover:underline truncate">
                {{ item.event_title }}
              </router-link>
              <span class="text-xs text-gray-400">·</span>
              <span class="text-xs text-gray-500">{{ item.org_name }}</span>
              <span class="text-xs text-gray-400">·</span>
              <span class="text-xs text-gray-500">{{ formatDate(item.event_start_time) }}</span>
            </div>
            <p class="text-sm text-gray-700 mt-0.5">
              {{ item.item_name }}
              <span class="font-semibold">{{ (item.total_amount_cents / 100).toFixed(2) }}&nbsp;€</span>
              <template v-if="item.options?.length">
                <span class="text-gray-400"> + {{ item.options.length }} option(s)</span>
              </template>
            </p>
          </div>

          <!-- Status badge -->
          <span class="shrink-0 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
            :class="{
              'bg-amber-100 text-amber-800': item.status === 'pending',
              'bg-green-100 text-green-800': item.status === 'approved',
              'bg-red-100 text-red-800': item.status === 'rejected',
            }"
          >
            {{ statusLabel(item.status) }}
          </span>
        </div>

        <!-- Card body -->
        <div class="px-5 py-3 flex flex-wrap items-center gap-x-6 gap-y-2">
          <!-- Entry stats -->
          <div v-if="item.status === 'approved'" class="flex items-center gap-4 text-sm text-gray-600">
            <span>
              <span class="font-semibold text-gray-900">{{ item.completed_count }}</span>
              paiement(s) complété(s)
            </span>
            <span class="text-gray-400">·</span>
            <span>
              <span class="font-semibold text-gray-900">{{ item.entry_count }}</span>
              initié(s)
            </span>
          </div>

          <!-- Actions -->
          <div class="ml-auto flex items-center gap-2 flex-wrap">
            <!-- Open/close toggle (approved only) -->
            <template v-if="item.status === 'approved'">
              <button
                @click="toggleOpen(item)"
                class="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
                :class="item.is_open
                  ? 'bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-300 hover:bg-amber-100'
                  : 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-300 hover:bg-green-100'"
              >
                <LockClosedIcon v-if="item.is_open" class="h-3.5 w-3.5" />
                <LockOpenIcon v-else class="h-3.5 w-3.5" />
                {{ item.is_open ? 'Fermer les paiements' : 'Rouvrir les paiements' }}
              </button>
            </template>

            <!-- Edit options -->
            <button
              v-if="item.status !== 'rejected'"
              @click="openEditModal(item)"
              class="flex items-center gap-1.5 rounded-md bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-100 transition-colors"
            >
              <PencilIcon class="h-3.5 w-3.5" />
              Options
            </button>

            <!-- Approve/reject (pending) -->
            <template v-if="item.status === 'pending'">
              <button
                @click="approveForm(item)"
                :disabled="processingId === item.id"
                class="rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-500 disabled:opacity-50 transition-colors"
              >
                Approuver
              </button>
              <button
                @click="openRejectModal(item)"
                :disabled="processingId === item.id"
                class="rounded-md bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-700 ring-1 ring-inset ring-red-300 hover:bg-red-100 disabled:opacity-50 transition-colors"
              >
                Refuser
              </button>
            </template>

            <!-- View entries -->
            <button
              v-if="item.status === 'approved' && item.entry_count > 0"
              @click="toggleEntries(item.id)"
              class="flex items-center gap-1.5 rounded-md bg-gray-50 px-3 py-1.5 text-xs font-semibold text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-100 transition-colors"
            >
              <UsersIcon class="h-3.5 w-3.5" />
              Inscrits
            </button>
          </div>
        </div>

        <!-- Options list -->
        <div v-if="item.options?.length" class="px-5 pb-3">
          <div class="flex flex-wrap gap-2">
            <span
              v-for="opt in item.options"
              :key="opt.name"
              class="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs text-indigo-700 ring-1 ring-inset ring-indigo-200"
            >
              {{ opt.name }} +{{ (opt.price_cents / 100).toFixed(2) }}&nbsp;€
            </span>
          </div>
        </div>

        <!-- Entries table -->
        <div v-if="expandedEntries[item.id]" class="border-t border-gray-100 bg-gray-50 px-5 py-3">
          <div v-if="loadingEntries[item.id]" class="text-xs text-gray-500 py-2">Chargement…</div>
          <table v-else-if="entries[item.id]?.length" class="w-full text-xs text-gray-700">
            <thead>
              <tr class="text-left text-gray-400 border-b border-gray-200">
                <th class="pb-1.5 font-medium">Participant</th>
                <th class="pb-1.5 font-medium">Montant</th>
                <th class="pb-1.5 font-medium">Options choisies</th>
                <th class="pb-1.5 font-medium">Statut</th>
                <th class="pb-1.5 font-medium">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="entry in entries[item.id]" :key="entry.id" class="py-1">
                <td class="py-1.5 pr-4">{{ entry.user_name || entry.user_id }}</td>
                <td class="py-1.5 pr-4">{{ (entry.amount_cents / 100).toFixed(2) }}&nbsp;€</td>
                <td class="py-1.5 pr-4">
                  <template v-if="entry.selected_option_indices?.length">
                    {{ entry.selected_option_indices.map(i => item.options[i]?.name).filter(Boolean).join(', ') }}
                  </template>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <td class="py-1.5 pr-4">
                  <span :class="entry.completed ? 'text-green-600 font-medium' : 'text-amber-600'">
                    {{ entry.completed ? 'Payé' : 'En attente' }}
                  </span>
                </td>
                <td class="py-1.5 text-gray-400">{{ formatDate(entry.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-xs text-gray-400 py-2">Aucune entrée.</p>
        </div>
      </div>
    </div>

    <!-- Edit options modal -->
    <div v-if="editModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Modifier les options</h3>
        <p class="text-sm text-gray-500 mb-1">{{ editModal.item?.item_name }} — {{ (editModal.item?.total_amount_cents / 100).toFixed(2) }}&nbsp;€</p>

        <!-- is_open toggle -->
        <div class="flex items-center justify-between py-3 border-b border-gray-100 mb-4">
          <span class="text-sm text-gray-700">Paiements ouverts</span>
          <button
            @click="editModal.is_open = !editModal.is_open"
            type="button"
            class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors"
            :class="editModal.is_open ? 'bg-green-500' : 'bg-gray-200'"
          >
            <span class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
              :class="editModal.is_open ? 'translate-x-4' : 'translate-x-0'" />
          </button>
        </div>

        <!-- Options -->
        <div class="space-y-4 mb-4">
          <div v-for="(opt, idx) in editModal.options" :key="idx" class="flex flex-col gap-2 p-3 border border-gray-100 rounded-lg bg-gray-50">
            <div class="flex items-center gap-2">
              <input v-model="opt.name" type="text" placeholder="Nom de l'option"
                class="flex-1 rounded-md border-0 py-1.5 pl-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600" />
              <div class="flex items-center gap-1">
                <span class="text-sm text-gray-500">+/-</span>
                <input v-model.number="opt.amount_euros" type="number" step="0.01" placeholder="2.00"
                  class="w-20 rounded-md border-0 py-1.5 pl-3 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600" />
                <span class="text-sm text-gray-500">€</span>
              </div>
              <button type="button" @click="editModal.options.splice(idx, 1)" class="text-red-400 hover:text-red-600">
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>
            
            <!-- Private Option Config -->
            <div class="flex items-center gap-2">
              <input type="checkbox" v-model="opt.is_private" :id="'dash-priv-' + idx" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
              <label :for="'dash-priv-' + idx" class="text-sm text-gray-600">Option privée</label>
            </div>
            
            <div v-if="opt.is_private" class="mt-2">
              <label class="block text-xs font-medium text-gray-700 mb-1">Personnes autorisées (Collez une liste de noms ou emails, un par ligne)</label>
              <textarea 
                v-model="opt.allowed_user_names" 
                rows="3" 
                placeholder="Jean Dupont&#10;jean.dupont@telecom-sudparis.eu"
                class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">Actuellement {{ opt.allowed_user_ids?.length || 0 }} personne(s) autorisée(s).</p>
            </div>
          </div>
          <button type="button" @click="editModal.options.push({ name: '', amount_euros: '', is_private: false, allowed_user_names: '', allowed_user_ids: [] })"
            class="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700">
            <PlusIcon class="h-4 w-4" />
            Ajouter une option
          </button>
        </div>

        <div class="flex justify-end gap-3">
          <button @click="editModal.open = false"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            Annuler
          </button>
          <button @click="saveEditModal" :disabled="savingEdit"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">
            {{ savingEdit ? 'Enregistrement…' : 'Enregistrer' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Reject modal -->
    <div v-if="rejectModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-3">Motif du refus</h3>
        <textarea v-model="rejectModal.message" rows="4" placeholder="Expliquez pourquoi ce formulaire est refusé…"
          class="block w-full rounded-md border-0 px-3 py-2 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600" />
        <div class="mt-4 flex justify-end gap-3">
          <button @click="rejectModal.open = false"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            Annuler
          </button>
          <button @click="confirmReject" :disabled="!rejectModal.message || processingId"
            class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:opacity-50">
            Refuser
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import {
  CreditCardIcon,
  LockClosedIcon,
  LockOpenIcon,
  PencilIcon,
  UsersIcon,
  XMarkIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'
import api from '../utils/api'

const items = ref([])
const loading = ref(true)
const processingId = ref(null)
const expandedEntries = reactive({})
const loadingEntries = reactive({})
const entries = reactive({})

const editModal = ref({ open: false, item: null, options: [], is_open: true })
const savingEdit = ref(false)
const rejectModal = ref({ open: false, item: null, message: '' })

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })

const statusLabel = (status) => ({
  pending: 'En attente',
  approved: 'Approuvé',
  rejected: 'Refusé',
}[status] ?? status)

const loadItems = async () => {
  loading.value = true
  try {
    const res = await api.get('/helloasso/my-payment-forms')
    items.value = res.data
  } catch (err) {
    console.error('Failed to load payment forms:', err)
  } finally {
    loading.value = false
  }
}

const toggleOpen = async (item) => {
  processingId.value = item.id
  try {
    const res = await api.put(`/helloasso/events/${item.event_id}/payment-form`, {
      is_open: !item.is_open,
    })
    const updated = res.data
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx].is_open = updated.is_open
  } catch (err) {
    console.error('Toggle open failed:', err)
  } finally {
    processingId.value = null
  }
}

const resolveUserNames = async (namesStr, eventId) => {
  if (!namesStr || !namesStr.trim()) return []
  const queries = namesStr.split('\n').map(n => n.trim()).filter(Boolean)
  if (!queries.length) return []
  
  try {
    const res = await api.post(`/helloasso/events/${eventId}/attendee-bulk-resolve`, { queries })
    return res.data.filter(r => r.user_id).map(r => r.user_id)
  } catch (err) {
    console.error('Bulk resolve failed:', err)
    return []
  }
}

const openEditModal = (item) => {
  editModal.value = {
    open: true,
    item,
    is_open: item.is_open,
    options: (item.options || []).map(o => ({ 
      name: o.name, 
      amount_euros: o.price_cents / 100,
      is_private: o.is_private || false,
      allowed_user_ids: o.allowed_user_ids || [],
      allowed_user_names: '',
    })),
  }
}

const saveEditModal = async () => {
  savingEdit.value = true
  try {
    const optionsToSave = []
    for (const o of editModal.value.options) {
      if (!o.name || o.amount_euros === '' || o.amount_euros === null) continue
      
      let finalUserIds = [...(o.allowed_user_ids || [])]
      if (o.is_private && o.allowed_user_names) {
        const resolvedIds = await resolveUserNames(o.allowed_user_names, editModal.value.item.event_id)
        finalUserIds = [...new Set([...finalUserIds, ...resolvedIds])]
      }
      
      optionsToSave.push({
        name: o.name,
        price_cents: Math.round(o.amount_euros * 100),
        is_private: o.is_private || false,
        allowed_user_ids: finalUserIds
      })
    }

    const res = await api.put(`/helloasso/events/${editModal.value.item.event_id}/payment-form`, {
      options: optionsToSave,
      is_open: editModal.value.is_open,
    })
    const idx = items.value.findIndex(i => i.id === editModal.value.item.id)
    if (idx !== -1) {
      items.value[idx].options = res.data.options
      items.value[idx].is_open = res.data.is_open
    }
    editModal.value.open = false
  } catch (err) {
    console.error('Save options failed:', err)
  } finally {
    savingEdit.value = false
  }
}

const approveForm = async (item) => {
  processingId.value = item.id
  try {
    await api.post(`/helloasso/events/${item.event_id}/payment-form/approve`)
    await loadItems()
  } catch (err) {
    console.error('Approve failed:', err)
  } finally {
    processingId.value = null
  }
}

const openRejectModal = (item) => {
  rejectModal.value = { open: true, item, message: '' }
}

const confirmReject = async () => {
  if (!rejectModal.value.message) return
  processingId.value = rejectModal.value.item.id
  try {
    await api.post(`/helloasso/events/${rejectModal.value.item.event_id}/payment-form/reject`, {
      rejection_message: rejectModal.value.message,
    })
    rejectModal.value.open = false
    await loadItems()
  } catch (err) {
    console.error('Reject failed:', err)
  } finally {
    processingId.value = null
  }
}

const toggleEntries = async (formId) => {
  if (expandedEntries[formId]) {
    expandedEntries[formId] = false
    return
  }
  expandedEntries[formId] = true
  if (entries[formId]) return

  loadingEntries[formId] = true
  try {
    const item = items.value.find(i => i.id === formId)
    const res = await api.get(`/helloasso/events/${item.event_id}/payment-form/entries`)
    entries[formId] = res.data
  } catch (err) {
    console.error('Failed to load entries:', err)
    entries[formId] = []
  } finally {
    loadingEntries[formId] = false
  }
}

onMounted(loadItems)
</script>
