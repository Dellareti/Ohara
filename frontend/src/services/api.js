import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

export const libraryAPI = {
  scanLibrary: async (libraryPath) => {
    try {

      const formData = new FormData()
      formData.append('library_path', libraryPath)

      const response = await axios.post(`${API_BASE_URL}/api/scan-library`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000
      })

      return response
    } catch (error) {
      console.error('Error scanning library:', error)
      throw error
    }
  },

  getLibrary: () => api.get('/api/library'),
  getManga: (mangaId) => api.get(`/api/manga/${mangaId}`),
  healthCheck: () => api.get('/health'),
  test: () => api.get('/api/test'),
  validatePath: (path) => api.get('/api/validate-path', { params: { path } }),
  clearLibrary: () => api.post('/api/clear-library')
}

export const apiUtils = {
  validatePathFormat: (path) => {
    if (!path || typeof path !== 'string') {
      return {
        valid: false,
        message: 'Path must be a valid string'
      }
    }

    const trimmedPath = path.trim()

    if (trimmedPath.length === 0) {
      return {
        valid: false,
        message: 'Path cannot be empty'
      }
    }

    const isWindows = /^[A-Za-z]:\\/.test(trimmedPath)
    const isUnix = trimmedPath.startsWith('/')
    const isRelative = !isWindows && !isUnix

    if (!isWindows && !isUnix && !isRelative) {
      return {
        valid: false,
        message: 'Invalid path format. Use /home/user/Manga (Linux/Mac) or C:\\Manga (Windows)'
      }
    }

    const forbiddenChars = isWindows
      ? /[<>"|?*]/
      : /[\0]/

    if (forbiddenChars.test(trimmedPath)) {
      return {
        valid: false,
        message: `Path contains invalid characters: ${isWindows ? '<>"|?*' : 'control characters'}`
      }
    }

    if (isWindows && trimmedPath.length > 260) {
      return {
        valid: false,
        message: 'Path too long (maximum 260 characters on Windows)'
      }
    }

    if (trimmedPath.length > 4096) {
      return {
        valid: false,
        message: 'Path too long (maximum 4096 characters)'
      }
    }

    return {
      valid: true,
      message: 'Valid path',
      normalized: trimmedPath
    }
  },

  isBackendOnline: async () => {
    try {
      const response = await api.get('/api/test', { timeout: 5000 })
      return response.status === 200
    } catch (error) {
      return false
    }
  },

  formatError: (error) => {
    if (error.response) {
      const data = error.response.data

      if (data && typeof data === 'object') {
        return data.message || data.detail || `Error ${error.response.status}`
      }

      return `Error ${error.response.status}: ${error.response.statusText}`
    } else if (error.request) {
      return 'Connection error with the server. Check that the backend is running.'
    } else {
      return error.message || 'Unknown error'
    }
  }
}

export default api
