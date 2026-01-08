import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const user = ref(null)
const token = ref(null)

export function useAuth() {
    const router = useRouter()

    const isAuthenticated = computed(() => !!token.value)
    const isSuperAdmin = computed(() => user.value?.is_superadmin || false)

    // Removed login and register functions as OIDC is the only auth method

    const logout = () => {
        user.value = null
        token.value = null
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        router.push('/login')
    }

    const loadUser = async () => {
        try {
            const response = await api.get('/auth/me')
            user.value = response.data
            localStorage.setItem('auth_user', JSON.stringify(user.value))
        } catch (error) {
            console.error('Failed to load user:', error)
            logout()
        }
    }


    const initialize = () => {
        const savedToken = localStorage.getItem('auth_token')
        const savedUser = localStorage.getItem('auth_user')

        if (savedToken && savedUser) {
            token.value = savedToken
            user.value = JSON.parse(savedUser)
            // Refresh user data and permissions
            loadUser()
        }
    }

    const setToken = async (authToken) => {
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
        setToken
    }
}
