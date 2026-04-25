<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-sm text-gray-500">Chargement...</p>
  </div>

  <div v-else-if="event">
    <!-- Header -->
    <header 
      class="shadow-sm rounded-lg mb-6 transition-colors"
      :style="{ 
        background: getEventGradientLight(event.organization, event.guest_organizations),
        borderTop: `4px solid ${event.organization?.color_primary || '#4f46e5'}`
      }"
    >
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ event.title }}</h1>
            <ReactionList 
              v-if="event" 
              :event-id="event.id" 
              :reactions="event.reactions"
              :btn-add="canEdit"
              @update="loadEvent" 
              class="my-2"
            />
            <div class="mt-1 flex items-center text-xs text-gray-500 mb-2">
              <InformationCircleIcon class="h-3 w-3 mr-1" />
              Interagir ajoute l'événement à votre calendrier
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 sm:gap-3">
              <!-- Visibility Badge -->
              <span v-if="event.visibility === 'draft'" class="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-inset ring-yellow-600/20">
                <DocumentTextIcon class="mr-1.5 h-4 w-4" />
                Brouillon
              </span>
              <span v-else-if="event.visibility === 'private'" class="inline-flex items-center rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700 ring-1 ring-inset ring-purple-600/20">
                <LockClosedIcon class="mr-1.5 h-4 w-4" />
                Privé
              </span>
              <span v-else-if="event.visibility === 'public_pending'" class="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
                <ClockIcon class="mr-1.5 h-4 w-4" />
                En attente d'approbation
              </span>
               <span v-else-if="event.visibility === 'public_rejected'" class="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/20">
                <XMarkIcon class="mr-1.5 h-4 w-4" />
                Refusé
              </span>
              <span v-else class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                <GlobeAltIcon class="mr-1.5 h-4 w-4" />
                Public
              </span>
              <router-link 
                v-if="event.organization"
                :to="`/organizations/${event.organization.id}`"
                class="text-sm font-medium hover:underline transition-colors"
                :style="{ color: event.organization?.color_primary || '#4f46e5' }"
              >
                {{ event.organization.name }}
              </router-link>
              <template v-if="event.guest_organizations && event.guest_organizations.length">
                  <span class="text-gray-400 mx-2 text-sm">×</span>
                  <div class="flex flex-wrap gap-1 items-center">
                    <router-link 
                        v-for="(guest, idx) in event.guest_organizations" 
                        :key="guest.id"
                        :to="`/organizations/${guest.id}`"
                        class="text-sm font-medium hover:underline transition-colors block"
                        :style="{ color: guest.color_primary || '#4f46e5' }"
                    >
                        {{ guest.name }}<span v-if="idx < event.guest_organizations.length - 1" class="text-gray-400 font-normal">, </span>
                    </router-link>
                  </div>
              </template>
            </div>
          </div>
          


      </div>
    </div>
    </header>

    <!-- Event Details Grid -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Links Cards -->
        <div v-if="event.event_links && event.event_links.length > 0" class="flex flex-wrap gap-3">
          <a
            v-for="link in event.event_links"
            :key="link.id"
            :href="link.url"
            target="_blank"
            class="flex items-center gap-2 bg-white shadow-md rounded-full px-5 py-3 text-lg font-semibold text-gray-800 hover:shadow-lg hover:text-indigo-600 transition-all border border-gray-100"
          >
            <!-- HelloAsso payment icon -->
            <CreditCardIcon v-if="isHelloAsso(link.url)" class="h-8 w-8 text-green-500 flex-shrink-0" />
            <!-- Social icon -->
            <img v-else-if="getSocialIcon(link.url)" :src="getSocialIcon(link.url)" class="h-8 w-8 object-contain flex-shrink-0" />
            <!-- Generic link icon -->
            <LinkIcon v-else class="h-8 w-8 text-gray-400 flex-shrink-0" />
            {{ link.name }}
          </a>
        </div>

        <!-- Poster / Video -->
        <div v-if="event.video_file || event.video_url" class="bg-white shadow-sm rounded-lg overflow-hidden">
          <video
          :src="(event.video_file?.url ?? event.video_url) ?? undefined"
          :poster="resolveMediaUrl(event.poster_file, 960) ?? event.poster_url ?? undefined"
          controls
          class="w-full object-cover"
          />
        </div>
        <MediaImage
          v-else-if="event.poster_file || event.poster_url"
          :stored-file="event.poster_file"
          :fallback-url="event.poster_url"
          :display-width="960"
          sizes="(max-width: 1024px) 100vw, 66vw"
          :alt="event.title"
          img-class="bg-white shadow-sm rounded-lg overflow-hidden w-full"
        />
        
        <!-- Description -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-3">Description</h2>
          <p class="text-gray-700 whitespace-pre-wrap">{{ event.description || 'Aucune description' }}</p>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <ActionPanel title="Actions">
             <ActionPanelButton
              v-if="event && user"
              :icon="ShareIcon"
              @click="showShareModal = true"
              variant="indigo"
             >
                Partager
             </ActionPanelButton>
             
             <ShareButton 
                v-if="event && user"
                :is-open="showShareModal"
                @close="showShareModal = false"
                :item-id="event.id" 
                item-type="event" 
                :organization="event.organization"
                :guest-organizations="event.guest_organizations"
             />
             
             <ActionPanelButton
              v-if="canEdit"
              :icon="FaceSmileIcon"
              @click="showReactionModal = true"
              variant="violet"
              class="w-full"
            >
              Réactions
            </ActionPanelButton>
            
            <ActionPanelButton
              v-if="canEdit"
              :to="`/events/${event.id}/edit`"
              :icon="PencilIcon"
              variant="purple"
              class="w-full"
            >
              Modifier
            </ActionPanelButton>

            <ActionPanelButton
              v-if="paymentForm?.status === 'approved' && canEdit"
              :to="`/events/${event.id}/validation`"
              :icon="TicketIcon"
              variant="fuchsia"
              class="w-full"
            >
              Validation
            </ActionPanelButton>
            
            <ActionPanelButton
               v-if="canEdit"
               :icon="DocumentDuplicateIcon"
               @click="duplicateEvent"
               variant="pink"
               class="w-full"
            >
              Dupliquer
            </ActionPanelButton>
            
            <ActionPanelButton
              :to="`/events/${event.id}/countdown`"
              target="_blank"
              :icon="ClockIcon"
              variant="rose"  
              class="w-full"
            >
              Compte à rebours
            </ActionPanelButton>
        </ActionPanel>

        <!-- HelloAsso Payment Form -->
        <div v-if="paymentForm" class="shadow-sm rounded-lg overflow-hidden">
          <!-- Paid ticket -->
          <template v-if="myEntry?.completed">
            <div class="bg-green-50 border-2 border-green-200 p-6">
              <div class="flex items-center gap-2 mb-4">
                <TicketIcon class="h-5 w-5 text-green-600" />
                <span class="text-base font-bold text-green-800">Billet confirmé</span>
              </div>

              <div class="space-y-1">
                <p class="text-sm text-gray-800 font-semibold">{{ myEntry.item_name }}</p>
                <div v-if="myEntry.selected_options?.length" class="space-y-0.5">
                  <p v-for="opt in myEntry.selected_options" :key="opt.name" class="text-xs text-gray-600">
                    + {{ opt.name }} ({{ opt.price_cents < 0 ? '-' : '+' }}{{ Math.abs(opt.price_cents / 100).toFixed(2) }}&nbsp;€)
                  </p>
                </div>
              </div>

              <div class="mt-4 pt-4 border-t border-green-200 flex items-center justify-between">
                <span class="text-xs font-medium text-green-700 uppercase tracking-wider">Total payé</span>
                <span class="text-lg font-bold text-green-700">{{ (myEntry.amount_cents / 100).toFixed(2) }}&nbsp;€</span>
              </div>

              <router-link to="/my-payments" class="mt-4 block text-center text-xs font-semibold text-green-700 hover:text-green-900 underline transition-colors">
                Voir mes paiements
              </router-link>
            </div>
          </template>

          <!-- Pending entry: payment initiated but not yet confirmed -->
          <template v-else-if="myEntry && !myEntry.completed && paymentForm.status === 'approved'">
            <div class="bg-amber-50 border-2 border-amber-200 p-6">
              <div class="flex items-center gap-2 mb-3">
                <CreditCardIcon class="h-5 w-5 text-amber-600" />
                <span class="text-base font-bold text-amber-800">Paiement en attente</span>
              </div>
              <p class="text-sm text-amber-700 mb-4">
                Votre paiement n'a pas encore été confirmé. Si vous avez déjà payé, cliquez sur « Vérifier le statut ».
              </p>
              <div class="flex flex-col gap-2">
                <button
                  @click="checkMyPayment"
                  :disabled="checkingPayment"
                  class="flex items-center justify-center gap-2 w-full rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-500 disabled:opacity-50 transition-colors"
                >
                  <CreditCardIcon class="h-4 w-4" />
                  {{ checkingPayment ? 'Vérification…' : 'Vérifier le statut' }}
                </button>
                <button
                  @click="initiatePayment"
                  :disabled="initiatingPayment"
                  class="flex items-center justify-center gap-2 w-full rounded-md bg-white border border-amber-300 px-4 py-2 text-sm font-semibold text-amber-700 hover:bg-amber-50 disabled:opacity-50 transition-colors"
                >
                  {{ initiatingPayment ? 'Redirection…' : 'Recommencer le paiement' }}
                </button>
              </div>
              <p v-if="paymentError" class="mt-2 text-xs text-red-600 text-center">{{ paymentError }}</p>
            </div>
          </template>

          <!-- Approved: show options + pay button -->
          <div v-else-if="paymentForm.status === 'approved'" class="bg-white p-6">
            <h3 class="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon class="h-4 w-4 text-green-600" />
              Paiement
            </h3>
            
            <p class="text-sm text-gray-700 font-medium">{{ paymentForm.item_name }}</p>

            <!-- Options -->
            <div v-if="paymentForm.options?.length" class="mt-3 space-y-2">
              <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Options</p>
              <template v-for="(opt, idx) in paymentForm.options" :key="idx">
                <label
                  v-if="!opt.is_private || (user && opt.allowed_user_ids?.includes(user.id))"
                  class="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="String(opt.id)"
                    v-model="selectedOptionIds"
                    class="h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span class="text-sm text-gray-700">{{ opt.name }}</span>
                  <span class="ml-auto text-sm text-gray-500">{{ opt.price_cents < 0 ? '-' : '+' }}{{ Math.abs(opt.price_cents / 100).toFixed(2) }}&nbsp;€</span>
                </label>
              </template>
            </div>

            <!-- Total -->
            <div class="mt-3 flex items-center justify-between text-sm">
              <span class="text-gray-500">Total</span>
              <span class="font-semibold text-gray-900">{{ paymentTotal.toFixed(2) }}&nbsp;€</span>
            </div>

            <div v-if="!paymentForm.is_open" class="mt-3 text-xs text-amber-700 bg-amber-50 rounded p-2 text-center">
              Les paiements sont temporairement fermés.
            </div>

            <!-- Not yet paid -->
            <template v-else>
              <button
                @click="initiatePayment"
                :disabled="initiatingPayment"
                class="mt-3 flex items-center justify-center gap-2 w-full rounded-md bg-green-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 disabled:opacity-50 transition-colors"
              >
                <CreditCardIcon class="h-4 w-4" />
                {{ initiatingPayment ? 'Redirection…' : "S'inscrire / Payer" }}
              </button>
              <p v-if="paymentError" class="mt-2 text-xs text-red-600 text-center">{{ paymentError }}</p>
            </template>
          </div>

          <!-- Pending: show info for org members -->
          <div v-else-if="paymentForm.status === 'pending' && canEdit" class="bg-white p-6">
            <h3 class="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon class="h-4 w-4 text-green-600" />
              Paiement
            </h3>
            <p class="text-sm text-gray-500 italic">
              Le formulaire de paiement est en attente de validation par l'organisation parente.
            </p>
            <p class="text-xs text-gray-400 mt-1">
              {{ paymentForm.item_name }} — {{ (paymentForm.total_amount_cents / 100).toFixed(2) }}&nbsp;€
            </p>
          </div>

          <!-- Rejected: show rejection message for org members -->
          <div v-else-if="paymentForm.status === 'rejected' && canEdit" class="bg-white p-6">
            <h3 class="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
              <CreditCardIcon class="h-4 w-4 text-green-600" />
              Paiement
            </h3>
            <p class="text-sm text-red-600 font-medium mb-1">Formulaire refusé</p>
            <p v-if="paymentForm.rejection_message" class="text-sm text-gray-600">
              {{ paymentForm.rejection_message }}
            </p>
          </div>
        </div>

        <!-- Date & Time -->
        <div class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Date et heure</h3>
          
          <div class="space-y-3">
            <div>
              <p class="text-xs text-gray-500">Début</p>
              <p class="text-sm font-medium text-gray-900">{{ formatDateTime(event.start_time) }}</p>
            </div>
            
            <div>
              <p class="text-xs text-gray-500">Fin</p>
              <p class="text-sm font-medium text-gray-900">{{ formatDateTime(event.end_time) }}</p>
            </div>
            
            <div>
              <p class="text-xs text-gray-500">Durée</p>
              <p class="text-sm font-medium text-gray-900">{{ getDuration() }}</p>
            </div>
          </div>
        </div>
        <!-- Location -->
        <div v-if="event.location" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Lieu</h3>
          <p class="text-sm text-gray-700 flex items-center">
            <MapPinIcon class="h-5 w-5 text-gray-400 mr-2" />
            <a 
              v-if="event.location_url" 
              :href="event.location_url" 
              target="_blank" 
              class="text-indigo-600 hover:text-indigo-500 hover:underline"
            >
              {{ event.location }}
            </a>
            <span v-else>{{ event.location }}</span>
          </p>
        </div>
        
        <!-- Links -->
        <div v-if="event.event_links && event.event_links.length > 0" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Liens</h3>
          <ul class="space-y-3">
            <li v-for="link in event.event_links" :key="link.id">
              <a 
                :href="link.url" 
                target="_blank" 
                class="flex items-center text-sm text-indigo-600 hover:text-indigo-500 hover:underline group"
              >
                <img v-if="getSocialIcon(link.url)" :src="getSocialIcon(link.url)" class="h-4 w-4 mr-2 object-contain opacity-70 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                <LinkIcon v-else class="h-4 w-4 mr-2 text-gray-400 group-hover:text-indigo-500 flex-shrink-0" />
                {{ link.name }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Visibility & Group Info -->
        <div v-if="event.visibility === 'private'" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-2">Groupe</h3>
          <p class="text-sm text-gray-700 flex items-center">
            <LockClosedIcon class="h-5 w-5 text-gray-400 mr-2" />
            <span v-if="event.group" class="font-medium text-gray-900">{{ event.group.name }}</span>
            <span v-else class="font-medium text-gray-900">Mandat (tous les membres)</span>
          </p>
          <p class="text-xs text-gray-500 mt-1">Événement privé, visible uniquement par les membres du groupe sélectionné.</p>
        </div>
        
        <OrganizationCard
          v-if="event.organization"
          :organization="event.organization"
          :show-type="true"
          :no-border="true"
          class="shadow-sm bg-white rounded-lg"
        />
        
        <!-- Guest Organizations -->
        <OrganizationCard 
            v-for="guest in event.guest_organizations"
            :key="guest.id"
            :organization="guest"
            :show-type="true"
            :no-border="true"
            class="shadow-sm bg-white rounded-lg"
        />
        
        <!-- Tags -->
        <div v-if="event.tags && event.tags.length > 0" class="bg-white shadow-sm rounded-lg p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Tags</h3>
          <div class="flex flex-wrap gap-2">
            <TagBadge 
              v-for="tag in event.tags" 
              :key="tag.id" 
              :tag="tag" 
              :organization="event.organization"
              :subscribed="isSubscribedToTag(tag.id)"
              :show-subscribe="true"
              @toggle-subscription="toggleTagSubscription"
            />
          </div>
        </div>

        

        
      </div>
    </div>
    
    <ReactionAdminModal 
      v-if="canEdit" 
      v-model="showReactionModal" 
      :event-id="event.id"
      @change="loadEvent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { api } from '@/api'
import type {
  EventRead,
  MembershipWithOrganization,
  MyPaymentEntryRead,
  PaymentFormRead,
  SubscriptionOrgEntry,
  SubscriptionTagEntry,
  TagRead,
} from '@/api/types'
import { getSocialIcon, isHelloAsso } from '../utils/social'
import {
  ClockIcon,
  MapPinIcon,
  PencilIcon,
  BellIcon,
  BellSlashIcon,
  XMarkIcon,
  DocumentTextIcon,
  LockClosedIcon,
  GlobeAltIcon,
  InformationCircleIcon,
  DocumentDuplicateIcon,
  LinkIcon,
  CreditCardIcon,
  TicketIcon,
  ShareIcon,
} from '@heroicons/vue/24/outline'
import { formatLocalDate } from '../utils/dateUtils'
import TagBadge from '../components/TagBadge.vue'
import OrganizationCard from '../components/OrganizationCard.vue'
import ReactionList from '../components/ReactionList.vue'
import ReactionAdminModal from '../components/ReactionAdminModal.vue'
import { FaceSmileIcon } from '@heroicons/vue/24/outline'
import { getEventGradient, getEventGradientLight } from '../utils/colorUtils'
import ShareButton from '../components/ShareButton.vue'
import ActionPanel from '../components/ActionPanel.vue'
import ActionPanelButton from '../components/ActionPanelButton.vue'
import MediaImage from '../components/MediaImage.vue'
import { resolveMediaUrl } from '../utils/media.js'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()
const event = ref<EventRead | null>(null)
const paymentForm = ref<PaymentFormRead | null>(null)
const myEntry = ref<MyPaymentEntryRead | null>(null)
const initiatingPayment = ref(false)
const checkingPayment = ref(false)
const paymentError = ref('')
const selectedOptionIds = ref<string[]>([])
const userMemberships = ref<MembershipWithOrganization[]>([])
const subscriptions = ref<(SubscriptionOrgEntry | SubscriptionTagEntry)[]>([])
const loading = ref(true)
const showReactionModal = ref(false)
const showShareModal = ref(false)

const canEdit = computed(() => {
  if (!event.value || !user.value) return false

  // Superadmin can edit anything
  if (user.value.is_superadmin) return true

  // Check if user is admin or member of the event's organization
  const orgId = event.value.organization?.id
  return userMemberships.value.some(m =>
    m.organization_id === orgId &&
    (m.role === 'org_admin' || m.role === 'org_member')
  )
})

const formatDateTime = (dateString: string) => {
  return formatLocalDate(dateString, { dateStyle: 'full', timeStyle: 'short' })
}

const getDuration = () => {
  if (!event.value) return ''

  const start = new Date(event.value.start_time)
  const end = new Date(event.value.end_time)
  const diffMs = end.getTime() - start.getTime()

  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

  if (hours > 0) {
    return `${hours}h${minutes > 0 ? ` ${minutes}min` : ''}`
  }
  return `${minutes} min`
}

const loadEvent = async () => {
  try {
    event.value = await api.events.get_event(String(route.params.id))
  } catch (error) {
    console.error('Failed to load event:', error)
  } finally {
    loading.value = false
  }
}

const paymentTotal = computed(() => {
  if (!paymentForm.value) return 0
  const base = paymentForm.value.total_amount_cents / 100
  const optionById = Object.fromEntries((paymentForm.value.options || []).map(o => [String(o.id), o]))
  const extra = selectedOptionIds.value.reduce((sum, optId) => {
    const opt = optionById[String(optId)]
    return sum + (opt ? opt.price_cents / 100 : 0)
  }, 0)
  return base + extra
})

const initiatePayment = async () => {
  initiatingPayment.value = true
  paymentError.value = ''
  try {
    const res = await api.helloasso.initiate_payment(String(route.params.id), {
      selected_option_ids: selectedOptionIds.value,
    })
    window.location.href = res.redirect_url
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
    paymentError.value = detail || 'Impossible d\'initier le paiement'
    initiatingPayment.value = false
  }
}

const loadPaymentForm = async () => {
  try {
    paymentForm.value = await api.helloasso.get_payment_form(String(route.params.id))

    // Auto-select private options the user is allowed to see
    if (paymentForm.value?.options && user.value) {
      const currentUser = user.value
      paymentForm.value.options.forEach((opt) => {
        if (opt.is_private && opt.allowed_user_ids?.includes(currentUser.id)) {
          const optId = String(opt.id)
          if (!selectedOptionIds.value.includes(optId)) {
            selectedOptionIds.value.push(optId)
          }
        }
      })
    }
  } catch (err: unknown) {
    const status = (err as { response?: { status?: number } }).response?.status
    if (status !== 404) {
      console.error('Failed to load payment form:', err)
    }
    paymentForm.value = null
  }
}

const loadMyEntry = async () => {
  try {
    myEntry.value = await api.helloasso.get_my_entry(String(route.params.id))
  } catch {
    myEntry.value = null
  }
}

const loadUserMemberships = async () => {
  try {
    userMemberships.value = await api.users.get_user_memberships()
  } catch (error) {
    console.error('Failed to load memberships:', error)
  }
}

const loadSubscriptions = async () => {
  try {
    const response = await api.subscriptions.get_my_subscriptions()
    subscriptions.value = [
      ...response.organizations,
      ...response.tags
    ]
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  }
}

import { askPermissionAndSubscribe } from '../utils/push'

const isSubscribedToTag = (tagId: string) => {
  return subscriptions.value.some(sub => (sub as SubscriptionTagEntry).tag?.id === tagId)
}

const toggleTagSubscription = async (tag: TagRead) => {
  const subscription = subscriptions.value.find(sub => (sub as SubscriptionTagEntry).tag?.id === tag.id)

  try {
    if (subscription) {
      await api.subscriptions.unsubscribe_from_tag(tag.id)
      subscriptions.value = subscriptions.value.filter(sub => (sub as SubscriptionTagEntry).tag?.id !== tag.id)
    } else {
      await api.subscriptions.subscribe_to_tag(tag.id)
      await loadSubscriptions()
      askPermissionAndSubscribe()
    }
  } catch (error) {
    console.error('Failed to toggle subscription:', error)
  }
}

const duplicateEvent = () => {
  router.push({
    name: 'CreateEvent',
    state: { duplicateEvent: JSON.parse(JSON.stringify(event.value)) }
  })
}

const checkMyPayment = async () => {
  checkingPayment.value = true
  paymentError.value = ''
  try {
    const res = await api.helloasso.check_payment_status(String(route.params.id))
    await loadMyEntry()
    if (res.completed === 0) {
      paymentError.value = 'Paiement non encore confirmé par HelloAsso. Réessayez dans quelques instants.'
    }
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
    paymentError.value = detail || 'Impossible de vérifier le paiement'
  } finally {
    checkingPayment.value = false
  }
}

const confirmPaymentIfReturning = () => {
  const params = new URLSearchParams(window.location.search)
  const paymentParam = params.get('payment')
  if (!paymentParam) return
  window.history.replaceState({}, '', window.location.pathname)
  if (paymentParam === 'error') {
    paymentError.value = 'Le paiement a échoué ou a été annulé. Vous pouvez réessayer.'
  }
}

onMounted(async () => {
  loadEvent()
  loadUserMemberships()
  loadSubscriptions()
  confirmPaymentIfReturning()
  await loadPaymentForm()
  await loadMyEntry()
})
</script>
