import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Handle 401 responses
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && !error.config.url.includes('/auth/token')) {
            localStorage.removeItem('auth_token')
            localStorage.removeItem('auth_user')

            // If on a public page, reload to clear state instead of redirecting to login
            const publicPaths = ['/', '/events', '/organizations', '/login', '/register']
            const isPublicPath = publicPaths.includes(window.location.pathname) ||
                window.location.pathname.match(/^\/(events|organizations)\/[^/]+$/)

            if (!isPublicPath) {
                // Store current location for redirect after login
                const currentUrl = window.location.pathname + window.location.search
                sessionStorage.setItem('auth_redirect_url', currentUrl)
                window.location.href = '/login'
            } else {
                // window.location.reload()
            }
        }
        return Promise.reject(error)
    }
)

export default api
