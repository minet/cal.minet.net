<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center p-4">
    <!-- Loading State -->
    <div class="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center" v-if="loading">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mx-auto mb-4"></div>
      <p class="text-gray-500">Chargement...</p>
    </div>

    <!-- Error State -->
    <div class="w-full max-w-md bg-white rounded-lg shadow-lg p-6 text-center" v-else-if="error">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 mb-4">
        <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
      </div>
      <h2 class="text-lg font-medium text-gray-900 mb-2">Erreur</h2>
      <p class="text-sm text-gray-500 mb-6">{{ error }}</p>
      <router-link to="/" class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
        Retour à l'accueil
      </router-link>
    </div>

    <!-- Content State -->
    <div class="w-full max-w-md bg-white rounded-lg shadow-lg overflow-hidden" v-else>
      <div class="px-6 py-8 text-center">
        <div 
          class="mx-auto flex h-16 w-16 items-center justify-center rounded-full mb-6 overflow-hidden"
          :class="!info.color_secondary ? 'bg-indigo-100' : ''"
          :style="{ backgroundColor: info.color_secondary || null }"
        >
           <!-- Logo if available -->
           <img v-if="info.logo_url" :src="info.logo_url" :alt="info.title" class="h-full w-full object-cover" />
           <!-- Icon fallback based on type -->
           <CalendarIcon 
             v-else-if="info.item_type === 'event'" 
             class="h-8 w-8" 
             :class="!info.color_primary ? 'text-indigo-600' : ''"
             :style="{ color: info.color_primary || null }"
           />
           <BuildingOfficeIcon 
             v-else-if="info.item_type === 'organization'" 
             class="h-8 w-8" 
             :class="!info.color_primary ? 'text-indigo-600' : ''"
             :style="{ color: info.color_primary || null }"
           />
           <TagIcon 
             v-else 
             class="h-8 w-8" 
             :class="!info.color_primary ? 'text-indigo-600' : ''"
             :style="{ color: info.color_primary || null }"
           />
        </div>

        <div v-if="info.item_type === 'event'">
           <h2 class="text-2xl font-bold text-gray-900 mb-2">Ajouter l'événement</h2>
           <p class="text-gray-600 mb-6">
              Voulez-vous ajouter cet événement à votre calendrier&nbsp;?<br/>
              Cela ajoutera automatiquement une réaction 👍 de votre part sur l'événement.
           </p>
        </div>
        <div v-else-if="info.item_type === 'organization'">
           <h2 class="text-2xl font-bold text-gray-900 mb-2">S'abonner à l'organisation</h2>
           <p class="text-gray-600 mb-6">
              Tous les événements de cette organisation seront ajoutés automatiquement à votre calendrier.
           </p>
        </div>
         <div v-else-if="info.item_type === 'tag'">
           <h2 class="text-2xl font-bold text-gray-900 mb-2">S'abonner au tag</h2>
           <p class="text-gray-600 mb-6">
              Les événements de l'organisation associés à ce tag seront ajoutés automatiquement à votre calendrier.
           </p>
        </div>
        <div v-else>
           <h2 class="text-2xl font-bold text-gray-900 mb-2">Confirmation</h2>
           <p class="text-gray-600 mb-6">Voulez-vous vous abonner à :</p>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-4 mb-8 border border-gray-100">
             <h3 
               class="text-lg font-semibold mb-1" 
               :class="!customTitleColor ? 'text-indigo-600' : ''"
               :style="{ color: customTitleColor }"
             >
                {{ info.title }}
             </h3>
             <p v-if="info.description" class="text-sm text-gray-500 line-clamp-3">
                {{ info.description }}
             </p>
        </div>

        <div class="flex flex-col sm:flex-row gap-3">
          <button @click="cancel" class="flex-1 inline-flex justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            Annuler
          </button>
          <button @click="confirm" class="flex-1 inline-flex justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed" :disabled="confirming">
            <span v-if="confirming" class="mr-2">
                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </span>
            Confirmer
          </button>
        </div>

        <div class="mt-8 text-sm text-gray-500 space-y-2 border-t border-gray-100 pt-6">
           <p v-if="info.item_type === 'event'">
             Vous pouvez synchroniser votre calendrier sur votre téléphone via <router-link to="/profile/add_calendar" class="text-indigo-600 hover:text-indigo-500 hover:underline">Mon profil</router-link>.
           </p>
           <p v-if="info.item_type === 'organization' || info.item_type === 'tag'">
             Gérez vos abonnements sur <router-link to="/subscriptions" class="text-indigo-600 hover:text-indigo-500 hover:underline">Mes abonnements</router-link>.
             <br/>
             Activez la synchronisation mobile via <router-link to="/profile/add_calendar" class="text-indigo-600 hover:text-indigo-500 hover:underline">Mon profil</router-link>.
           </p>
        </div>
      </div>
    </div>
    <!-- Login Modal -->
    <LoginModal 
      :isOpen="showLoginModal" 
      :description="loginDescription"
      @close="showLoginModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import api from '../utils/api';
import { 
    ExclamationTriangleIcon, 
    CalendarIcon, 
    BuildingOfficeIcon, 
    TagIcon
} from '@heroicons/vue/24/outline';
import LoginModal from '../components/LoginModal.vue';

const route = useRoute();
const router = useRouter();
const { isAuthenticated } = useAuth();

const loading = ref(true);
const error = ref(null);
const info = ref(null);
const confirming = ref(false);
const showLoginModal = ref(false);
const loginDescription = ref("Vous devez être connecté pour vous abonner ou ajouter cet événement à votre calendrier.");

const shortId = route.params.shortId;

const customTitleColor = computed(() => {
  if (!info.value) return null;
  if (info.value.item_type === 'tag' && info.value.tag_color) {
      return info.value.tag_color;
  }
  if (info.value.color_primary) {
      return info.value.color_primary;
  }
  return null;
});

const fetchInfo = async () => {
  try {
    const response = await api.get(`/short-links/info/${shortId}`);
    info.value = response.data;
  } catch (err) {
    console.error(err);
    if (err.response && err.response.status === 403) {
      // Show login modal instead of error message
      loginDescription.value = "Ce contenu est privé. Veuillez vous connecter pour y accéder.";
      showLoginModal.value = true;
      // Also set error just in case modal is closed? Or keep error clear?
      // Since modal covers interaction, maybe fine. 
      // User sees loading then modal? 
      // Or error below modal?
      error.value = "Accès refusé. Connexion requise.";
    } else if (err.response && err.response.status === 404) {
      error.value = "Lien invalide ou expiré.";
    } else {
      error.value = "Une erreur est survenue lors du chargement des informations.";
    }
  } finally {
    loading.value = false;
  }
};

const confirm = async () => {
    if (!isAuthenticated.value) {
        loginDescription.value = "Vous devez être connecté pour vous abonner ou ajouter cet événement à votre calendrier.";
        showLoginModal.value = true;
        return;
    }
    confirming.value = true;
    try {
        await api.post(`/short-links/confirm/${shortId}`);
        // Redirect to the item
        if (info.value.item_type === 'event') {
            router.push(`/events/${info.value.item_id}`);
        } else if (info.value.item_type === 'organization') {
            router.push(`/organizations/${info.value.item_id}`);
        } else if (info.value.item_type === 'tag') {
            router.push('/subscriptions');
        } else {
            router.push('/');
        }
    } catch (err) {
        console.error(err);
        alert("Une erreur est survenue.");
    } finally {
        confirming.value = false;
    }
};

const cancel = () => {
    router.push('/');
};

onMounted(async () => {
  await fetchInfo();
});
</script>
