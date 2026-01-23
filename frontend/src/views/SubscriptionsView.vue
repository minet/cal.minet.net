<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-2xl font-semibold text-gray-900">Mes abonnements</h1>
        <p class="mt-2 text-sm text-gray-700">Gérez vos abonnements aux organisations et aux tags. Une fois abonné, vous recevrez dans votre calendrier les événements de l'organisation ou du tag.</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-sm text-gray-500">Chargement...</p>
    </div>

    <div v-else class="mt-8 space-y-8">
      <!-- Organizations -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Organisations</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Les organisations que vous suivez.</p>
        </div>
        <div class="border-t border-gray-200">
          <div v-if="organizationSubscriptions.length > 0" class="divide-y divide-gray-200">
            <div 
              v-for="sub in organizationSubscriptions" 
              :key="sub.id" 
              class="px-4 py-2 sm:px-6 hover:bg-gray-50 transition-colors"
            >
              <OrganizationCard 
                :organization="sub.organization" 
                :show-type="true" 
                :no-border="true"
                :clickable="true"
              >
                <template #side>
                  <button 
                    @click.prevent.stop="unsubscribe(sub)"
                    class="ml-4 text-sm font-medium text-red-600 hover:text-red-800 focus:outline-none bg-transparent whitespace-nowrap"
                  >
                    Se désabonner
                  </button>
                </template>
              </OrganizationCard>
            </div>
          </div>
          <div v-else class="px-4 py-12 sm:px-6 text-center text-gray-500 text-sm">
            <p class="mb-4">Vous n'êtes abonné à aucune organisation.</p>
            <router-link 
              to="/organizations"
              class="w-full justify-center sm:w-auto inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Voir toutes les organisations
            </router-link>
          </div>
        </div>
      </div>

      <!-- Groups -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Groupes</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Les groupes privés dont vous faites partie. Ils vous donnent accès à des événements restreints.</p>
        </div>
        <div class="border-t border-gray-200">
          <div v-if="groups.length > 0" class="px-4 py-5 sm:px-6 flex flex-wrap gap-4">
            <GroupBadge 
              v-for="group in groups" 
              :key="group.id" 
              :group="group" 
              :organization="group.organization"
              @leave="leaveGroup"
            />
          </div>
          <div v-else class="px-4 py-5 sm:px-6 text-center text-gray-500 text-sm">
            Vous ne faites partie d'aucun groupe.
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Tags</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Les tags que vous suivez.</p>
        </div>
        <div class="border-t border-gray-200">
          <div v-if="tagSubscriptions.length > 0" class="px-4 py-5 sm:px-6 flex flex-wrap gap-4">
            <TagBadge 
              v-for="sub in tagSubscriptions" 
              :key="sub.id" 
              :tag="sub.tag" 
              :organization="sub.tag.organization"
              :subscribed="true"
              :show-subscribe="true"
              @toggle-subscription="unsubscribe(sub)"
            />
          </div>
          <div v-else class="px-4 py-5 sm:px-6 text-center text-gray-500 text-sm">
            Vous n'êtes abonné à aucun tag.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../utils/api'
import TagBadge from '../components/TagBadge.vue'
import GroupBadge from '../components/GroupBadge.vue'
import OrganizationCard from '../components/OrganizationCard.vue'

const subscriptions = ref({ organizations: [], tags: [] })
const groups = ref([])
const loading = ref(true)

const organizationSubscriptions = computed(() => {
  return subscriptions.value.organizations || []
})

const tagSubscriptions = computed(() => {
  return subscriptions.value.tags || []
})

const loadSubscriptions = async () => {
  loading.value = true
  try {
    const [subsResponse, groupsResponse] = await Promise.all([
      api.get('/subscriptions/me'),
      api.get('/users/me/groups')
    ])
    subscriptions.value = subsResponse.data
    groups.value = groupsResponse.data
  } catch (error) {
    console.error('Failed to load subscriptions:', error)
  } finally {
    loading.value = false
  }
}

const unsubscribe = async (sub) => {
  if (!confirm('Êtes-vous sûr de vouloir vous désabonner ?')) return

  try {
    if (sub.organization) {
      await api.delete(`/subscriptions/organizations/${sub.organization.id}`)
      subscriptions.value.organizations = subscriptions.value.organizations.filter(s => s.id !== sub.id)
    } else if (sub.tag) {
      await api.delete(`/subscriptions/tags/${sub.tag.id}`)
      subscriptions.value.tags = subscriptions.value.tags.filter(s => s.id !== sub.id)
    }
  } catch (error) {
    console.error('Failed to unsubscribe:', error)
  }
}

const leaveGroup = async (group) => {
  if (!confirm(`Attention : vous êtes sur le point de quitter le groupe "${group.name}".\n\nUne fois parti, vous ne pourrez pas rejoindre ce groupe par vous-même. Un administrateur devra vous ajouter à nouveau.\n\nÊtes-vous sûr de vouloir continuer ?`)) return

  try {
    await api.delete(`/groups/${group.id}/members/me`)
    groups.value = groups.value.filter(g => g.id !== group.id)
  } catch (error) {
    console.error('Failed to leave group:', error)
    alert("Erreur lors de la tentative de quitter le groupe.")
  }
}

onMounted(() => {
  loadSubscriptions()
})
</script>
