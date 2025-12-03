import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// Search API
export const searchAPI = {
  create: (keyword, limit = 30) => api.post('/search', { keyword, limit }),
  getAll: (skip = 0, limit = 20) => api.get('/search', { params: { skip, limit } }),
  getById: (searchId) => api.get(`/search/${searchId}`),
  getStatus: (searchId) => api.get(`/search/${searchId}/status`),
  delete: (searchId) => api.delete(`/search/${searchId}`),
}

// Videos API
export const videosAPI = {
  getAll: (params) => api.get('/videos', { params }),
  getById: (videoId) => api.get(`/videos/${videoId}`),
  download: (videoId) => api.post(`/videos/${videoId}/download`),
  downloadBatch: (videoIds) => api.post('/videos/download-batch', videoIds),
  getDownloadStatus: (videoId) => api.get(`/videos/${videoId}/download-status`),
  delete: (videoId, deleteFile = false) =>
    api.delete(`/videos/${videoId}`, { params: { delete_file: deleteFile } }),
  getStats: () => api.get('/videos/stats/summary'),
}

// Projects API
export const projectsAPI = {
  create: (title, description = '') => api.post('/projects', { title, description }),
  getAll: (skip = 0, limit = 20) => api.get('/projects', { params: { skip, limit } }),
  getById: (projectId) => api.get(`/projects/${projectId}`),
  update: (projectId, data) => api.put(`/projects/${projectId}`, data),
  addVideos: (projectId, videoIds) =>
    api.post(`/projects/${projectId}/videos`, videoIds),
  generate: (projectId, musicPath = null) =>
    api.post(`/projects/${projectId}/generate`, null, { params: { music_path: musicPath } }),
  getStatus: (projectId) => api.get(`/projects/${projectId}/status`),
  delete: (projectId) => api.delete(`/projects/${projectId}`),
}

export default api
