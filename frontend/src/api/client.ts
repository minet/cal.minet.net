import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'

const PUBLIC_PATHS = [
  '/',
  '/events',
  '/organizations',
  '/login',
  '/register',
  '/dashboard',
  '/walldisplay',
]

function isPublicPath(pathname: string): boolean {
  if (PUBLIC_PATHS.includes(pathname)) return true
  if (/^\/(events|organizations)\/[^/]+$/.test(pathname)) return true
  if (/^\/events\/[^/]+\/countdown$/.test(pathname)) return true
  if (/^\/consent\/[^/]+$/.test(pathname)) return true
  return false
}

export function createApiClient(baseURL = '/api'): AxiosInstance {
  const instance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
  })

  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  instance.interceptors.response.use(
    (response) => response,
    (error: unknown) => {
      if (
        axios.isAxiosError(error) &&
        error.response?.status === 401 &&
        !error.config?.url?.includes('/auth/token')
      ) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')

        if (!isPublicPath(window.location.pathname)) {
          const currentUrl = window.location.pathname + window.location.search
          localStorage.setItem('auth_redirect_url', currentUrl)
          console.log('User is not authenticated, page :', window.location.pathname)
          window.location.href = '/login'
        }
      }
      return Promise.reject(error)
    },
  )

  return instance
}

/** Shared singleton used by all API resource classes. */
export const httpClient = createApiClient()

export type { AxiosRequestConfig }
