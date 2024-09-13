import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const auth = {
  login: (username: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: { username: string; email: string; password: string; role: string }) =>
    api.post('/auth/register', data),
}

export const documents = {
  list: () => api.get('/documents/'),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  get: (id: number) => api.get(`/documents/${id}`),
  process: (id: number) => api.post(`/documents/${id}/process`),
}

export const entities = {
  extract: (docId: number) => api.post(`/entities/extract/${docId}`),
  get: (docId: number) => api.get(`/entities/${docId}`),
  getCodes: (entityId: number) => api.get(`/entities/${entityId}/codes`),
}

export const rag = {
  query: (query: string, topK: number = 5) =>
    api.post('/rag/query', { query, top_k: topK }),
}

export const audit = {
  logs: (params?: { user_id?: number; action?: string; skip?: number; limit?: number }) =>
    api.get('/audit/logs', { params }),
}

export default api
