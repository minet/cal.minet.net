<template>
  <div class="max-w-5xl mx-auto">
    <header class="bg-white shadow-sm rounded-lg mb-6">
      <div class="px-4 py-6 sm:px-6 lg:px-8 flex items-center justify-between gap-4 flex-wrap">
        <div class="flex items-center gap-3">
          <CreditCardIcon class="h-7 w-7 text-green-600" />
          <div>
            <DocsHint path="/tableau-de-bord-tresorerie" search="tableau de bord trésorerie">
              <h1 class="text-2xl font-bold tracking-tight text-gray-900">Paiements HelloAsso</h1>
            </DocsHint>
            <p class="text-sm text-gray-500 mt-0.5">Formulaires de paiement de vos organisations</p>
          </div>
        </div>

        <!-- Time filter dropdown -->
        <select
          v-model="timeFilter"
          class="rounded-md border-0 py-1.5 pl-3 pr-8 text-sm text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
        >
          <option value="upcoming">À venir</option>
          <option value="all">Tous</option>
          <option value="past">Passés</option>
        </select>
      </div>
    </header>

    <!-- Cancellation notice -->
    <div class="mb-4 flex items-start gap-3 rounded-lg bg-amber-50 border border-amber-200 px-4 py-3 text-sm text-amber-800">
      <InformationCircleIcon class="h-5 w-5 shrink-0 mt-0.5 text-amber-500" />
      <span>
        <strong>Paiement annulé ≠ remboursé.</strong>
        Un paiement HelloAsso annulé signifie simplement qu'il a été supprimé depuis la page de validation de l'événement.
        Les paiements annulés restent affichés pour des raisons de traçabilité.
      </span>
    </div>

    <div v-if="loading" class="bg-white shadow-sm rounded-lg p-8 text-center text-sm text-gray-500">
      Chargement…
    </div>

    <div v-else-if="items.length === 0" class="bg-white shadow-sm rounded-lg p-8 text-center text-sm text-gray-500">
      Aucun formulaire de paiement pour la période sélectionnée.
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
            <div class="flex items-center gap-2 flex-wrap mt-0.5">
              <span class="text-sm text-gray-700">
                {{ item.item_name }}
                <span class="font-semibold">{{ (item.total_amount_cents / 100).toFixed(2) }}&nbsp;€</span>
              </span>
              <span
                v-for="opt in item.options"
                :key="opt.id || opt.name"
                class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700 ring-1 ring-inset ring-indigo-200"
              >
                {{ opt.name }}{{ opt.price_cents !== 0 ? ' · ' + (opt.price_cents / 100).toFixed(2) + ' €' : '' }}
              </span>
            </div>
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
        <div class="px-5 py-3 space-y-2">
          <!-- Entry stats -->
          <div v-if="item.status === 'approved'" class="flex items-center gap-3 text-sm text-gray-600">
            <span>
              <span class="font-semibold text-gray-900">{{ item.completed_count }}</span>
              payé(s)
            </span>
            <span class="text-gray-300">·</span>
            <span>
              <span class="font-semibold text-gray-900">{{ item.entry_count }}</span>
              initié(s)
            </span>
          </div>

          <!-- Actions row -->
          <div class="flex flex-wrap gap-2">

            <!-- ── Pending: approve / reject ── -->
            <template v-if="item.status === 'pending'">
              <button
                @click="approveForm(item)"
                :disabled="processingId === item.id"
                class="flex items-center gap-1.5 rounded-md bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-500 disabled:opacity-50 transition-colors"
              >
                <CheckCircleIcon class="h-3.5 w-3.5" />
                Approuver
              </button>
              <button
                @click="openRejectModal(item)"
                :disabled="processingId === item.id"
                class="flex items-center gap-1.5 rounded-md bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-500 disabled:opacity-50 transition-colors"
              >
                <XMarkIcon class="h-3.5 w-3.5" />
                Refuser
              </button>
            </template>

            <!-- ── Approved: primary actions ── -->
            <template v-if="item.status === 'approved'">
              <!-- Validation view -->
              <router-link
                :to="`/events/${item.event_id}/validation`"
                class="flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 transition-colors"
              >
                <ClipboardDocumentCheckIcon class="h-3.5 w-3.5" />
                Validation
              </router-link>

              <!-- View entries -->
              <button
                v-if="item.entry_count > 0"
                @click="toggleEntries(item.id)"
                class="flex items-center gap-1.5 rounded-md bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700 ring-1 ring-inset ring-blue-200 hover:bg-blue-100 transition-colors"
              >
                <UsersIcon class="h-3.5 w-3.5" />
                Inscrits
              </button>

              <!-- Export ODS -->
              <button
                v-if="item.entry_count > 0"
                @click="downloadEntriesOds(item)"
                class="flex items-center gap-1.5 rounded-md bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-200 hover:bg-indigo-100 transition-colors"
              >
                <ArrowDownTrayIcon class="h-3.5 w-3.5" />
                Export ODS
              </button>

              <!-- Check HelloAsso payment status -->
              <button
                v-if="item.completed_count < item.entry_count"
                @click="checkPayments(item)"
                :disabled="checkingPaymentId === item.id"
                class="flex items-center gap-1.5 rounded-md bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-200 hover:bg-amber-100 disabled:opacity-50 transition-colors"
              >
                <CreditCardIcon class="h-3.5 w-3.5" />
                {{ checkingPaymentId === item.id ? 'Vérification…' : 'Vérifier paiements HA' }}
              </button>

              <!-- Billeterie -->
              <button
                v-if="item.approving_org_id"
                @click="openBilleterieModal(item)"
                class="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
                :class="item.billeterie
                  ? 'bg-purple-600 text-white hover:bg-purple-500'
                  : 'bg-purple-50 text-purple-700 ring-1 ring-inset ring-purple-200 hover:bg-purple-100'"
              >
                <TicketIcon class="h-3.5 w-3.5" />
                {{ item.billeterie ? 'Billeterie liée' : 'Billeterie Exté' }}
              </button>

              <!-- Open/close toggle -->
              <button
                @click="toggleOpen(item)"
                class="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
                :class="item.is_open
                  ? 'bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-200 hover:bg-amber-100'
                  : 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-200 hover:bg-green-100'"
              >
                <LockClosedIcon v-if="item.is_open" class="h-3.5 w-3.5" />
                <LockOpenIcon v-else class="h-3.5 w-3.5" />
                {{ item.is_open ? 'Fermer' : 'Rouvrir' }}
              </button>
            </template>

            <!-- ── Edit options (all non-rejected) ── -->
            <button
              v-if="item.status !== 'rejected'"
              @click="openEditModal(item)"
              class="flex items-center gap-1.5 rounded-md bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-200 transition-colors"
            >
              <PencilIcon class="h-3.5 w-3.5" />
              Options
            </button>

          </div>
        </div>

        <!-- Billeterie status strip -->
        <div v-if="item.billeterie" class="px-5 py-2 bg-purple-50 border-t border-purple-100 flex items-center justify-between gap-4 flex-wrap">
          <div class="flex items-center gap-2 text-xs text-purple-700">
            <TicketIcon class="h-3.5 w-3.5 shrink-0" />
            <span class="font-medium">{{ item.billeterie.helloasso_form_title }}</span>
            <span class="text-purple-400">·</span>
            <span v-if="item.billeterie.last_imported_at" class="text-purple-500">
              Dernier import : {{ formatDate(item.billeterie.last_imported_at) }}
            </span>
            <span v-else class="text-purple-400 italic">Aucun import effectué</span>
          </div>
          <button
            @click="importBilleterie(item)"
            :disabled="importingId === item.id"
            class="flex items-center gap-1 rounded-md bg-purple-600 px-3 py-1 text-xs font-semibold text-white hover:bg-purple-500 disabled:opacity-50 transition-colors"
          >
            <ArrowDownTrayIcon class="h-3.5 w-3.5" />
            {{ importingId === item.id ? 'Import…' : 'Importer les participants' }}
          </button>
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
                <th class="pb-1.5 font-medium">Payment ID</th>
                <th class="pb-1.5 font-medium">Order ID</th>
                <th class="pb-1.5 font-medium">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="entry in entries[item.id]" :key="entry.id" class="py-1">
                <td class="py-1.5 pr-4">{{ entry.user_name || entry.attendee_name || entry.user_id }}</td>
                <td class="py-1.5 pr-4">{{ (entry.amount_cents / 100).toFixed(2) }}&nbsp;€</td>
                <td class="py-1.5 pr-4">
                  <template v-if="entry.imported_options?.length">
                    {{ entry.imported_options.map(o => o.amount_cents > 0 ? `${o.name} (+${(o.amount_cents / 100).toFixed(2)} €)` : o.name).join(', ') }}
                  </template>
                  <template v-else-if="entry.selected_option_ids?.length">
                    {{ entry.selected_option_ids.map(id => item.options.find(o => String(o.id) === String(id))?.name).filter(Boolean).join(', ') }}
                  </template>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <td class="py-1.5 pr-4">
                  <span v-if="entry.cancelled" class="inline-flex items-center gap-1 text-red-500 font-medium">
                    Annulé
                  </span>
                  <template v-else>
                    <span :class="entry.completed ? 'text-green-600 font-medium' : 'text-amber-600'">
                      {{ entry.completed ? 'Payé' : 'En attente' }}
                    </span>
                  </template>
                  <span v-if="entry.payment_type === 'helloasso_import'" class="ml-1 text-purple-500 text-xs">(billeterie)</span>
                  <span v-if="entry.cancelled && entry.completed" class="ml-1 text-gray-400 text-xs">(était : payé)</span>
                </td>
                <td class="py-1.5 pr-4 font-mono text-[11px] text-gray-500">{{ entry.helloasso_payment_id || '—' }}</td>
                <td class="py-1.5 pr-4 font-mono text-[11px] text-gray-500">{{ entry.helloasso_order_id || '—' }}</td>
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
      <div class="bg-white rounded-xl shadow-xl w-full max-w-4xl p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Modifier les options</h3>
        <p class="text-sm text-gray-500 mb-1">{{ editModal.item?.item_name }} — {{ ((editModal.item?.total_amount_cents ?? 0) / 100).toFixed(2) }}&nbsp;€</p>

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

            <div v-if="opt.is_private" class="space-y-2">
              <details class="rounded-md border border-indigo-100 bg-indigo-50/40" @toggle="onToggleAllowedUsers(idx, $event)">
                <summary class="cursor-pointer select-none px-3 py-2 text-xs font-medium text-indigo-700">
                  Personnes autorisées ({{ opt.allowed_user_ids.length }})
                </summary>
                <div class="px-3 pb-3">
                  <div v-if="opt.allowed_user_ids.length" class="mb-2">
                    <input
                      v-model="opt.allowed_user_search"
                      type="text"
                      placeholder="Rechercher dans la liste…"
                      class="block w-full rounded-md border-0 px-3 py-1.5 text-xs text-gray-900 shadow-sm ring-1 ring-inset ring-indigo-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                    />
                  </div>

                  <p v-if="opt.allowed_users_loading" class="text-xs text-gray-500 italic">Chargement des noms…</p>
                  <ul v-else-if="filteredAllowedUsers(opt).length" class="space-y-1 max-h-40 overflow-y-auto text-xs text-indigo-900">
                    <li v-for="person in filteredAllowedUsers(opt)" :key="person.id" class="flex items-center justify-between gap-2 rounded bg-white px-2 py-1 ring-1 ring-inset ring-indigo-100">
                      <span class="truncate">{{ person.full_name || person.email || person.id }}</span>
                      <button type="button" @click="removeAllowedUser(idx, person.id)" class="rounded p-0.5 hover:bg-indigo-100 transition-colors">
                        <XMarkIcon class="h-3 w-3" />
                      </button>
                    </li>
                  </ul>
                  <p v-else-if="opt.allowed_user_ids.length" class="text-xs text-gray-500 italic">Aucun résultat.</p>
                  <p v-else class="text-xs text-gray-500 italic">Aucune personne autorisée.</p>
                </div>
              </details>

              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Ajouter des personnes (une ligne par nom/email/uid)</label>
                <textarea
                  v-model="opt.allowed_user_input"
                  rows="4"
                  placeholder="Jean Dupont&#10;jean.dupont@telecom-sudparis.eu"
                  class="block w-full rounded-md border-0 px-3 py-2 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                />
                <div class="mt-2 flex items-center gap-2">
                  <button
                    type="button"
                    @click="resolveAllowedUsersForOption(idx)"
                    :disabled="resolveModal.resolving"
                    class="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
                  >
                    Valider la liste
                  </button>
                  <span class="text-xs text-gray-500">Les lignes non trouvées seront reproposées pour correction.</span>
                </div>
              </div>
            </div>
          </div>
          <button type="button" @click="editModal.options.push({ id: null, name: '', amount_euros: '', is_private: false, allowed_user_ids: [], allowed_users: [], allowed_users_loaded: false, allowed_users_loading: false, allowed_user_search: '', allowed_user_input: '' })"
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

    <!-- Resolve failed lines modal -->
    <div v-if="resolveModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-2xl p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">Corriger les lignes non résolues</h3>
        <p class="text-sm text-gray-500 mb-3">Certaines lignes n'ont pas pu être associées à un compte. Corrigez-les puis validez à nouveau.</p>
        <textarea
          v-model="resolveModal.failedText"
          rows="8"
          class="block w-full rounded-md border-0 px-3 py-2 text-sm text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600"
        />
        <div class="mt-4 flex justify-end gap-3">
          <button @click="resolveModal.open = false"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            Fermer
          </button>
          <button @click="submitResolveCorrections" :disabled="resolveModal.resolving"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50">
            {{ resolveModal.resolving ? 'Validation…' : 'Valider de nouveau' }}
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
          <button @click="confirmReject" :disabled="!rejectModal.message || !!processingId"
            class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:opacity-50">
            Refuser
          </button>
        </div>
      </div>
    </div>

    <!-- Billeterie modal -->
    <div v-if="billeterieModal.open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-1">Lier une billeterie HelloAsso</h3>
        <p class="text-sm text-gray-500 mb-4">
          Sélectionnez un formulaire de billeterie HelloAsso pour importer automatiquement ses participants dans la liste des inscrits.
        </p>

        <!-- Currently linked billeterie -->
        <div v-if="billeterieModal.item?.billeterie" class="mb-4 p-3 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-between gap-3">
          <div class="text-sm text-purple-800">
            <span class="font-medium">Liée&nbsp;: </span>{{ billeterieModal.item.billeterie.helloasso_form_title }}
          </div>
          <button
            @click="unlinkBilleterie(billeterieModal.item)"
            :disabled="billeterieModal.saving"
            class="text-xs text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
          >
            Délier
          </button>
        </div>

        <!-- Billeterie list -->
        <div v-if="billeterieModal.loading" class="text-sm text-gray-400 py-4 text-center">Chargement des billeteries…</div>
        <div v-else-if="billeterieModal.error" class="text-sm text-red-600 py-2">{{ billeterieModal.error }}</div>
        <div v-else-if="billeterieModal.forms.length === 0" class="text-sm text-gray-400 py-4 text-center">
          Aucun formulaire de billeterie trouvé sur HelloAsso.
        </div>
        <div v-else class="space-y-2 max-h-64 overflow-y-auto mb-4">
          <label
            v-for="form in billeterieModal.forms"
            :key="form.form_slug"
            class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors"
            :class="billeterieModal.selected === form.form_slug
              ? 'border-purple-400 bg-purple-50'
              : 'border-gray-200 hover:bg-gray-50'"
          >
            <input
              type="radio"
              :value="form.form_slug"
              v-model="billeterieModal.selected"
              class="text-purple-600 focus:ring-purple-500"
            />
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ form.title }}</p>
              <p class="text-xs text-gray-400">
                {{ form.state }}
                <template v-if="form.start_date"> · {{ formatDate(form.start_date) }}</template>
              </p>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-3">
          <button @click="billeterieModal.open = false"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            Fermer
          </button>
          <button
            @click="saveBilleterieLink"
            :disabled="!billeterieModal.selected || billeterieModal.saving"
            class="rounded-md bg-purple-600 px-3 py-2 text-sm font-semibold text-white hover:bg-purple-500 disabled:opacity-50"
          >
            {{ billeterieModal.saving ? 'Enregistrement…' : 'Lier la billeterie' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Import result toast -->
    <div v-if="importToast" class="fixed bottom-4 right-4 z-50 bg-white shadow-lg rounded-lg px-4 py-3 flex items-center gap-3 ring-1 ring-gray-200">
      <CheckCircleIcon class="h-5 w-5 text-green-500 shrink-0" />
      <p class="text-sm text-gray-800">{{ importToast }}</p>
    </div>

    <!-- Check payment result toast -->
    <div v-if="checkPaymentToast" class="fixed bottom-16 right-4 z-50 bg-white shadow-lg rounded-lg px-4 py-3 flex items-center gap-3 ring-1 ring-gray-200">
      <CheckCircleIcon v-if="!checkPaymentToast.error" class="h-5 w-5 text-amber-500 shrink-0" />
      <XMarkIcon v-else class="h-5 w-5 text-red-500 shrink-0" />
      <p class="text-sm text-gray-800">{{ checkPaymentToast.message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, reactive } from 'vue'
import {
  CreditCardIcon,
  LockClosedIcon,
  LockOpenIcon,
  PencilIcon,
  UsersIcon,
  XMarkIcon,
  PlusIcon,
  TicketIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ClipboardDocumentCheckIcon,
} from '@heroicons/vue/24/outline'
import { api } from '@/api'
import type {
  PaymentDashboardItem,
  PaymentEntryRead,
  HelloAssoFormSummary,
  PaymentCheckResult,
} from '@/api/types'

// Local type for options displayed in the edit modal — extends PaymentFormOption
// with UI-only fields (amount_euros for display, allowed_users cache, etc.)
interface EditableOption {
  id: string | null | undefined
  name: string
  amount_euros: number | string
  is_private: boolean
  allowed_user_ids: string[]
  allowed_users: Array<{ id: string; full_name: string | null; email: string | null }>
  allowed_users_loaded: boolean
  allowed_users_loading: boolean
  allowed_user_search: string
  allowed_user_input: string
}

const items = ref<PaymentDashboardItem[]>([])
const loading = ref(true)
const processingId = ref<string | null>(null)
const importingId = ref<string | null>(null)
const importToast = ref<string | null>(null)
const checkingPaymentId = ref<string | null>(null)
const checkPaymentToast = ref<{ message: string; error: boolean } | null>(null)
const expandedEntries = reactive<Record<string, boolean>>({})
const loadingEntries = reactive<Record<string, boolean>>({})
const entries = reactive<Record<string, PaymentEntryRead[]>>({})

// Time filter: 'upcoming' | 'all' | 'past'
const timeFilter = ref('upcoming')

const editModal = ref<{
  open: boolean
  item: PaymentDashboardItem | null
  options: EditableOption[]
  is_open: boolean
}>({ open: false, item: null, options: [], is_open: true })
const savingEdit = ref(false)
const rejectModal = ref<{ open: boolean; item: PaymentDashboardItem | null; message: string }>({ open: false, item: null, message: '' })
const resolveModal = ref<{ open: boolean; resolving: boolean; optionIdx: number | null; failedText: string }>({ open: false, resolving: false, optionIdx: null, failedText: '' })


const billeterieModal = ref<{
  open: boolean
  item: PaymentDashboardItem | null
  forms: HelloAssoFormSummary[]
  selected: string | null
  loading: boolean
  saving: boolean
  error: string | null
}>({
  open: false,
  item: null,
  forms: [],
  selected: null,
  loading: false,
  saving: false,
  error: null,
})

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })

const statusLabel = (status: string): string => ({
  pending: 'En attente',
  approved: 'Approuvé',
  rejected: 'Refusé',
} as Record<string, string>)[status] ?? status

const loadItems = async () => {
  loading.value = true
  try {
    items.value = await api.helloasso.get_my_payment_forms({ time_filter: timeFilter.value })
  } catch (err) {
    console.error('Failed to load payment forms:', err)
  } finally {
    loading.value = false
  }
}

watch(timeFilter, loadItems)

const toggleOpen = async (item: PaymentDashboardItem) => {
  processingId.value = item.id
  try {
    const updated = await api.helloasso.update_payment_form(item.event_id, {
      is_open: !item.is_open,
    })
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx].is_open = updated.is_open
  } catch (err: unknown) {
    console.error('Toggle open failed:', err)
  } finally {
    processingId.value = null
  }
}

const openEditModal = async (item: PaymentDashboardItem) => {
  editModal.value = {
    open: true,
    item,
    is_open: item.is_open,
    options: (item.options || []).map((o): EditableOption => ({
      id: o.id || null,
      name: o.name,
      amount_euros: o.price_cents / 100,
      is_private: o.is_private || false,
      allowed_user_ids: [...(o.allowed_user_ids || [])],
      allowed_users: [],
      allowed_users_loaded: false,
      allowed_users_loading: false,
      allowed_user_search: '',
      allowed_user_input: '',
    })),
  }
}

const loadAllowedUsersForOption = async (optIdx: number) => {
  const opt = editModal.value.options[optIdx]
  if (!opt || opt.allowed_users_loading || opt.allowed_users_loaded) return
  if (!opt.allowed_user_ids.length) {
    opt.allowed_users = []
    opt.allowed_users_loaded = true
    return
  }

  opt.allowed_users_loading = true
  try {
    const res = await api.helloasso.batch_lookup_users({ ids: opt.allowed_user_ids })
    const map = Object.fromEntries((res || []).map(u => [String(u.id), u]))
    opt.allowed_users = opt.allowed_user_ids.map((id) => {
      const found = map[String(id)]
      return found
        ? { id: String(found.id), full_name: found.full_name, email: found.email }
        : { id: String(id), full_name: null, email: null }
    })
    opt.allowed_users_loaded = true
  } catch (err) {
    console.error('Failed to load allowed users:', err)
  } finally {
    opt.allowed_users_loading = false
  }
}

const onToggleAllowedUsers = (optIdx: number, evt: Event) => {
  const isOpen = !!(evt?.target as HTMLDetailsElement)?.open
  if (isOpen) loadAllowedUsersForOption(optIdx)
}

const filteredAllowedUsers = (opt: EditableOption) => {
  const q = (opt.allowed_user_search || '').trim().toLowerCase()
  if (!q) return opt.allowed_users || []
  return (opt.allowed_users || []).filter((u) => (
    (u.full_name || '').toLowerCase().includes(q)
    || (u.email || '').toLowerCase().includes(q)
    || String(u.id || '').toLowerCase().includes(q)
  ))
}

const _splitLines = (raw: string) => {
  const seen = new Set()
  return (raw || '')
    .split('\n')
    .map((s: string) => s.trim())
    .filter(Boolean)
    .filter((s: string) => {
      const key = s.toLowerCase()
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
}

const _resolveLinesToUserIds = async (eventId: string, lines: string[]) => {
  if (!lines.length) return { resolvedIds: [], failedLines: [] }
  const res = await api.helloasso.bulk_resolve_attendees(eventId, { queries: lines })
  const resolvedIds = []
  const failedLines = []
  for (const row of res || []) {
    if (row.user_id) resolvedIds.push(String(row.user_id))
    else if (row.query) failedLines.push(String(row.query))
  }
  return { resolvedIds, failedLines }
}

const _appendAllowedIds = (optIdx: number, ids: string[]) => {
  const opt = editModal.value.options[optIdx]
  if (!opt) return
  const existing = new Set(opt.allowed_user_ids.map(String))
  for (const id of ids) {
    const sid = String(id)
    if (!existing.has(sid)) {
      opt.allowed_user_ids.push(sid)
      existing.add(sid)
    }
  }
  opt.allowed_users_loaded = false
}

const resolveAllowedUsersForOption = async (optIdx: number) => {
  const opt = editModal.value.options[optIdx]
  if (!opt) return
  const lines = _splitLines(opt.allowed_user_input)
  if (!lines.length) return

  resolveModal.value.resolving = true
  try {
    const { resolvedIds, failedLines } = await _resolveLinesToUserIds(editModal.value.item!.event_id, lines)
    _appendAllowedIds(optIdx, resolvedIds)
    opt.allowed_user_input = ''

    if (failedLines.length) {
      resolveModal.value.open = true
      resolveModal.value.optionIdx = optIdx
      resolveModal.value.failedText = failedLines.join('\n')
    }
  } catch (err) {
    console.error('Bulk resolve failed:', err)
  } finally {
    resolveModal.value.resolving = false
  }
}

const submitResolveCorrections = async () => {
  const optIdx = resolveModal.value.optionIdx
  if (optIdx === null || optIdx === undefined) return
  const lines = _splitLines(resolveModal.value.failedText)
  if (!lines.length) {
    resolveModal.value.open = false
    return
  }

  resolveModal.value.resolving = true
  try {
    const { resolvedIds, failedLines } = await _resolveLinesToUserIds(editModal.value.item!.event_id, lines)
    _appendAllowedIds(optIdx, resolvedIds)
    if (failedLines.length) {
      resolveModal.value.failedText = failedLines.join('\n')
    } else {
      resolveModal.value.open = false
      resolveModal.value.failedText = ''
      resolveModal.value.optionIdx = null
    }
  } catch (err) {
    console.error('Correction resolve failed:', err)
  } finally {
    resolveModal.value.resolving = false
  }
}

const removeAllowedUser = (optIdx: number, userId: string) => {
  const opt = editModal.value.options[optIdx]
  const id = String(userId)
  opt.allowed_user_ids = opt.allowed_user_ids.filter(x => String(x) !== id)
  opt.allowed_users = (opt.allowed_users || []).filter(u => String(u.id) !== id)
}

const saveEditModal = async () => {
  savingEdit.value = true
  try {
    const optionsToSave = editModal.value.options
      .filter(o => o.name && o.amount_euros !== '' && o.amount_euros !== null)
      .map(o => ({
        id: o.id || undefined,
        name: o.name,
        price_cents: Math.round(Number(o.amount_euros) * 100),
        is_private: o.is_private || false,
        allowed_user_ids: o.allowed_user_ids,
      }))
    const res = await api.helloasso.update_payment_form(editModal.value.item!.event_id, {
      options: optionsToSave,
      is_open: editModal.value.is_open,
    })
    const idx = items.value.findIndex(i => i.id === editModal.value.item!.id)
    if (idx !== -1) {
      items.value[idx].options = res.options
      items.value[idx].is_open = res.is_open
    }
    editModal.value.open = false
  } catch (err) {
    console.error('Save options failed:', err)
  } finally {
    savingEdit.value = false
  }
}

const approveForm = async (item: PaymentDashboardItem) => {
  processingId.value = item.id
  try {
    await api.helloasso.approve_payment_form(item.event_id)
    await loadItems()
  } catch (err) {
    console.error('Approve failed:', err)
  } finally {
    processingId.value = null
  }
}

const openRejectModal = (item: PaymentDashboardItem) => {
  rejectModal.value = { open: true, item, message: '' }
}

const confirmReject = async () => {
  if (!rejectModal.value.message) return
  processingId.value = rejectModal.value.item!.id
  try {
    await api.helloasso.reject_payment_form(rejectModal.value.item!.event_id, {
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

const toggleEntries = async (formId: string) => {
  if (expandedEntries[formId]) {
    expandedEntries[formId] = false
    return
  }
  expandedEntries[formId] = true
  if (entries[formId]) return

  loadingEntries[formId] = true
  try {
    const item = items.value.find(i => i.id === formId)
    entries[formId] = await api.helloasso.get_payment_entries(item!.event_id)
  } catch (err) {
    console.error('Failed to load entries:', err)
    entries[formId] = []
  } finally {
    loadingEntries[formId] = false
  }
}

const downloadEntriesOds = async (item: PaymentDashboardItem) => {
  try {
    const blob = await api.helloasso.export_payment_entries(item.event_id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `participants_${item.event_id}.ods`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('ODS export failed:', err)
  }
}

// ---------------------------------------------------------------------------
// On-demand payment status check
// ---------------------------------------------------------------------------

const checkPayments = async (item: PaymentDashboardItem) => {
  checkingPaymentId.value = item.id
  checkPaymentToast.value = null
  try {
    const result: PaymentCheckResult = await api.helloasso.check_payment_status(item.event_id)
    const parts: string[] = []
    if (result.completed > 0) parts.push(`${result.completed} confirmé(s)`)
    if (result.backfilled > 0) parts.push(`${result.backfilled} référence(s) complétée(s)`)
    checkPaymentToast.value = {
      message: parts.length > 0
        ? `${parts.join(', ')} sur ${result.checked} vérifié(s).`
        : `${result.checked} paiement(s) vérifié(s) — aucun nouveau.`,
      error: false,
    }
    // Refresh entries if expanded
    if (expandedEntries[item.id]) {
      delete entries[item.id]
      await toggleEntries(item.id)
    }
    // Refresh item counts
    await loadItems()
  } catch (err) {
    console.error('check-payment-status failed:', err)
    checkPaymentToast.value = { message: 'Erreur lors de la vérification.', error: true }
  } finally {
    checkingPaymentId.value = null
    setTimeout(() => { checkPaymentToast.value = null }, 5000)
  }
}

// ---------------------------------------------------------------------------
// Billeterie
// ---------------------------------------------------------------------------

const openBilleterieModal = async (item: PaymentDashboardItem) => {
  billeterieModal.value = {
    open: true,
    item,
    forms: [],
    selected: item.billeterie?.helloasso_form_slug ?? null,
    loading: true,
    saving: false,
    error: null,
  }

  try {
    billeterieModal.value.forms = await api.helloasso.get_billeteries(item.approving_org_id!)
  } catch (err) {
    const e = err as { response?: { status?: number; data?: { detail?: string } } }
    if (e.response?.status === 403) {
      billeterieModal.value.error = 'Vous n\'avez pas les droits pour gérer les billeteries de cette organisation.'
    } else if (e.response?.status === 404) {
      billeterieModal.value.error = 'Aucune intégration HelloAsso configurée sur cette organisation.'
    } else {
      billeterieModal.value.error = e.response?.data?.detail || 'Erreur lors du chargement des billeteries.'
    }
  } finally {
    billeterieModal.value.loading = false
  }
}

const saveBilleterieLink = async () => {
  const { item, selected, forms } = billeterieModal.value
  if (!selected) return

  const form = forms.find(f => f.form_slug === selected)
  billeterieModal.value.saving = true
  try {
    const res = await api.helloasso.create_billeterie(item!.event_id, {
      org_id: item!.approving_org_id ?? '',
      form_slug: selected,
      form_type: form?.form_type ?? 'Event',
      form_title: form?.title ?? selected,
    })
    // Update local item
    const idx = items.value.findIndex(i => i.id === item!.id)
    if (idx !== -1) items.value[idx].billeterie = res
    billeterieModal.value.item = { ...item!, billeterie: res }
    billeterieModal.value.open = false
  } catch (err) {
    billeterieModal.value.error = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur lors de la liaison.'
  } finally {
    billeterieModal.value.saving = false
  }
}

const unlinkBilleterie = async (item: PaymentDashboardItem) => {
  billeterieModal.value.saving = true
  try {
    await api.helloasso.delete_billeterie(item.event_id)
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx !== -1) items.value[idx].billeterie = null
    billeterieModal.value.item = { ...item, billeterie: null }
    billeterieModal.value.open = false
  } catch (err) {
    billeterieModal.value.error = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur lors de la déliaison.'
  } finally {
    billeterieModal.value.saving = false
  }
}

const importBilleterie = async (item: PaymentDashboardItem) => {
  importingId.value = item.id
  try {
    const res = await api.helloasso.import_billeterie(item.event_id)
    const { imported, skipped } = res

    // Refresh the item's billeterie (to update last_imported_at) and entries
    await loadItems()
    // Reset cached entries so they reload on next expand
    delete entries[item.id]

    importToast.value = `${imported} participant(s) importé(s), ${skipped} ignoré(s).`
    setTimeout(() => { importToast.value = null }, 4000)
  } catch (err) {
    console.error('Import failed:', err)
    importToast.value = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur lors de l\'import.'
    setTimeout(() => { importToast.value = null }, 5000)
  } finally {
    importingId.value = null
  }
}

onMounted(loadItems)
</script>
