import axios from 'axios'
import type {
  LoginRequest,
  LoginResponse,
  Finding,
  FindingListResponse,
  FindingStatusUpdate,
  User,
  Area,
  NotificationSettings,
} from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },
  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
}

// Findings API
export const findingsApi = {
  list: async (params?: {
    area_id?: string
    severity?: string
    status?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
  }): Promise<FindingListResponse> => {
    const response = await api.get<FindingListResponse>('/findings', { params })
    return response.data
  },
  get: async (id: string): Promise<Finding> => {
    const response = await api.get<Finding>(`/findings/${id}`)
    return response.data
  },
  updateStatus: async (id: string, data: FindingStatusUpdate): Promise<Finding> => {
    const response = await api.patch<Finding>(`/findings/${id}/status`, data)
    return response.data
  },
  assign: async (id: string, assignedTo: string | null): Promise<Finding> => {
    const response = await api.patch<Finding>(`/findings/${id}/assign`, null, {
      params: { assigned_to: assignedTo },
    })
    return response.data
  },
  generateSummary: async (dateFrom: string, dateTo?: string) => {
    const response = await api.post('/findings/summary', null, {
      params: { date_from: dateFrom, date_to: dateTo },
    })
    return response.data
  },
}

// Areas API
export const areasApi = {
  list: async (params?: { level?: number; parent_id?: string }): Promise<Area[]> => {
    const response = await api.get<Area[]>('/areas', { params })
    return response.data
  },
  getTree: async (): Promise<Area[]> => {
    const response = await api.get<Area[]>('/areas/tree')
    return response.data
  },
  get: async (id: string): Promise<Area> => {
    const response = await api.get<Area>(`/areas/${id}`)
    return response.data
  },
}

// Users API (Admin only)
export const usersApi = {
  list: async (params?: {
    role?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }): Promise<User[]> => {
    const response = await api.get<User[]>('/admin/users', { params })
    return response.data
  },
  get: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/admin/users/${id}`)
    return response.data
  },
  create: async (data: Partial<User>): Promise<User> => {
    const response = await api.post<User>('/admin/users', data)
    return response.data
  },
  update: async (id: string, data: Partial<User>): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${id}`, data)
    return response.data
  },
}

// Notifications API
export const notificationsApi = {
  getSettings: async (): Promise<NotificationSettings> => {
    const response = await api.get<NotificationSettings>('/notifications/settings')
    return response.data
  },
  updateSettings: async (data: NotificationSettings): Promise<NotificationSettings> => {
    const response = await api.patch<NotificationSettings>('/notifications/settings', data)
    return response.data
  },
  sendTest: async (): Promise<void> => {
    await api.post('/notifications/test')
  },
}

export default api
