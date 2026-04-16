<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <TicketIcon class="h-6 w-6 text-green-600" />
        Mes paiements
      </h1>
      <button
        v-if="hasPending"
        @click="refresh"
        :disabled="loading"
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 transition-colors disabled:opacity-50"
        title="Rafraîchir les paiements en attente"
      >
        <ArrowPathIcon class="h-4 w-4" :class="{ 'animate-spin': loading }" />
        Actualiser
      </button>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-12">Chargement…</div>

    <div v-else-if="!entries.length" class="text-center text-gray-400 py-12">
      Aucun paiement pour l'instant.
    </div>

    <template v-else>
      <!-- Upcoming / current -->
      <section v-if="upcoming.length">
        <h2 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">À venir</h2>
        <div class="space-y-3 mb-8">
          <TicketCard v-for="entry in upcoming" :key="entry.id" :entry="entry" />
        </div>
      </section>

      <!-- Past (collapsible) -->
      <section v-if="past.length">
        <button
          @click="pastOpen = !pastOpen"
          class="flex items-center gap-2 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 hover:text-gray-600 transition-colors"
        >
          <ChevronRightIcon class="h-3 w-3 transition-transform" :class="{ 'rotate-90': pastOpen }" />
          Passés ({{ past.length }})
        </button>
        <div v-if="pastOpen" class="space-y-3">
          <TicketCard v-for="entry in past" :key="entry.id" :entry="entry" :dim="true" />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineComponent, h, type PropType } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api'
import type { MyPaymentEntryRead } from '@/api/types'
import { TicketIcon, ChevronRightIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import { formatLocalDate } from '../utils/dateUtils'

const loading = ref(false)
const entries = ref<MyPaymentEntryRead[]>([])
const pastOpen = ref(false)

const hasPending = computed(() => entries.value.some(e => !e.completed))

const now = new Date()

const upcoming = computed(() =>
  entries.value.filter(e => new Date(e.event_start_time) >= now)
)

const past = computed(() =>
  entries.value.filter(e => new Date(e.event_start_time) < now)
)

// Inline ticket card component
const TicketCard = defineComponent({
  props: { entry: { type: Object as PropType<MyPaymentEntryRead>, required: true }, dim: Boolean },
  setup(props) {
    return () => h(RouterLink, {
      to: `/events/${props.entry.event_id}`,
      class: [
        'block rounded-xl border p-4 transition-colors hover:bg-gray-50',
        props.dim ? 'border-gray-100 bg-gray-50 opacity-60' : 'border-green-100 bg-white shadow-sm',
      ].join(' '),
    }, () => [
      h('div', { class: 'flex items-start justify-between gap-3' }, [
        h('div', { class: 'flex-1 min-w-0' }, [
          h('p', { class: 'text-sm font-semibold text-gray-900 truncate' }, props.entry.event_title),
          h('p', { class: 'text-xs text-gray-500 mt-0.5' }, formatLocalDate(props.entry.event_start_time)),
          h('p', { class: 'text-xs text-gray-400' }, props.entry.org_name),
        ]),
        h('div', { class: 'flex-shrink-0 text-right' }, [
          h('p', { class: 'text-sm font-bold ' + (props.entry.completed ? 'text-green-700' : 'text-amber-600') },
            (props.entry.amount_cents / 100).toFixed(2) + ' €'),
          h('p', { class: 'text-xs mt-0.5 ' + (props.entry.completed ? 'text-green-600' : 'text-amber-500') },
            props.entry.completed ? 'Payé ✓' : 'En attente'),
        ]),
      ]),
      h('div', { class: 'mt-2 border-t border-dashed border-gray-200 pt-2' }, [
        h('p', { class: 'text-xs text-gray-700' }, props.entry.item_name),
        ...(props.entry.selected_options || []).map((opt: { name: string; price_cents: number }) =>
          h('p', { class: 'text-xs text-gray-500' }, `+ ${opt.name} (+${(opt.price_cents / 100).toFixed(2)} €)`)
        ),
      ]),
    ])
  },
})

const refresh = async () => {
  loading.value = true
  try {
    entries.value = await api.helloasso.get_my_entries()
  } catch (err) {
    console.error('Failed to load payment entries:', err)
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>
