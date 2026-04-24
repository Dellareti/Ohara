import { defineStore } from 'pinia'
import { libraryAPI, apiUtils } from '@/services/api'
import { formatError } from '@/utils/errorUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    mangas: [],
    currentManga: null,
    libraryPath: null,
    totalMangas: 0,
    totalChapters: 0,
    totalPages: 0,
    lastUpdated: null,

    loading: false,
    scanning: false,
    error: null,

    backendOnline: false,

    lastLoadTime: null,
    cacheTimeout: 5 * 60 * 1000,
    isInitialized: false
  }),

  getters: {
    sortedMangas: (state) => {
      return [...state.mangas].sort((a, b) => a.title.localeCompare(b.title))
    },

    libraryStats: (state) => ({
      totalMangas: state.totalMangas,
      totalChapters: state.totalChapters,
      totalPages: state.totalPages,
      averageChaptersPerManga: state.totalMangas > 0 ?
        Math.round(state.totalChapters / state.totalMangas) : 0,
      averagePagesPerChapter: state.totalChapters > 0 ?
        Math.round(state.totalPages / state.totalChapters) : 0
    }),

    libraryStatus: (state) => {
      if (state.scanning) return 'scanning'
      if (state.loading) return 'loading'
      if (state.error) return 'error'
      if (!state.libraryPath) return 'not-configured'
      if (state.mangas.length === 0) return 'empty'
      return 'ready'
    },

    isCacheValid: (state) => {
      if (!state.lastLoadTime) return false
      return (Date.now() - state.lastLoadTime) < state.cacheTimeout
    },

    isLibraryConfigured: (state) => {
      return state.libraryPath && state.libraryPath.trim().length > 0
    }
  },

  actions: {
    async checkBackendStatus() {
      try {
        this.backendOnline = await apiUtils.isBackendOnline()
        return this.backendOnline
      } catch (error) {
        this.backendOnline = false
        console.error('Error checking backend:', error)
        return false
      }
    },

    async clearBackendLibrary() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/clear-library`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })

        if (response.ok) {
        } else {
          console.warn('Error clearing backend:', response.status)
        }
      } catch (error) {
        console.warn('Backend communication error:', error.message)
      }
    },

    async scanLibrary() {
      if (!this.libraryPath) {
        throw new Error('Library path not configured')
      }

      this.loading = true
      this.scanning = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('library_path', this.libraryPath)

        const response = await fetch(`${API_BASE_URL}/api/scan-library`, {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        if (data.library) {
          this.mangas = data.library.mangas || []
          this.totalMangas = data.library.total_mangas || this.mangas.length
          this.totalChapters = data.library.total_chapters || 0
          this.totalPages = data.library.total_pages || 0
          this.lastUpdated = new Date(data.library.last_updated || Date.now())
          this.lastLoadTime = Date.now()

          this.saveLibraryConfig()

          return true
        } else {
          throw new Error(data.message || 'Error scanning library')
        }

      } catch (error) {
        console.error('Scan error:', error)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
        this.scanning = false
      }
    },

    async fetchLibrary(forceRefresh = false) {
      if (this.isInitialized && !forceRefresh && this.isCacheValid && this.mangas.length > 0) {
        return { mangas: this.mangas }
      }

      if (this.scanning) return

      this.loading = true
      this.error = null

      try {
        const response = await libraryAPI.getLibrary()
        const data = response.data

        this.mangas = data.mangas || []
        this.totalMangas = data.total_mangas || data.mangas?.length || 0
        this.totalChapters = data.total_chapters || 0
        this.totalPages = data.total_pages || 0
        this.lastLoadTime = Date.now()
        this.isInitialized = true

        if (data.last_updated) {
          this.lastUpdated = new Date(data.last_updated)
        }

        if (data.scanned_path) {
          this.libraryPath = data.scanned_path
        }

        if (this.mangas.length > 0) {
          this.saveLibraryConfig()
        }

        return data

      } catch (error) {
        this.error = formatError(error)
        console.error('Error loading library:', this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchManga(mangaId) {
      this.loading = true
      this.error = null

      try {
        const response = await libraryAPI.getManga(mangaId)
        const data = response.data

        this.currentManga = data.manga || data

        return this.currentManga

      } catch (error) {
        this.error = formatError(error)
        console.error('Error loading manga:', this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async refreshLibrary() {
      if (this.libraryPath) {
        return await this.scanLibrary()
      } else {
        return await this.fetchLibrary(true)
      }
    },

    searchMangas(query) {
      if (!query || typeof query !== 'string') {
        return this.mangas
      }

      const searchTerm = query.toLowerCase().trim()
      return this.mangas.filter(manga =>
        manga.title.toLowerCase().includes(searchTerm) ||
        manga.id.toLowerCase().includes(searchTerm) ||
        (manga.author && manga.author.toLowerCase().includes(searchTerm))
      )
    },

    async clearLibrary() {
      this.mangas = []
      this.currentManga = null
      this.libraryPath = null
      this.totalMangas = 0
      this.totalChapters = 0
      this.totalPages = 0
      this.lastUpdated = null
      this.lastLoadTime = null
      this.isInitialized = false
      this.error = null

      this.clearLibraryConfig()

      await this.clearBackendLibrary()
    },

    async setLibraryPath(path) {

      try {
        const validation = await this.validatePath(path)
        if (!validation.valid && !validation.is_valid) {
          throw new Error(validation.message)
        }

        const formData = new FormData()
        formData.append('library_path', path)

        const response = await fetch(`${API_BASE_URL}/api/set-library-path`, {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        if (data.status === 'configured') {
          this.libraryPath = path
          this.isInitialized = true

          this.saveLibraryConfig()

          return true
        } else {
          throw new Error(data.message || 'Error configuring library')
        }

      } catch (error) {
        console.error('Error configuring library:', error)
        throw error
      }
    },

    saveLibraryConfig() {
      try {
        if (this.libraryPath) {
          localStorage.setItem('ohara_library_path', this.libraryPath)
          localStorage.setItem('ohara_last_load', this.lastLoadTime?.toString() || '')
          localStorage.setItem('ohara_last_updated', this.lastUpdated?.toISOString() || '')
        }
      } catch (error) {
        console.warn('Error saving to localStorage:', error)
      }
    },

    loadLibraryConfig() {
      try {
        const savedPath = localStorage.getItem('ohara_library_path')
        const savedLastLoad = localStorage.getItem('ohara_last_load')
        const savedLastUpdated = localStorage.getItem('ohara_last_updated')

        if (savedPath) {
          this.libraryPath = savedPath
          if (savedLastLoad) {
            this.lastLoadTime = parseInt(savedLastLoad)
          }
          if (savedLastUpdated) {
            this.lastUpdated = new Date(savedLastUpdated)
          }
          return savedPath
        }
      } catch (error) {
        console.warn('Error loading from localStorage:', error)
      }

      return null
    },

    clearLibraryConfig() {
      try {
        const keysToRemove = [
          'ohara_library_path',
          'ohara_last_load',
          'ohara_last_updated',
          'ohara_mangas_cache',
          'ohara_settings'
        ]

        keysToRemove.forEach(key => {
          localStorage.removeItem(key)
        })
      } catch (error) {
        console.warn('Error clearing localStorage:', error)
      }
    },

    async initialize() {
      if (this.isInitialized) {
        return
      }

      await this.checkBackendStatus()

      if (!this.backendOnline) {
        this.error = `Backend is not accessible. Check that it is running at ${API_BASE_URL}`
        return
      }

      const savedPath = this.loadLibraryConfig()

      if (savedPath && this.isCacheValid && this.mangas.length > 0) {
        this.isInitialized = true
        return
      }

      try {
        await this.fetchLibrary()

        if (this.mangas.length === 0 && savedPath) {
          try {
            await this.scanLibrary()
          } catch (error) {
            console.warn('Error rescanning saved library:', error)
            this.clearLibraryConfig()
          }
        }

        this.isInitialized = true
      } catch (error) {
        console.error('Initialization error:', error)
        this.error = 'Error initializing library'
      }
    },

    async validatePath(path) {
      try {
        const localValidation = apiUtils.validatePathFormat(path)
        if (!localValidation.valid) {
          return {
            valid: false,
            message: localValidation.message
          }
        }

        const response = await libraryAPI.validatePath(path)
        const data = response.data

        return {
          valid: data.is_valid,
          is_valid: data.is_valid,
          message: data.message,
          path: data.path
        }

      } catch (error) {
        console.error('Validation error:', error)
        return {
          valid: false,
          message: formatError(error)
        }
      }
    },
  }
})
