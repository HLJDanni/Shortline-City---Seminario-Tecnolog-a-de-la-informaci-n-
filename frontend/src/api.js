import axios from 'axios'

// Cliente HTTP central. La sesión viaja en una cookie HttpOnly que fija el
// backend al iniciar sesión: JavaScript nunca ve ni guarda el token.
const api = axios.create({ baseURL: '/api', withCredentials: true })

api.interceptors.response.use(
  (r) => r,
  (error) => {
    const url = error.config?.url || ''
    const esAuth = url.startsWith('/auth/')
    if (error.response?.status === 401 && !esAuth && location.pathname !== '/login') {
      location.assign('/login')
    }
    return Promise.reject(error)
  },
)

export default api
