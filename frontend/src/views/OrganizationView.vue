<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-sm text-gray-500">Chargement...</p>
  </div>

  <div v-else-if="organization">
    <!-- Header -->
    <header class="shadow-sm rounded-lg mb-6 overflow-hidden transition-colors" :style="{
      backgroundColor: organization.color_secondary || '#f3f4f6',
      borderTop: `4px solid ${organization.color_primary || '#4f46e5'}`
    }">
      <div class="px-4 py-6 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="h-16 w-16 rounded-xl flex items-center justify-center overflow-hidden transition-colors"
              :style="{ backgroundColor: organization.color_secondary || '#f3f4f6' }"
              :class="{ 'bg-indigo-100': !organization.color_secondary }">
              <img v-if="organization.logo_file || organization.logo_url" :src="(resolveMediaUrl(organization.logo_file, 96) ?? organization.logo_url) ?? undefined" :alt="organization.name"
                class="h-full w-full object-cover" />
              <span v-else class="text-2xl font-semibold" :style="{ color: organization.color_primary || '#4f46e5' }"
                :class="{ 'text-indigo-600': !organization.color_primary }">{{ organization.name.charAt(0) }}</span>
            </div>
            <div>
              <h1 class="text-3xl font-bold tracking-tight text-gray-900">{{ organization.name }}</h1>
              <p class="text-sm text-gray-500">{{ organization.type }}</p>
            </div>
          </div>


        </div>

      </div>
    </header>

    <ActionPanel title="Actions" content-class="flex flex-col lg:flex-row lg:flex-wrap lg:gap-3 lg:space-y-0">
      <DocsHint path="/partager" search="Partager une organisation">
        <ActionPanelButton v-if="isMember || (user && user.is_superadmin)" @click="showOrgShareModal = true"
          :icon="ShareIcon" variant="indigo" class="w-full lg:w-auto">
          Partager
        </ActionPanelButton>
      </DocsHint>

      <SubscribeButton v-if="!isMember" :organization-id="organization.id" class="w-full lg:w-auto" />

      <DocsHint path="/tags-organisation" search="tags">
        <ActionPanelButton v-if="canEdit" :to="`/organizations/${organization.id}/tags`" :icon="TagIcon" variant="violet"
          class="w-full lg:w-auto">
          Tags
        </ActionPanelButton>
      </DocsHint>

      <DocsHint path="/groupes-evenements" search="groupes">
        <ActionPanelButton v-if="canEdit" :to="`/organizations/${organization.id}/groups`" :icon="UsersIcon"
          variant="purple" class="w-full lg:w-auto">
          Groupes
        </ActionPanelButton>
      </DocsHint>

      <DocsHint path="/gerer-les-membres" search="membres">
        <ActionPanelButton v-if="isMember" :to="`/organizations/${organization.id}/members`" :icon="UserGroupIcon"
          variant="fuchsia" class="w-full lg:w-auto">
          {{ canEdit ? 'Membres' : 'Mon poste' }}
        </ActionPanelButton>
      </DocsHint>

      <DocsHint path="/configurer-helloasso" search="HelloAsso">
        <ActionPanelButton v-if="canEdit" :to="`/organizations/${organization.id}/helloasso`" :icon="CreditCardIcon"
          variant="pink" class="w-full lg:w-auto">
          HelloAsso
        </ActionPanelButton>
      </DocsHint>

      <DocsHint path="/personnaliser-organisation" search="Personnaliser">
        <ActionPanelButton v-if="canEdit" :to="`/organizations/${organization.id}/edit`" :icon="PencilIcon" variant="rose"
          class="w-full lg:w-auto">
          Modifier
        </ActionPanelButton>
      </DocsHint>

      <template #footer>
        <p v-if="!isMember" class="text-xs text-gray-500 mt-2 text-center">
          S'abonner ajoute les événements à votre <router-link to="/profile"
            class="text-indigo-600 hover:underline">calendrier</router-link>
        </p>
      </template>
    </ActionPanel>

    <!-- Description -->
    <div v-if="organization.description" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Description</h2>
      <OrgDescriptionRenderer :description="organization.description" :members="members"
        :allowed-image-urls="orgImages.map(i => i.url).filter((u): u is string => u !== null)" />
    </div>

    <!-- Parent Organization -->
    <div v-if="parent" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Organisation parente</h2>
      <router-link :to="`/organizations/${parent.id}`"
        class="flex items-center space-x-3 hover:bg-gray-50 p-3 rounded-lg transition-colors">
        <div class="h-10 w-10 rounded-full flex items-center justify-center transition-colors"
          :style="{ backgroundColor: parent.color_secondary || '#f3f4f6' }">
          <img v-if="parent.logo_file || parent.logo_url" :src="(resolveMediaUrl(parent.logo_file, 64) ?? parent.logo_url) ?? undefined" :alt="parent.name"
            class="h-full w-full object-cover rounded-full" />
          <span v-else class="font-semibold" :style="{ color: parent.color_primary || '#4f46e5' }">{{
            parent.name.charAt(0)
            }}</span>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900">{{ parent.name }}</p>
          <p class="text-xs text-gray-500">{{ parent.type }}</p>
        </div>
      </router-link>
    </div>

    <!-- Custom Links -->
    <div v-if="organization.organization_links && organization.organization_links.length > 0"
      class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-3">Liens</h2>
      <ul class="space-y-2">
        <li v-for="link in organization.organization_links" :key="link.id">
          <a :href="link.url" target="_blank" class="text-indigo-600 hover:text-indigo-800 flex items-center">
            <img v-if="getSocialIcon(link.url)" :src="getSocialIcon(link.url)"
              class="h-4 w-4 mr-2 object-contain opacity-70 group-hover:opacity-100 transition-opacity flex-shrink-0" />
            <LinkIcon v-else class="h-4 w-4 mr-2 flex-shrink-0" />
            {{ link.name }}
          </a>
        </li>
      </ul>
    </div>

    <!-- Tags -->
    <div v-if="tags.length > 0" class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Tags</h2>
      <div class="flex flex-wrap gap-2">
        <TagBadge v-for="tag in tags" :key="tag.id" :tag="tag" :organization="organization"
          :subscribed="isSubscribedToTag(tag.id)" :show-subscribe="true"
          :show-share="isMember || !!user?.is_superadmin" @toggle-subscription="toggleTagSubscription"
          @share="openTagShare" />
      </div>
    </div>

    <!-- Members -->
    <div class="bg-white shadow-sm rounded-lg p-6 mb-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Membres</h2>

      <div v-if="loadingMembers" class="text-center py-4">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <div v-else-if="members.length === 0" class="text-center py-8">
        <p class="text-sm text-gray-500">Aucun membre</p>
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <MemberCard v-for="member in members" :key="member.user_id" :member="member"
          :show-request-transfer="!isMember && !!user && showJoinHelp" @request-transfer="openRequestTransfer" />
      </div>

      <p v-if="!isMember && !!user && !showJoinHelp" class="text-xs text-gray-500 mt-4 text-center">
        <button type="button" @click="showJoinHelp = true" class="text-indigo-600 hover:underline">
          Je fais partie de cette organisation, comment la rejoindre sur Calend'INT ?
        </button>
      </p>
    </div>

    <!-- Future Events -->
    <div class="bg-white shadow-sm rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Événements à venir</h2>

      <div v-if="loadingEvents" class="text-center py-4">
        <p class="text-sm text-gray-500">Chargement...</p>
      </div>

      <div v-else-if="events.length === 0" class="text-center py-8">
        <p class="text-sm text-gray-500">Aucun événement à venir</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-[repeat(auto-fill,18rem)] gap-6 justify-start mt-4">
        <EventCard v-for="event in events" :key="event.id" :event="event" />
      </div>
    </div>
    <!-- Share Buttons -->
    <ShareButton v-if="showOrgShareModal" :is-open="showOrgShareModal" @close="showOrgShareModal = false" :item-id="organization.id" item-type="organization"
      :organization="organization" />
    <ShareButton v-if="activeShareTag" :is-open="showTagShareModal" @close="showTagShareModal = false" :item-id="activeShareTag.id" item-type="tag" />

    <!-- Request Transfer Modal -->
    <TransitionRoot as="template" :show="showRequestTransferModal">
      <Dialog as="div" class="relative z-50" @close="showRequestTransferModal = false">
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
                  <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-100">
                    <UserPlusIcon class="h-6 w-6 text-amber-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      Demander le poste « {{ requestTransferTarget?.title || 'Membre' }} »
                    </DialogTitle>
                    <div class="mt-2 text-left">
                      <p class="text-sm text-gray-500">
                        Un e-mail va être envoyé à <strong>{{ requestTransferTarget?.full_name || requestTransferTarget?.email }}</strong>
                        pour lui demander de vous transférer ce poste.
                      </p>
                      <p class="mt-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-md p-3">
                        Ce n'est pas la voie privilégiée : la passation devrait normalement être
                        initiée par la personne en poste, une fois le nouveau mandat décidé.
                        N'utilisez ce bouton que si elle n'a pas fait la démarche elle-même.
                        En cas de doute, contactez un·e administrateur·rice de l'organisation ou
                        le/la secrétaire du BDE plutôt que d'envoyer cette demande.
                      </p>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button type="button" :disabled="sendingRequestTransfer"
                    class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:col-start-2 disabled:opacity-50"
                    @click="confirmRequestTransfer">
                    {{ sendingRequestTransfer ? 'Envoi...' : "Confirmer l'envoi" }}
                  </button>
                  <button type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="showRequestTransferModal = false">
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

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import SubscribeButton from '../components/SubscribeButton.vue'
import ShareButton from '../components/ShareButton.vue'
import ActionPanel from '../components/ActionPanel.vue'
import ActionPanelButton from '../components/ActionPanelButton.vue'
import MemberCard from '../components/MemberCard.vue'
import EventCard from '../components/EventCard.vue'
import OrgDescriptionRenderer from '../components/OrgDescriptionRenderer.vue'

import TagBadge from '../components/TagBadge.vue'
import { api } from '@/api'
import { getSocialIcon } from '../utils/social'
import { resolveMediaUrl } from '../utils/media.js'
import type {
  OrganizationRead,
  OrgMember,
  EventRead,
  TagRead,
  OrganizationImageRead,
  SubscriptionOrgEntry,
  SubscriptionTagEntry,
} from '@/api/types'
import {
  PencilIcon,
  UserGroupIcon,
  TagIcon,
  UsersIcon,
  LinkIcon,
  CreditCardIcon,
  ShareIcon,
  UserPlusIcon
} from '@heroicons/vue/24/outline'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'

const route = useRoute()
const { user } = useAuth()
const organization = ref<OrganizationRead | null>(null)
const parent = ref<OrganizationRead | null>(null)
const members = ref<OrgMember[]>([])
const events = ref<EventRead[]>([])
const tags = ref<TagRead[]>([])
const subscriptions = ref<(SubscriptionOrgEntry | SubscriptionTagEntry)[]>([])
const canEdit = ref(false)
const loading = ref(true)
const loadingMembers = ref(false)
const loadingEvents = ref(false)
const orgImages = ref<OrganizationImageRead[]>([])

const showOrgShareModal = ref(false)
const showTagShareModal = ref(false)
const activeShareTag = ref<TagRead | null>(null)

const openTagShare = (tag: TagRead) => {
  activeShareTag.value = tag
  showTagShareModal.value = true
}

const showJoinHelp = ref(false)
const showRequestTransferModal = ref(false)
const sendingRequestTransfer = ref(false)
const requestTransferTarget = ref<OrgMember | null>(null)

const openRequestTransfer = (member: OrgMember) => {
  requestTransferTarget.value = member
  showRequestTransferModal.value = true
}

const confirmRequestTransfer = async () => {
  if (!requestTransferTarget.value || !organization.value) return
  sendingRequestTransfer.value = true
  try {
    await api.organizations.request_membership_transfer(organization.value.id, requestTransferTarget.value.id)
    showRequestTransferModal.value = false
    alert('Votre demande a été envoyée par e-mail à la personne actuellement en poste.')
  } catch (error) {
    console.error('Failed to request membership transfer:', error)
    const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    alert('Erreur : ' + (detail || "impossible d'envoyer la demande"))
  } finally {
    sendingRequestTransfer.value = false
  }
}

const isMember = computed(() => {
  return members.value.some(m => m.user_id === user.value?.id)
})

const getRoleLabel = (role: string): string => {
  const labels: Record<string, string> = {
    'superadmin': 'Superadmin',
    'org_admin': 'Administrateur',
    'org_member': 'Éditeur',
    'org_viewer': 'Lecteur',
  }
  return labels[role] ?? role
}

const getRoleBadgeClass = (role: string): string => {
  const classes: Record<string, string> = {
    'superadmin': 'bg-purple-50 text-purple-700 ring-purple-700/10',
    'org_admin': 'bg-blue-50 text-blue-700 ring-blue-700/10',
    'org_member': 'bg-green-50 text-green-700 ring-green-600/20',
    'org_viewer': 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  }
  return classes[role] ?? 'bg-gray-50 text-gray-700 ring-gray-600/20'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadOrganization = async () => {
  try {
    organization.value = await api.organizations.get_organization(String(route.params.id))

    // Load parent if exists
    if (organization.value.parent_id) {
      parent.value = await api.organizations.get_organization(organization.value.parent_id)
    } else {
      parent.value = null
    }
  } catch (error) {
    console.error('Failed to load organization:', error)
  } finally {
    loading.value = false
  }
}

const loadMembers = async () => {
  loadingMembers.value = true
  try {
    members.value = await api.organizations.get_organization_members(String(route.params.id))
  } catch (error) {
    console.error('Failed to load members:', error)
  } finally {
    loadingMembers.value = false
  }
}

const loadEvents = async () => {
  loadingEvents.value = true
  try {
    events.value = await api.organizations.get_organization_events(String(route.params.id))
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loadingEvents.value = false
  }
}

const loadTags = async () => {
  try {
    tags.value = await api.tags.get_organization_tags(String(route.params.id))
  } catch (error) {
    console.error('Failed to load tags:', error)
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

const checkCanEdit = async () => {
  try {
    const response = await api.organizations.can_edit_organization(String(route.params.id))
    canEdit.value = response.can_edit
  } catch (error) {
    console.error('Failed to check edit permission:', error)
  }
}

const loadImages = async () => {
  try {
    orgImages.value = await api.organization_images.list_organization_images(String(route.params.id))
  } catch {
    // Silently ignore – user likely not a member
  }
}

import { askPermissionAndSubscribe } from '../utils/push'

const isSubscribedToTag = (tagId: string): boolean => {
  return subscriptions.value.some(sub => {
    if ('tag' in sub) return sub.tag.id === tagId
    return false
  })
}

const toggleTagSubscription = async (tag: TagRead) => {
  const subscription = subscriptions.value.find(sub => {
    if ('tag' in sub) return sub.tag.id === tag.id
    return false
  })

  try {
    if (subscription) {
      await api.subscriptions.unsubscribe_from_tag(tag.id)
      subscriptions.value = subscriptions.value.filter(sub => {
        if ('tag' in sub) return sub.tag.id !== tag.id
        return true
      })
    } else {
      await api.subscriptions.subscribe_to_tag(tag.id)
      const newEntry: SubscriptionTagEntry = {
        id: tag.id,
        tag: { id: tag.id, name: tag.name, color: tag.color, organization: null }
      }
      subscriptions.value.push(newEntry)
      askPermissionAndSubscribe()
    }
  } catch (error) {
    console.error('Failed to toggle subscription:', error)
  }
}

const loadAll = () => {
  loading.value = true
  loadOrganization()
  loadMembers().then(() => {
    // images require membership – load after members to avoid 403 for non-members
    loadImages()
  })
  loadEvents()
  loadTags()
  loadSubscriptions()
  checkCanEdit()
}

// Watch for route changes to reload data when navigating between organizations
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadAll()
  }
})

onMounted(() => {
  loadAll()
})

// suppress unused variable warnings for helper functions only used in template or future use
void getRoleLabel
void getRoleBadgeClass
void formatDate
</script>
