import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(BASE_URL + '/merchants/token/refresh/', {
            refresh: refreshToken,
          })
          const newToken = response.data.access
          localStorage.setItem('access_token', newToken)
          originalRequest.headers.Authorization = 'Bearer ' + newToken
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/merchants/login/', { username, password }),
  register: (data: object) =>
    api.post('/merchants/register/', data),
  getProfile: () =>
    api.get('/merchants/profile/'),
  toggleMode: () =>
    api.post('/merchants/mode/toggle/'),
}

export const transactionsApi = {
  list: (params?: object) =>
    api.get('/transactions/', { params }),
  detail: (id: string) =>
    api.get('/transactions/' + id + '/'),
  initiate: (data: object) =>
    api.post('/transactions/initiate/', data),
}

export const webhooksApi = {
  listEndpoints: () =>
    api.get('/webhooks/endpoints/'),
  createEndpoint: (data: object) =>
    api.post('/webhooks/endpoints/', data),
  deleteEndpoint: (id: string) =>
    api.delete('/webhooks/endpoints/' + id + '/'),
  listDeliveries: () =>
    api.get('/webhooks/deliveries/'),
  retryDelivery: (id: string) =>
    api.post('/webhooks/deliveries/' + id + '/retry/'),
}

export const apiKeysApi = {
  list: () =>
    api.get('/merchants/api-keys/'),
  create: (data: object) =>
    api.post('/merchants/api-keys/', data),
  revoke: (id: string) =>
    api.post('/merchants/api-keys/' + id + '/revoke/'),
}

export const refundsApi = {
  list: () =>
    api.get('/refunds/'),
  initiate: (data: object) =>
    api.post('/refunds/initiate/', data),
}

export default api
