import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import type { UserMeRead } from '../api/types'

const user = ref<UserMeRead | null>(null)
const token = ref<string | null>(null)

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)
  const isSuperAdmin = computed(() => user.value?.is_superadmin ?? false)

  const logout = (): void => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    router.push('/login')
  }

  const loadUser = async (): Promise<void> => {
    try {
      user.value = await api.auth.read_users_me()
      localStorage.setItem('auth_user', JSON.stringify(user.value))
    } catch (error) {
      console.error('Failed to load user:', error)
      logout()
    }
  }

  const initialize = (): void => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')

    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser) as UserMeRead
      // Refresh user data and permissions
      loadUser()
    }
  }

  const setToken = async (authToken: string): Promise<void> => {
    token.value = authToken
    localStorage.setItem('auth_token', authToken)
    await loadUser()
  }

  return {
    user,
    token,
    isAuthenticated,
    isSuperAdmin,
    logout,
    loadUser,
    initialize,
    setToken,
  }
}
