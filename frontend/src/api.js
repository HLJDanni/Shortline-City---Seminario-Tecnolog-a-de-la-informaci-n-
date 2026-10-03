import axios from 'axios'

// Cliente HTTP central. El token JWT se adjunta automáticamente.
const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sc_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('sc_token')
      if (location.pathname !== '/login') location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export default api
