<template>
  <div class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-sm">
      <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">Connexion</h2>
      <p class="mt-2 text-center text-sm text-gray-600">Connectez-vous avec votre compte Campus.</p>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <div v-if="error" class="rounded-md bg-red-50 p-4 mb-4">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>

      <!-- OIDC Login Options -->
      <div>
        <a
          href="/api/auth/login/campus"
          @click="handleLoginClick"
          class="flex w-full items-center justify-center gap-3 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:ring-transparent"
        >
          <span>Se connecter avec Campus</span>
        </a>
        <p class="mt-4 text-xs text-center text-gray-500">
          En vous connectant, vous acceptez que votre nom, prénom et email, ainsi que le contenu que vous créerez sur la plateforme soient stockés sur le serveurs de MiNET et mis à disposition des étudiants et associations du campus. Pour en savoir plus sur le traitement de vos données, veuillez contacter <a href="mailto:dpo@minet.net" class="text-indigo-600 hover:text-indigo-500">dpo@minet.net</a>.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'


const router = useRouter()
const route = useRoute()
const error = ref('')

const handleLoginClick = () => {
  localStorage.setItem('has_clicked_login_before', 'true')
}

onMounted(() => {
  if (route.query.error) {
    error.value = "Erreur lors de la connexion. Veuillez réessayer."
  }

  const hasClickedBefore = localStorage.getItem('has_clicked_login_before')
  const hasAutoClickedSession = sessionStorage.getItem('has_auto_clicked_login_session')

  if (hasClickedBefore && !hasAutoClickedSession && !route.query.error) {
    sessionStorage.setItem('has_auto_clicked_login_session', 'true')
    window.location.href = '/api/auth/login/campus'
  }
})
</script>
