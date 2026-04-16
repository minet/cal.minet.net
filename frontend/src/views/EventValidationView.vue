<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-2xl mx-auto px-4 py-6">
      <!-- Header -->
      <div class="flex items-center gap-3 mb-6">
        <router-link :to="`/events/${eventId}`" class="text-gray-400 hover:text-gray-600">
          <ArrowLeftIcon class="h-5 w-5" />
        </router-link>
        <div class="flex-1 min-w-0">
          <h1 class="text-xl font-bold text-gray-900 truncate">Validation — {{ eventTitle }}</h1>
          <p class="text-xs text-gray-400 mt-0.5">
            {{ validated }}/{{ total }} validés
            <span v-if="completed < total" class="ml-2 text-amber-500">· {{ total - completed }} en attente de paiement</span>
          </p>
        </div>
        <button
          @click="openManualForm()"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
        >
          <PlusIcon class="h-4 w-4" />
          Manuel
        </button>
      </div>

      <!-- Search -->
      <div class="relative mb-4">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
        <input
          ref="searchRef"
          v-model="search"
          @keydown.enter="handleEnter"
          @keydown.escape="search = ''"
          type="search"
          placeholder="Nom, prénom ou email… (Entrée pour valider)"
          class="w-full pl-10 pr-4 py-3 text-base rounded-xl border border-gray-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          autocomplete="off"
          autofocus
        />
        <span v-if="search && filtered.length === 1" class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-indigo-500 font-medium">
          Appuyez sur Entrée ↵
        </span>
      </div>

      <!-- Manual entry panel -->
      <div v-if="showManualForm" class="mb-4 bg-white rounded-xl border border-gray-200 shadow-sm">
        <!-- Panel header -->
        <div class="flex items-center justify-between px-4 pt-4 pb-3 border-b border-gray-100">
          <h3 class="text-sm font-semibold text-gray-700">Ajouter une entrée manuelle</h3>
          <button @click="closeManualForm" class="text-gray-400 hover:text-gray-600 p-1 rounded">
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>

        <div class="p-4 space-y-4">
          <!-- Person search -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Personne</label>
            <div class="relative">
              <UserIcon class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
              <input
                ref="personSearchRef"
                v-model="personQuery"
                @input="debouncedPersonSearch"
                @keydown.escape="personResults = []; personQuery = ''; selectedPerson = null"
                type="text"
                :placeholder="selectedPerson ? '' : 'Rechercher un nom, prénom ou email…'"
                class="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-400"
                autocomplete="off"
              />
            </div>

            <!-- Person results dropdown -->
            <div v-if="personResults.length" class="mt-1 rounded-lg border border-gray-200 bg-white shadow-md overflow-hidden">
              <button
                v-for="person in personResults"
                :key="person.email || person.full_name || undefined"
                @click="selectPerson(person)"
                class="w-full flex items-center gap-3 px-3 py-2 hover:bg-indigo-50 text-left transition-colors"
              >
                <div class="flex-shrink-0 h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="person.source === 'user' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600'">
                  {{ initials(person.full_name || person.email) }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ person.full_name || person.email }}</p>
                  <p v-if="person.full_name && person.email" class="text-xs text-gray-400 truncate">{{ person.email }}</p>
                </div>
                <span class="flex-shrink-0 text-xs px-1.5 py-0.5 rounded-full"
                  :class="person.source === 'user' ? 'bg-indigo-50 text-indigo-600' : 'bg-gray-100 text-gray-500'">
                  {{ person.source === 'user' ? 'Compte' : 'Annuaire' }}
                </span>
              </button>
            </div>

            <!-- Selected person chip -->
            <div v-if="selectedPerson" class="mt-2 flex items-center gap-2 bg-indigo-50 rounded-lg px-3 py-2">
              <div class="h-6 w-6 rounded-full bg-indigo-200 flex items-center justify-center text-xs font-bold text-indigo-700">
                {{ initials(selectedPerson.full_name || selectedPerson.email) }}
              </div>
              <span class="text-sm font-medium text-indigo-900 flex-1 truncate">
                {{ selectedPerson.full_name || selectedPerson.email }}
                <span v-if="selectedPerson.email && selectedPerson.full_name" class="text-indigo-500 font-normal"> — {{ selectedPerson.email }}</span>
              </span>
              <button @click="clearPerson" class="text-indigo-400 hover:text-indigo-700">
                <XMarkIcon class="h-4 w-4" />
              </button>
            </div>

            <!-- Custom name fallback -->
            <div v-if="!selectedPerson && !personResults.length && personQuery.length >= 2" class="mt-2">
              <button
                @click="useCustomName"
                class="w-full text-left text-sm text-gray-500 border border-dashed border-gray-300 rounded-lg px-3 py-2 hover:bg-gray-50 transition-colors"
              >
                Utiliser <span class="font-medium text-gray-800">« {{ personQuery }} »</span> comme nom libre
              </button>
            </div>
          </div>

          <!-- Price: clickable buttons -->
          <div v-if="formOptions !== null">
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Tarif de base</label>
            <div class="flex gap-2 flex-wrap">
              <button
                @click="useCustomPrice = false"
                class="px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors"
                :class="!useCustomPrice ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300'"
              >
                {{ (formBaseCents / 100).toFixed(2) }} €
              </button>
              <button
                @click="useCustomPrice = true"
                class="px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors"
                :class="useCustomPrice ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-200 hover:border-indigo-300'"
              >
                Autre…
              </button>
            </div>
            <div v-if="useCustomPrice" class="mt-2 flex items-center gap-2">
              <input
                v-model.number="customPriceEuros"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                class="w-28 px-3 py-1.5 text-sm rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
              <span class="text-sm text-gray-500">€</span>
            </div>

            <!-- Options -->
            <div v-if="formOptions.length" class="mt-3">
              <label class="block text-xs font-medium text-gray-600 mb-1.5">Options</label>
              <div class="space-y-1.5">
                <button
                  v-for="(opt, idx) in formOptions"
                  :key="opt.id || idx"
                  @click="toggleOption(opt)"
                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-colors text-left"
                  :class="selectedOptionIds.includes(String(opt.id))
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-900'
                    : 'bg-white border-gray-200 text-gray-700 hover:border-indigo-200'"
                >
                  <span class="flex-1">{{ opt.name }}</span>
                  <span class="font-medium" :class="selectedOptionIds.includes(String(opt.id)) ? 'text-indigo-600' : 'text-gray-500'">
                    +{{ (opt.price_cents / 100).toFixed(2) }} €
                  </span>
                  <span v-if="selectedOptionIds.includes(String(opt.id))" class="text-indigo-500">✓</span>
                </button>
              </div>
            </div>

            <!-- Total -->
            <p class="mt-3 text-xs text-gray-500">
              Total : <span class="font-semibold text-gray-800">{{ (computedTotal / 100).toFixed(2) }} €</span>
            </p>
          </div>

          <!-- Payment type pills -->
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1.5">Mode de paiement</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="type in manual_payment_type_options"
                :key="type"
                @click="manualPaymentType = type"
                class="px-3 py-1.5 rounded-full text-xs font-medium border transition-colors"
                :class="manualPaymentType === type
                  ? 'border-transparent text-white ' + PAYMENT_TYPE_BG[type]
                  : 'bg-white border-gray-200 text-gray-600 hover:border-gray-400'"
              >
                {{ PAYMENT_TYPE_LABELS[type] || type }}
              </button>
            </div>
          </div>

          <!-- Submit -->
          <button
            @click="submitManualEntry"
            :disabled="!attendeeName.trim() || submittingManual"
            class="w-full py-2 text-sm font-medium rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50 transition-colors"
          >
            {{ submittingManual ? 'Ajout…' : 'Ajouter' }}
          </button>
        </div>
      </div>

      <!-- Results -->
      <div v-if="loading" class="text-center text-gray-400 py-12">Chargement…</div>

      <div v-else-if="search && !filtered.length" class="text-center text-gray-400 py-8 text-sm">
        Aucune correspondance pour "{{ search }}"
      </div>

      <div v-else class="space-y-2">
        <TransitionGroup name="list">
          <div
            v-for="entry in displayedEntries"
            :key="entry.id"
            class="bg-white rounded-xl border shadow-sm px-4 py-3 flex items-center gap-3 transition-all"
            :class="entry.validated ? 'border-green-200 bg-green-50' : entry.completed ? 'border-gray-200' : 'border-amber-100 bg-amber-50/50'"
          >
            <!-- Status dot -->
            <div class="flex-shrink-0">
              <div v-if="entry.validated" class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircleIcon class="h-5 w-5 text-green-600" />
              </div>
              <div v-else-if="entry.completed" class="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                <CreditCardIcon class="h-5 w-5 text-gray-400" />
              </div>
              <div v-else class="h-8 w-8 rounded-full bg-amber-100 flex items-center justify-center">
                <ClockIcon class="h-5 w-5 text-amber-500" />
              </div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ entry.display_name }}</p>
              <p v-if="entry.user_email" class="text-xs text-gray-400 truncate">{{ entry.user_email }}</p>
              <div class="flex items-center gap-2 mt-0.5 flex-wrap">
                <span class="text-xs text-gray-600">{{ entry.item_name }}</span>
                <template v-if="entry.imported_options?.length">
                  <span v-for="opt in entry.imported_options" :key="opt.name" class="text-xs text-indigo-600">
                    {{ opt.amount_cents > 0 ? `+${opt.name} (+${(opt.amount_cents / 100).toFixed(2)} €)` : `+${opt.name}` }}
                  </span>
                </template>
                <template v-else>
                  <span v-for="opt in entry.selected_options" :key="opt.name" class="text-xs text-indigo-600">+{{ opt.name }}</span>
                </template>
                <span class="text-xs font-medium text-gray-700 ml-auto">{{ (entry.amount_cents / 100).toFixed(2) }}&nbsp;€</span>
                <PaymentTypeBadge :type="entry.payment_type" />
              </div>
            </div>

            <!-- Validate button -->
            <button
              v-if="entry.completed || entry.payment_type !== 'helloasso'"
              @click="toggleValidate(entry)"
              class="flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
              :class="entry.validated
                ? 'bg-green-100 text-green-700 hover:bg-red-50 hover:text-red-600'
                : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-700'"
            >
              {{ entry.validated ? 'Validé ✓' : 'Valider' }}
            </button>
            <span v-else class="flex-shrink-0 text-xs text-amber-500 font-medium">Non payé</span>

            <!-- Cancel button -->
            <button
              @click="cancelEntry(entry)"
              class="flex-shrink-0 px-2 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors"
              title="Annuler cette entrée"
            >
              <XMarkIcon class="h-4 w-4" />
            </button>
          </div>
        </TransitionGroup>

        <p v-if="!search && entries.length > 30" class="text-center text-xs text-gray-400 mt-4">
          {{ entries.length }} entrées — utilisez la recherche pour filtrer
        </p>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast" class="fixed bottom-6 left-1/2 -translate-x-1/2 bg-green-700 text-white text-sm font-medium px-5 py-3 rounded-full shadow-lg flex items-center gap-2 z-50">
        <CheckCircleIcon class="h-4 w-4" />
        {{ toast }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineComponent, h } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { api } from '@/api'
import type { EventRead, ManualEntryCreate, PaymentFormRead, ValidationEntryRead, AttendeeSearchResult, PaymentFormOption } from '@/api'
import { PaymentType } from '@/api'
import {
  MagnifyingGlassIcon,
  CheckCircleIcon,
  CreditCardIcon,
  ClockIcon,
  ArrowLeftIcon,
  PlusIcon,
  XMarkIcon,
  UserIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const eventId = String(route.params.id)

const loading = ref(true)
const entries = ref<ValidationEntryRead[]>([])
const eventTitle = ref('')
const search = ref('')
const searchRef = ref<HTMLInputElement | null>(null)
const toast = ref('')

// Manual panel state
const showManualForm = ref(false)
const submittingManual = ref(false)
const formOptions = ref<PaymentFormOption[]>([])
const formBaseCents = ref(0)

// Person search
const personQuery = ref('')
const personResults = ref<AttendeeSearchResult[]>([])
const selectedPerson = ref<AttendeeSearchResult | null>(null)
const personSearchRef = ref<HTMLInputElement | null>(null)
let personSearchTimer: ReturnType<typeof setTimeout> | undefined

// Price
const useCustomPrice = ref(false)
const customPriceEuros = ref<number>(0)
const selectedOptionIds = ref<string[]>([])

// Payment type
const manualPaymentType = ref('cash')

const PAYMENT_TYPE_LABELS: Record<string, string> = {
  cash: 'Espèces',
  credit_card: 'CB',
  cheque: 'Chèque',
  exchange: 'Échange',
  helloasso: 'HelloAsso',
  helloasso_import: 'HelloAsso (Externe)',
  none: 'Gratuit',
  other: 'Autre',
}
const manual_payment_type_options = Object.keys(PAYMENT_TYPE_LABELS).filter(t => t !== 'helloasso_import' && t !== 'helloasso')

const PAYMENT_TYPE_BG: Record<string, string> = {
  cash: 'bg-emerald-600',
  credit_card: 'bg-purple-600',
  cheque: 'bg-orange-600',
  exchange: 'bg-pink-600',
  helloasso: 'bg-blue-600',
  helloasso_import: 'bg-indigo-600',
  none: 'bg-gray-400',
  other: 'bg-gray-500',
}

const attendeeName = computed(() => {
  if (selectedPerson.value) return selectedPerson.value.full_name || selectedPerson.value.email || ''
  return personQuery.value.trim()
})

const computedTotal = computed(() => {
  const base = useCustomPrice.value
    ? Math.round((customPriceEuros.value || 0) * 100)
    : formBaseCents.value
  const optionById = Object.fromEntries((formOptions.value || []).map((o: PaymentFormOption) => [String(o.id), o]))
  const extras = selectedOptionIds.value.reduce((sum: number, optId: string) => {
    const opt = optionById[String(optId)]
    return sum + (opt?.price_cents || 0)
  }, 0)
  return base + extras
})

const initials = (name: string | null | undefined): string => {
  if (!name) return '?'
  return name.split(/\s+/).map((w: string) => w[0]).join('').slice(0, 2).toUpperCase()
}

const openManualForm = (prefill = '') => {
  showManualForm.value = true
  personQuery.value = prefill
  personResults.value = []
  selectedPerson.value = null
  useCustomPrice.value = false
  customPriceEuros.value = 0
  selectedOptionIds.value = []
  manualPaymentType.value = 'cash'
  if (prefill) debouncedPersonSearch()
}

const closeManualForm = () => {
  showManualForm.value = false
}

const debouncedPersonSearch = () => {
  clearTimeout(personSearchTimer)
  if (personQuery.value.trim().length < 2) {
    personResults.value = []
    return
  }
  personSearchTimer = setTimeout(async () => {
    try {
      const res = await api.helloasso.search_attendees(eventId, personQuery.value)
      personResults.value = res
    } catch (err) {
      console.error('Person search failed:', err)
    }
  }, 250)
}

const selectPerson = (person: AttendeeSearchResult) => {
  selectedPerson.value = person
  personQuery.value = ''
  personResults.value = []
}

const clearPerson = () => {
  selectedPerson.value = null
  personQuery.value = ''
  personResults.value = []
}

const useCustomName = () => {
  selectedPerson.value = { id: null, full_name: personQuery.value.trim(), email: null, uid: null, source: 'custom' }
  personResults.value = []
}

const toggleOption = (opt: PaymentFormOption) => {
  if (!opt?.id) return
  const optId = String(opt.id)
  const i = selectedOptionIds.value.indexOf(optId)
  if (i >= 0) selectedOptionIds.value.splice(i, 1)
  else selectedOptionIds.value.push(optId)
}

const PAYMENT_TYPE_COLOR_MAP: Record<string, string> = {
  helloasso: 'bg-blue-50 text-blue-600',
  helloasso_import: 'bg-indigo-50 text-indigo-600',
  credit_card: 'bg-purple-50 text-purple-600',
  cash: 'bg-emerald-50 text-emerald-600',
  cheque: 'bg-orange-50 text-orange-600',
  exchange: 'bg-pink-50 text-pink-600',
  none: 'bg-gray-50 text-gray-400',
  other: 'bg-gray-50 text-gray-500',
}

const PaymentTypeBadge = defineComponent({
  props: { type: String },
  setup(props) {
    return () => {
      const t = props.type ?? ''
      const label = PAYMENT_TYPE_LABELS[t] ?? t
      return h('span', {
        class: `inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium ${PAYMENT_TYPE_COLOR_MAP[t] ?? 'bg-gray-50 text-gray-500'}`,
      }, label)
    }
  },
})

const validated = computed(() => entries.value.filter(e => e.validated).length)
const completed = computed(() => entries.value.filter(e => e.completed).length)
const total = computed(() => entries.value.length)

const filtered = computed(() => {
  if (!search.value.trim()) return entries.value
  const q = search.value.trim().toLowerCase()
  return entries.value.filter(e =>
    e.display_name?.toLowerCase().includes(q) ||
    e.user_email?.toLowerCase().includes(q) ||
    e.attendee_name?.toLowerCase().includes(q)
  )
})

const displayedEntries = computed(() =>
  search.value.trim() ? filtered.value : entries.value.slice(0, 50)
)

const showToast = (msg: string) => {
  toast.value = msg
  setTimeout(() => { toast.value = '' }, 2500)
}

const handleEnter = async () => {
  if (filtered.value.length === 1) {
    const entry = filtered.value[0]
    if (!entry.completed && entry.payment_type === 'helloasso') return
    if (entry.validated) return
    await toggleValidate(entry)
    search.value = ''
    searchRef.value?.focus()
  } else if (filtered.value.length === 0 && search.value.trim()) {
    // No ticket match → open manual form with search text prefilled
    openManualForm(search.value.trim())
    search.value = ''
  }
}

const toggleValidate = async (entry: ValidationEntryRead) => {
  try {
    const updated = await api.helloasso.validate_entry(entry.id)
    const idx = entries.value.findIndex(e => e.id === entry.id)
    if (idx !== -1) entries.value[idx] = updated
    if (updated.validated) {
      showToast(`${updated.display_name} — validé ✓`)
    }
  } catch (err) {
    console.error('Validation failed:', err)
  }
}

const cancelEntry = async (entry: ValidationEntryRead) => {
  if (!confirm(`Annuler l'entrée de ${entry.display_name} ?`)) return
  try {
    await api.helloasso.cancel_entry(entry.id)
    entries.value = entries.value.filter(e => e.id !== entry.id)
    showToast(`${entry.display_name} — entrée annulée`)
  } catch (err) {
    console.error('Cancel failed:', err)
  }
}

const submitManualEntry = async () => {
  const name = attendeeName.value
  if (!name.trim()) return
  submittingManual.value = true
  try {
    const payload: ManualEntryCreate = {
      attendee_name: name.trim(),
      payment_type: manualPaymentType.value as PaymentType,
      selected_option_ids: selectedOptionIds.value,
      amount_cents: computedTotal.value,
    }
    const created = await api.helloasso.create_manual_entry(String(eventId), payload)
    entries.value.unshift(created)
    showManualForm.value = false
    showToast(`${created.display_name} — entrée ajoutée`)
  } catch (err) {
    console.error('Manual entry failed:', err)
  } finally {
    submittingManual.value = false
  }
}

onMounted(async () => {
  try {
    const [event, validationEntries] = await Promise.all([
      api.events.get_event(String(eventId)) as Promise<EventRead>,
      api.helloasso.get_validation_entries(String(eventId)),
    ])
    eventTitle.value = event.title
    entries.value = validationEntries

    try {
      const form: PaymentFormRead = await api.helloasso.get_payment_form(String(eventId))
      formBaseCents.value = form.total_amount_cents || 0
      formOptions.value = form.options || []
    } catch { /* no form */ }
  } catch (err) {
    console.error('Failed to load validation data:', err)
  } finally {
    loading.value = false
  }
  searchRef.value?.focus()
})
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 1rem); }

.list-move, .list-enter-active, .list-leave-active { transition: all 0.2s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateX(-8px); }
</style>
