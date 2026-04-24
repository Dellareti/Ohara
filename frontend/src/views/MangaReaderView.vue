<template>
  <div class="manga-reader" :class="{ 
    'fullscreen': readerStore.isFullscreen, 
    'controls-hidden': readerStore.hideControls,
    [`theme-${readerStore.theme}`]: true
  }">
    <!-- Loading State -->
    <div v-if="loading || readerStore.loading" class="reader-loading">
      <div class="spinner"></div>
      <p>Loading chapter...</p>
    </div>

    <!-- Error State -->
    <div v-if="error || readerStore.error" class="reader-error">
      <h2>Error Loading Chapter</h2>
      <p>{{ error || readerStore.error }}</p>
      <button @click="loadChapter" class="retry-btn">Try Again</button>
    </div>

    <!-- Reader Content -->
    <div v-if="!loading && !readerStore.loading && !error && !readerStore.error && readerStore.currentChapter" class="reader-content">
      <!-- Header Controls -->
      <div class="reader-header" :class="{ 'hidden': readerStore.hideControls }">
        <div class="header-left">
          <button @click="goBack" class="control-btn back-btn">Back</button>
          <div class="chapter-info">
            <h3>{{ readerStore.currentManga?.title || 'Loading...' }}</h3>
            <p>{{ readerStore.currentChapter?.chapter?.name || 'Loading...' }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="page-counter">
            {{ readerStore.currentPage + 1 }} / {{ readerStore.totalPages }}
          </div>
          <button @click="toggleFullscreen" class="control-btn">
            {{ readerStore.isFullscreen ? '🗖' : '🗗' }}
          </button>
          <button @click="toggleSettings" class="control-btn">⚙️</button>
        </div>
      </div>

      <!-- Page Viewer -->
      <div class="page-viewer" :class="`mode-${readerStore.readingMode}`" @click="toggleControls">
        <!-- Single Page Mode -->
        <div v-if="readerStore.readingMode === 'single'" class="single-page-container">
          <img
            :src="getPageImageUrl(readerStore.currentPage)"
            :alt="`Page ${readerStore.currentPage + 1}`"
            class="manga-page"
            :class="`fit-${readerStore.fitMode}`"
            @error="handleImageError"
            @load="handleImageLoad"
          />
        </div>


        <!-- Vertical Mode -->
        <div v-else-if="readerStore.readingMode === 'vertical'" class="vertical-container">
          <div class="vertical-pages">
            <div
              v-for="pageIndex in readerStore.totalPages"
              :key="pageIndex"
              class="vertical-page-wrapper"
            >
              <img
                :src="getPageImageUrl(pageIndex - 1)"
                :alt="`Page ${pageIndex}`"
                class="manga-page vertical-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
                loading="lazy"
              />
            </div>
          </div>
        </div>

      </div>

      <!-- Footer Controls -->
      <div class="reader-footer" :class="{ 'hidden': readerStore.hideControls }">
        <div class="progress-bar">
          <div class="progress-track" @click="seekToPosition">
            <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            <div class="progress-thumb" :style="{ left: progressPercentage + '%' }"></div>
          </div>
        </div>

        <div class="footer-controls">
          <button
            @click="previousChapter"
            :disabled="!hasPreviousChapter"
            class="control-btn"
          >
            ⏮️ Prev. Chapter
          </button>
          <button @click="previousPage" :disabled="!canGoPrevious" class="control-btn">
            ⏪ Previous
          </button>
          <select :value="readerStore.readingMode" @change="changeReadingMode($event.target.value)" class="mode-select">
            <option value="single">Horizontal</option>
            <option value="vertical">Vertical</option>
          </select>
          <button @click="nextPage" :disabled="!canGoNext" class="control-btn">
            Next ⏩
          </button>
          <button
            @click="nextChapter"
            :disabled="!hasNextChapter"
            class="control-btn"
          >
            Next Chapter ⏭️
          </button>
        </div>
      </div>

      <!-- Settings Panel -->
      <div v-if="readerStore.showSettings" class="settings-panel" @click.stop>
        <div class="settings-content">
          <div class="settings-header">
            <h3>Reading Settings</h3>
            <button @click="closeSettings" class="close-btn">✕</button>
          </div>

          <div class="setting-group">
            <label class="setting-label">Image Fit:</label>
            <select v-model="readerStore.fitMode" class="setting-select">
              <option value="width">Fit Width</option>
              <option value="height">Fit Height</option>
              <option value="screen">Fit Screen</option>
              <option value="original">Original Size</option>
            </select>
          </div>


          <div class="setting-group">
            <label class="setting-label">Theme:</label>
            <select v-model="readerStore.theme" class="setting-select">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="sepia">Sepia</option>
            </select>
          </div>

          <div class="setting-actions">
            <button @click="resetSettings" class="secondary-btn">Reset</button>
            <button @click="applySettings" class="primary-btn">Apply</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReaderStore } from '@/store/reader'

const API_BASE_URL = 'http://localhost:8000'

export default {
  name: 'MangaReaderView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const readerStore = useReaderStore()

    // Reactive data
    const loading = ref(false)
    const error = ref(null)
    
    // Auto-hide controls
    let controlsTimeout = null

    // Computed properties
    const mangaId = computed(() => route.params.mangaId)
    const chapterId = computed(() => route.params.chapterId)
    
    const progressPercentage = computed(() => {
      return readerStore.progressPercentage || 0
    })


    const canGoPrevious = computed(() => {
      return readerStore.currentPage > 0
    })

    const canGoNext = computed(() => {
      return readerStore.currentPage < readerStore.totalPages - 1
    })

    const hasPreviousChapter = computed(() => {
      return readerStore.hasPreviousChapter
    })

    const hasNextChapter = computed(() => {
      return readerStore.hasNextChapter
    })

    // Methods
    const getPageImageUrl = (pageIndex) => {
      if (!readerStore.currentChapter?.chapter?.pages) {
        return `https://via.placeholder.com/800x1200/333/fff?text=No+Data+Available`
      }

      const page = readerStore.currentChapter.chapter.pages[pageIndex]
      if (!page) {
        return `https://via.placeholder.com/800x1200/ff6b6b/fff?text=Page+${pageIndex + 1}+Not+Found`
      }

      let imageUrl = ''

      if (page.url) {
        imageUrl = page.url
      } else if (page.path) {
        imageUrl = page.path.startsWith('http') ? page.path : `${API_BASE_URL}${page.path}`
      } else {
        imageUrl = `${API_BASE_URL}/api/manga/${mangaId.value}/chapter/${chapterId.value}/page/${pageIndex}`
      }

      return imageUrl
    }

    const handleImageError = (event) => {
      event.target.src = `https://via.placeholder.com/800x1200/ff6b6b/fff?text=Error+Loading+Page`
    }

    const handleImageLoad = (event) => {
    }

    const loadChapter = async () => {
      if (!mangaId.value || !chapterId.value) {
        error.value = 'Invalid route parameters'
        return
      }

      loading.value = true
      error.value = null

      try {
        await readerStore.loadChapter(mangaId.value, chapterId.value)
        resetControlsTimer()
      } catch (err) {
        error.value = `Error loading chapter: ${err.message}`
      } finally {
        loading.value = false
      }
    }

    const nextPage = () => {
      if (readerStore.readingMode === 'vertical') {
        const container = document.querySelector('.vertical-container')
        if (container) {
          container.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' })
        }
        return
      }
      
      const success = readerStore.nextPage()
      if (!success && hasNextChapter.value) {
        nextChapter()
      }
      resetControlsTimer()
    }

    const previousPage = () => {
      if (readerStore.readingMode === 'vertical') {
        const container = document.querySelector('.vertical-container')
        if (container) {
          container.scrollBy({ top: -window.innerHeight * 0.8, behavior: 'smooth' })
        }
        return
      }
      
      const success = readerStore.previousPage()
      if (!success && hasPreviousChapter.value) {
        previousChapter()
      }
      resetControlsTimer()
    }

    const nextChapter = () => {
      if (readerStore.navigation?.nextChapter) {
        const nextChapterId = readerStore.navigation.nextChapter.id
        
        router.push({
          name: 'MangaReader',
          params: { 
            mangaId: mangaId.value, 
            chapterId: nextChapterId 
          }
        })
      } else {
        showTemporaryMessage('📖 This is the last available chapter')
      }
    }

    const previousChapter = () => {
      if (readerStore.navigation?.previousChapter) {
        const prevChapterId = readerStore.navigation.previousChapter.id

        router.push({
          name: 'MangaReader',
          params: {
            mangaId: mangaId.value,
            chapterId: prevChapterId
          }
        })
      } else {
        showTemporaryMessage('📖 This is the first chapter')
      }
    }

    const showTemporaryMessage = (message) => {
      const messageEl = document.createElement('div')
      messageEl.className = 'temporary-message'
      messageEl.textContent = message
      messageEl.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        z-index: 9999;
        font-size: 1.1rem;
        border: 2px solid #4ecdc4;
        animation: fadeInOut 2s ease-in-out;
      `
      
      document.body.appendChild(messageEl)
      
      setTimeout(() => {
        if (document.body.contains(messageEl)) {
          document.body.removeChild(messageEl)
        }
      }, 2000)
    }

    const toggleControls = () => {
      readerStore.toggleControls()
      resetControlsTimer()
    }

    const toggleSettings = () => {
      readerStore.toggleSettings()
    }

    const closeSettings = () => {
      readerStore.showSettings = false
    }

    const resetControlsTimer = () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      
      if (!readerStore.hideControls) {
        controlsTimeout = setTimeout(() => {
          readerStore.hideControls = true
        }, 3000)
      }
    }

    const toggleFullscreen = async () => {
      try {
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen()
        } else {
          await document.exitFullscreen()
        }
        readerStore.toggleFullscreen()
      } catch (err) {
        console.error('Error toggling fullscreen:', err)
      }
    }

    const seekToPosition = (event) => {
      const rect = event.target.getBoundingClientRect()
      const x = event.clientX - rect.left
      const percentage = (x / rect.width) * 100
      
      readerStore.seekToProgress(percentage)
      resetControlsTimer()
    }

    const goBack = () => {
      router.push(`/manga/${mangaId.value}`)
    }

    const resetSettings = () => {
      readerStore.resetSettings()
    }

    const applySettings = () => {
      readerStore.saveSettings()
      readerStore.showSettings = false
    }

    const changeReadingMode = (mode) => {
      readerStore.setReadingMode(mode)
    }

    // Keyboard shortcuts
    const handleKeydown = (event) => {
      if (readerStore.showSettings) return
      
      switch (event.key) {
        case ' ':
        case 'ArrowRight':
          event.preventDefault()
          nextPage()
          break
        case 'Backspace':
        case 'ArrowLeft':
          event.preventDefault()
          previousPage()
          break
        case 'f':
        case 'F':
          event.preventDefault()
          toggleFullscreen()
          break
        case 'h':
        case 'H':
          event.preventDefault()
          toggleControls()
          break
        case 's':
        case 'S':
          event.preventDefault()
          toggleSettings()
          break
        case 'Escape':
          event.preventDefault()
          if (readerStore.showSettings) {
            closeSettings()
          }
          break
        case 'PageDown':
          event.preventDefault()
          nextChapter()
          break
        case 'PageUp':
          event.preventDefault()
          previousChapter()
          break
      }
    }

    // Lifecycle
    onMounted(() => {
      readerStore.loadSettings()

      const targetPage = route.query.page ? parseInt(route.query.page) - 1 : 0

      loadChapter().then(() => {
        if (targetPage > 0 && targetPage < readerStore.totalPages) {
          readerStore.setCurrentPage(targetPage)
        }
      })
      
      document.addEventListener('keydown', handleKeydown)
      document.addEventListener('fullscreenchange', () => {
        readerStore.isFullscreen = !!document.fullscreenElement
      })
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
    })

    // Watch route changes
    watch(() => route.params, (newParams, oldParams) => {
      if (newParams.chapterId !== oldParams?.chapterId) {
        loadChapter()
      }
    })

    return {
      readerStore,
      loading,
      error,
      progressPercentage,
      canGoPrevious,
      canGoNext,
      hasPreviousChapter,
      hasNextChapter,
      getPageImageUrl,
      handleImageError,
      handleImageLoad,
      loadChapter,
      nextPage,
      previousPage,
      nextChapter,
      previousChapter,
      toggleControls,
      toggleSettings,
      closeSettings,
      toggleFullscreen,
      seekToPosition,
      goBack,
      resetSettings,
      applySettings,
      changeReadingMode
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.manga-reader {
  position: relative;
  min-height: 100vh;
  background: #000;
  color: white;
  overflow: hidden;
  user-select: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.manga-reader.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
}

/* Theme Variations */
.manga-reader.theme-light {
  background: #fff;
}

.manga-reader.theme-sepia {
  background: #f4e5d3;
  color: #5d4037;
}

/* Loading & Error States */
.reader-loading, .reader-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #4ecdc4;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 500;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #44a08d;
}

/* Header Controls */
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.9);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  transition: transform 0.5s ease;
}

.reader-header.hidden {
  transform: translateY(-100%);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chapter-info h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.chapter-info p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.page-counter {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 500;
  color: white;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.control-btn.back-btn {
  background: white;
  color: black;
  font-weight: bold;
  font-size: 1.1rem;
}

/* Page Viewer */
.page-viewer {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

/* Single Page Mode */
.single-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}


/* Vertical Mode */
.vertical-container {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.vertical-pages {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.vertical-page-wrapper {
  margin-bottom: 10px;
}

/* Image Fitting */
.manga-page {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
  transition: all 0.3s ease;
}

.manga-page.fit-width {
  width: 100%;
  height: auto;
  max-height: 100vh;
}

.manga-page.fit-height {
  height: 100vh;
  width: auto;
  max-width: 100%;
}

.manga-page.fit-screen {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
}

.manga-page.fit-original {
  width: auto;
  height: auto;
  max-width: none;
  max-height: none;
}

/* Footer Controls */
.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.9);
  padding: 1rem 2rem;
  z-index: 100;
  transition: transform 0.3s ease;
}

.reader-footer.hidden {
  transform: translateY(100%);
}

.progress-bar {
  margin-bottom: 1rem;
}

.progress-track {
  position: relative;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: #4ecdc4;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-thumb {
  position: absolute;
  top: -3px;
  width: 12px;
  height: 12px;
  background: #4ecdc4;
  border-radius: 50%;
  transform: translateX(-50%);
  cursor: grab;
}

.footer-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.mode-select {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-weight: 500;
}

.mode-select option {
  background: #1e1e2e;
  color: white;
}

/* Settings Panel */
.settings-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  height: 100vh;
  background: rgba(30, 30, 46, 0.98);
  backdrop-filter: blur(15px);
  border-left: 2px solid #4ecdc4;
  z-index: 200;
  overflow-y: auto;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
}

.settings-content {
  padding: 2rem;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #4ecdc4;
}

.settings-header h3 {
  color: #fff;
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.close-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 2px solid #ff6b6b;
  color: #ff6b6b;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #ff6b6b;
  color: white;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #fff;
  font-size: 1rem;
}

.setting-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #4ecdc4;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.setting-select:focus {
  outline: none;
  border-color: #44a08d;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
}

.setting-select option {
  background: #1e1e2e;
  color: white;
  padding: 0.5rem;
}

.setting-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-btn, .secondary-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
}

.primary-btn {
  background-color:#3BAF41;
  color: white;
  border: none;
}

.secondary-btn {
  background-color: #E53935;
  color: white;
  border: none;
}

/* Scrollbar customization */
.vertical-container::-webkit-scrollbar {
  width: 8px;
}

.vertical-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.vertical-container::-webkit-scrollbar-thumb {
  background: #4ecdc4;
  border-radius: 4px;
}

.vertical-container::-webkit-scrollbar-thumb:hover {
  background: #44a08d;
}

/* Responsive */
@media (max-width: 768px) {
  .reader-header, .reader-footer {
    padding: 1rem;
  }
  
  .header-left, .header-right {
    gap: 0.5rem;
  }
  
  .footer-controls {
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  
  .settings-panel {
    width: 100%;
  }
  
  .control-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .manga-page.fit-width {
    max-width: 95vw;
  }
}

@media (max-width: 480px) {
  .settings-content {
    padding: 1rem;
  }
  
  .footer-controls {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .chapter-info h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
  20% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
}

.reader-content {
  animation: fadeIn 0.3s ease-in;
}

.settings-panel {
  animation: slideUp 0.3s ease-out;
}

/* Hover effects */
.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.setting-select:hover {
  border-color: #44a08d;
}

.mode-select:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Loading animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.reader-loading p {
  animation: pulse 2s infinite;
}

/* Temporary Message */
.temporary-message {
  animation: fadeInOut 2s ease-in-out;
}
</style>