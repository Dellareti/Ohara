import { defineStore } from 'pinia'
import axios from 'axios'
import { formatError } from '@/utils/errorUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const useReaderStore = defineStore('reader', {
  state: () => ({
    currentManga: null,
    currentChapter: null,
    currentPage: 0,
    totalPages: 0,

    loading: false,
    error: null,

    readingMode: 'vertical',
    fitMode: 'original',
    theme: 'dark',

    isFullscreen: false,
    hideControls: false,
    showSettings: false,

    navigation: {
      previousChapter: null,
      nextChapter: null,
      chapterIndex: { current: 0, total: 0 },
      allChapters: []
    },

    readingProgress: {},
    readingStartTime: null,

    preloadedPages: new Set(),
    pageCache: new Map(),
    maxCacheSize: 50,

    _saveProgressTimeout: null
  }),

  getters: {
    currentPageData: (state) => {
      if (!state.currentChapter?.chapter?.pages || state.currentPage < 0) return null
      return state.currentChapter.chapter.pages[state.currentPage]
    },

    nextPageData: (state) => {
      if (!state.currentChapter?.chapter?.pages || state.currentPage >= state.totalPages - 1) return null
      return state.currentChapter.chapter.pages[state.currentPage + 1]
    },

    visiblePages: (state) => {
      if (!state.currentChapter?.chapter?.pages) return []

      if (state.readingMode === 'vertical' || state.readingMode === 'webtoon') {
        return state.currentChapter.chapter.pages
      }

      const pages = [state.currentChapter.chapter.pages[state.currentPage]]
      if (state.readingMode === 'double' && state.currentPage < state.totalPages - 1) {
        pages.push(state.currentChapter.chapter.pages[state.currentPage + 1])
      }

      return pages.filter(Boolean)
    },

    progressPercentage: (state) => {
      if (state.totalPages === 0) return 0
      return Number(((state.currentPage / Math.max(state.totalPages - 1, 1)) * 100).toFixed(2))
    },

    hasPreviousChapter: (state) => {
      return state.navigation.previousChapter !== null
    },

    hasNextChapter: (state) => {
      return state.navigation.nextChapter !== null
    },

    currentReadingTime: (state) => {
      if (!state.readingStartTime) return 0
      return Math.floor((Date.now() - state.readingStartTime) / 1000)
    }
  },

  actions: {
    async loadChapter(mangaId, chapterId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}/chapter/${chapterId}`)
        const data = response.data

        this.currentManga = data.manga
        this.currentChapter = data
        this.totalPages = data.chapter.pages.length

        if (data.navigation) {
          this.navigation = {
            previousChapter: data.navigation.previous_chapter,
            nextChapter: data.navigation.next_chapter,
            chapterIndex: data.navigation.chapter_index,
            allChapters: []
          }
        }

        this.loadChapterList(mangaId)

        await this.loadChapterProgress(mangaId, chapterId)

        this.readingStartTime = Date.now()

        this.preloadPages()


        return data

      } catch (error) {
        this.error = formatError(error)
        console.error('Error loading chapter:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async loadChapterList(mangaId) {
      try {
        const chaptersResponse = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}/chapters`)
        const chaptersData = chaptersResponse.data

        if (chaptersData.chapters && Array.isArray(chaptersData.chapters)) {
          this.navigation.allChapters = chaptersData.chapters
        }
      } catch (error) {
        console.warn('Error loading chapter list:', error)
      }
    },

    async loadChapterNavigation(mangaId, currentChapterId) {
      try {
        const chaptersResponse = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}/chapters`)
        const chaptersData = chaptersResponse.data

        if (!chaptersData.chapters || !Array.isArray(chaptersData.chapters)) {
          console.warn('Invalid chapter list')
          this.navigation = {
            previousChapter: null,
            nextChapter: null,
            chapterIndex: { current: 0, total: 0 },
            allChapters: []
          }
          return
        }

        const allChapters = chaptersData.chapters
        this.navigation.allChapters = allChapters

        const currentIndex = allChapters.findIndex(ch =>
          ch.id === currentChapterId ||
          ch.id.includes(currentChapterId) ||
          currentChapterId.includes(ch.id)
        )

        if (currentIndex === -1) {
          console.warn('Current chapter not found in list')
          const flexibleIndex = this.findChapterFlexible(allChapters, currentChapterId)
          if (flexibleIndex !== -1) {
            this.setupNavigation(allChapters, flexibleIndex)
          } else {
            this.navigation = {
              previousChapter: null,
              nextChapter: null,
              chapterIndex: { current: 0, total: allChapters.length },
              allChapters: allChapters
            }
          }
          return
        }

        this.setupNavigation(allChapters, currentIndex)

      } catch (error) {
        console.error('Error loading navigation:', error)
        this.navigation = {
          previousChapter: null,
          nextChapter: null,
          chapterIndex: { current: 0, total: 0 },
          allChapters: []
        }
      }
    },

    findChapterFlexible(chapters, targetId) {
      const strategies = [
        (id) => chapters.findIndex(ch => ch.id === id),

        (id) => chapters.findIndex(ch => ch.id.includes(id) || id.includes(ch.id)),

        (id) => {
          const match = id.match(/(\d+(?:\.\d+)?)/);
          if (match) {
            const number = parseFloat(match[1]);
            return chapters.findIndex(ch => ch.number === number);
          }
          return -1;
        },

        (id) => {
          const normalizedId = id.toLowerCase().replace(/[^a-z0-9]/g, '');
          return chapters.findIndex(ch => {
            const normalizedChId = ch.id.toLowerCase().replace(/[^a-z0-9]/g, '');
            return normalizedChId.includes(normalizedId) || normalizedId.includes(normalizedChId);
          });
        }
      ];

      for (let i = 0; i < strategies.length; i++) {
        const index = strategies[i](targetId);
        if (index !== -1) {
          return index;
        }
      }

      console.warn('No strategy found the chapter');
      return -1;
    },

    setupNavigation(allChapters, currentIndex) {
      const total = allChapters.length;

      const previousChapter = currentIndex < total - 1 ? allChapters[currentIndex + 1] : null;

      const nextChapter = currentIndex > 0 ? allChapters[currentIndex - 1] : null;

      this.navigation = {
        previousChapter: previousChapter ? {
          id: previousChapter.id,
          name: previousChapter.name,
          number: previousChapter.number
        } : null,
        nextChapter: nextChapter ? {
          id: nextChapter.id,
          name: nextChapter.name,
          number: nextChapter.number
        } : null,
        chapterIndex: {
          current: currentIndex + 1,
          total: total
        },
        allChapters: allChapters
      };
    },

    async loadChapterProgress(mangaId, chapterId) {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/progress/${mangaId}/${chapterId}`)
        const progressData = response.data.progress

        if (progressData) {
          this.currentPage = progressData.current_page || 0
          this.readingProgress[chapterId] = progressData
        } else {
          this.currentPage = 0
        }

      } catch (error) {
        console.warn('Error loading progress:', error)
        this.currentPage = 0
      }
    },

    async saveProgress(mangaId, chapterId) {
      if (!mangaId || !chapterId) return

      try {
        const readingTime = this.currentReadingTime

        const response = await axios.post(`${API_BASE_URL}/api/progress/${mangaId}/${chapterId}`, {
          current_page: this.currentPage,
          total_pages: this.totalPages,
          reading_time_seconds: readingTime
        })

        this.readingProgress[chapterId] = response.data.progress

      } catch (error) {
        console.error('Error saving progress:', error)
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++
        this.saveProgressDebounced()
        this.preloadPages()
        return true
      }
      return false
    },

    previousPage() {
      if (this.currentPage > 0) {
        this.currentPage--
        this.saveProgressDebounced()
        return true
      }
      return false
    },

    goToPage(pageNumber) {
      const page = Math.max(0, Math.min(pageNumber, this.totalPages - 1))
      this.currentPage = page
      this.saveProgressDebounced()
      this.preloadPages()
    },

    seekToProgress(percentage) {
      const targetPage = Math.floor((percentage / 100) * this.totalPages)
      this.goToPage(targetPage)
    },

    preloadPages() {
      if (!this.currentChapter?.chapter?.pages) return

      const startIndex = this.currentPage
      const endIndex = Math.min(this.totalPages, this.currentPage + 5)

      for (let i = startIndex; i < endIndex; i++) {
        const page = this.currentChapter.chapter.pages[i]
        if (page && !this.preloadedPages.has(page.url)) {
          this.preloadImage(page.url)
          this.preloadedPages.add(page.url)
        }
      }

      if (this.preloadedPages.size > this.maxCacheSize) {
        const oldPages = Array.from(this.preloadedPages).slice(0, 10)
        oldPages.forEach(url => {
          this.preloadedPages.delete(url)
          this.pageCache.delete(url)
        })
      }
    },

    preloadImage(url) {
      return new Promise((resolve, reject) => {
        if (this.pageCache.has(url)) {
          resolve(this.pageCache.get(url))
          return
        }

        const img = new Image()
        img.onload = () => {
          this.pageCache.set(url, img)
          resolve(img)
        }
        img.onerror = reject
        img.src = url
      })
    },

    updateReadingSettings(settings) {
      Object.assign(this, settings)
      this.saveSettings()
    },

    saveSettings() {
      const settings = {
        readingMode: this.readingMode,
        fitMode: this.fitMode,
        theme: this.theme
      }

      localStorage.setItem('ohara_reader_settings', JSON.stringify(settings))
    },

    loadSettings() {
      try {
        const saved = localStorage.getItem('ohara_reader_settings')
        if (saved) {
          const settings = JSON.parse(saved)
          Object.assign(this, settings)
        }
      } catch (error) {
        console.warn('Error loading settings:', error)
      }
    },

    resetSettings() {
      this.readingMode = 'vertical'
      this.fitMode = 'original'
      this.theme = 'dark'
      this.saveSettings()
    },

    setReadingMode(mode) {
      if (mode === 'single' || mode === 'vertical') {
        this.readingMode = mode
        if (mode === 'vertical') {
          this.fitMode = 'original'
        } else if (mode === 'single') {
          this.fitMode = 'screen'
        }
      } else {
        this.readingMode = 'vertical'
        this.fitMode = 'original'
      }
      this.saveSettings()
    },

    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen
    },

    toggleControls() {
      this.hideControls = !this.hideControls
    },

    toggleSettings() {
      this.showSettings = !this.showSettings
    },

    clearReader() {
      this.currentManga = null
      this.currentChapter = null
      this.currentPage = 0
      this.totalPages = 0
      this.navigation = {
        previousChapter: null,
        nextChapter: null,
        chapterIndex: { current: 0, total: 0 },
        allChapters: []
      }
      this.readingStartTime = null
      this.preloadedPages.clear()
      this.pageCache.clear()
    },

    saveProgressDebounced() {
      if (this._saveProgressTimeout) {
        clearTimeout(this._saveProgressTimeout)
      }

      this._saveProgressTimeout = setTimeout(() => {
        if (this.currentManga && this.currentChapter) {
          this.saveProgress(this.currentManga.id, this.currentChapter.chapter.id)
        }
      }, 1000)
    }
  }
})
