import axios from 'axios'

const TOKEN_KEY = 'mechman_crm_token'
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (value) => localStorage.setItem(TOKEN_KEY, value)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '' })
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      clearToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export const publicApi = axios.create({ baseURL: import.meta.env.VITE_API_URL || '' })
export default api
