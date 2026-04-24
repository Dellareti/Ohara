<template>
  <div class="manga-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading manga details...</p>
    </div>

    <ErrorState
      v-if="error"
      :message="error"
      title="Error Loading Manga"
      severity="high"
      :retryable="true"
      :on-retry="loadManga"
    />

    <!-- Manga Content - Two Column Layout (35/65) -->
    <div v-if="manga && !loading" class="manga-layout">
      <!-- Left Panel - Manga Details (35%) -->
      <div class="manga-details-panel">
        <div class="manga-cover-section">
          <div class="cover-container">
            <img 
              v-if="manga.thumbnail" 
              :src="manga.thumbnail" 
              :alt="manga.title"
              class="cover-image"
            />
            <div v-else class="cover-placeholder">📚</div>
          </div>
          
          <h1 class="manga-title">{{ manga.title }}</h1>

          <!-- Quick Action - Continue Reading -->
          <button @click="continueReading" class="continue-reading-btn">
            Continue Reading
          </button>
        </div>

        <!-- Manga Information -->
        <div class="manga-info-section">

          <!-- Status -->
          <div v-if="manga.status" class="status-section">
            <span class="status-label">Status:</span>
            <span class="status-value" :class="statusClass">{{ manga.status }}</span>
          </div>

          <!-- Genres -->
          <div v-if="manga.genres && manga.genres.length" class="genres-section">
            <span class="genres-label">Genres:</span>
            <div class="genres-list">
              <span v-for="genre in manga.genres" :key="genre" class="genre-tag">
                {{ genre }}
              </span>
            </div>
          </div>

          <!-- Statistics -->
          <div class="stats-section">
            <div class="stat-item">
              <div class="stat-value">{{ manga.chapter_count }}</div>
              <div class="stat-label">Chapters</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ manga.total_pages }}</div>
              <div class="stat-label">Pages</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ readProgress }}%</div>
              <div class="stat-label">Progress</div>
            </div>
          </div>

          <!-- Description -->
          <div v-if="manga.description" class="description-section">
            <h3>Description</h3>
            <p class="description-text">{{ manga.description }}</p>
          </div>
        </div>
      </div>

      <!-- Right Panel - Chapters List (65%) -->
      <div class="chapters-panel">
        <!-- Chapters Header -->
        <div class="chapters-header">
          <h2>Chapters ({{ manga.chapter_count }})</h2>

          <!-- Filter Controls -->
          <div class="filter-controls">
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search chapter..."
              class="search-input"
            />

            <!-- Refresh Button -->
            <button @click="refreshChapters" class="refresh-btn" title="Refresh chapters">
              Refresh chapters
            </button>

            <select v-model="sortOrder" class="sort-select">
              <option value="desc">Newest First</option>
              <option value="asc">Oldest First</option>
            </select>
          </div>
        </div>

        <!-- Chapters List -->
        <div class="chapters-list">
          <div 
            v-for="chapter in filteredChapters" 
            :key="chapter.id"
            class="chapter-row"
            @click="openChapter(chapter)"
            :class="{
              'read': chapter.isRead,
              'current': chapter.id === currentChapterId,
              'selected': selectedChapters.includes(chapter.id)
            }"
          >
            <!-- Selection Checkbox -->
            <div class="chapter-selection" @click.stop>
              <input 
                type="checkbox" 
                :checked="selectedChapters.includes(chapter.id)"
                @change="toggleChapterSelection(chapter.id)"
                class="selection-checkbox"
              />
            </div>

            <!-- Chapter Number/Title -->
            <div class="chapter-main-info">
              <div class="chapter-title">{{ chapter.name }}</div>
              <div class="chapter-meta">
                <span v-if="chapter.number" class="chapter-number">
                Chapter {{ chapter.number }}
                </span>
                <span v-if="chapter.volume" class="volume-number">
                  Vol. {{ chapter.volume }}
                </span>
                <span class="page-count">{{ chapter.page_count }} pages</span>
                <span v-if="chapter.date_added" class="date-added">
                  {{ formatDate(chapter.date_added) }}
                </span>
              </div>
            </div>

            <!-- Reading Progress -->
            <div class="chapter-progress">
              <div v-if="chapter.readProgress > 0" class="progress-indicator">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: chapter.readProgress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ chapter.readProgress.toFixed(2) }}%</span>
              </div>
              <div v-if="chapter.isRead" class="read-indicator">✓</div>
            </div>

            <!-- Chapter Menu -->
            <div class="chapter-menu">
              <button 
                @click.stop="showChapterMenu($event, chapter)" 
                class="menu-btn"
                :class="{ 'active': activeMenuChapter === chapter.id }"
              >
                ⋮
              </button>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMoreChapters" class="load-more-section" style="display: none;">
          <button @click="loadMoreChapters" class="load-more-btn">
            Load More Chapters
          </button>
        </div>
      </div>
    </div>

    <!-- Chapter Context Menu -->
    <div 
      v-if="contextMenu.visible" 
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="context-menu-content">
        <button @click="selectChapter" class="menu-option">
          Select
        </button>
        <button @click="selectAllChapters" class="menu-option">
          Select All
        </button>
        <hr class="menu-divider" />
        <button @click="markAsRead" class="menu-option">
          {{ contextMenu.chapter?.isRead ? 'Mark as Unread' : 'Mark as Read' }}
        </button>
        <button @click="markAsUnread" class="menu-option">
          Mark as Unread
        </button>
        <button @click="markPreviousAsRead" class="menu-option">
          Mark Previous as Read
        </button>
      </div>
    </div>

    <!-- Overlay for closing menus -->
    <div 
      v-if="contextMenu.visible" 
      class="menu-overlay"
      @click="closeAllMenus"
    ></div>

    <!-- Selection Actions Bar (appears when chapters are selected) -->
    <div v-if="selectedChapters.length > 0" class="selection-actions-bar">
      <div class="selection-info">
        {{ selectedChapters.length }} chapters selected
      </div>
      <div class="selection-actions">
        <button @click="markSelectedAsRead" class="action-btn read-btn">
          Mark as Read
        </button>
        <button @click="markSelectedAsUnread" class="action-btn unread-btn">
          Mark as Unread
        </button>
        <button @click="clearSelection" class="action-btn cancel-btn">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import ErrorState from '@/components/ErrorState.vue'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'MangaDetailView',
  components: {
    ErrorState
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const libraryStore = useLibraryStore()
    const { showInfo } = useToast()

    // Reactive data
    const manga = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const sortOrder = ref('desc')
    const searchTerm = ref('')
    const currentChapterId = ref(null)
    const chapterLimit = ref(50)
    const activeMenuChapter = ref(null)
    const selectedChapters = ref([])
    const showBulkMenu = ref(false)

    // Context menu
    const contextMenu = ref({
      visible: false,
      x: 0,
      y: 0,
      chapter: null
    })

    // Computed
    const mangaId = computed(() => route.params.id)
    
    const statusClass = computed(() => {
      if (!manga.value?.status) return ''
      return {
        'status-ongoing': manga.value.status.toLowerCase().includes('ongoing'),
        'status-completed': manga.value.status.toLowerCase().includes('completed'),
        'status-hiatus': manga.value.status.toLowerCase().includes('hiatus')
      }
    })

    const readProgress = computed(() => {
      if (!manga.value?.chapters) return 0
      const readChapters = manga.value.chapters.filter(ch => ch.isRead).length
      return Number(((readChapters / manga.value.chapters.length) * 100).toFixed(2))
    })

    const filteredChapters = computed(() => {
      if (!manga.value?.chapters) return []

      let chapters = [...manga.value.chapters]

      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        chapters = chapters.filter(ch =>
          ch.name.toLowerCase().includes(term) ||
          ch.number?.toString().includes(term)
        )
      }

      chapters.sort((a, b) => {
        const aNum = a.number || 0
        const bNum = b.number || 0
        return sortOrder.value === 'desc' ? bNum - aNum : aNum - bNum
      })

      return chapters
    })

    const hasMoreChapters = computed(() => {
      return false
    })

    // Methods
    const loadManga = async () => {
      loading.value = true
      error.value = null
      
      try {
        const mangaData = await libraryStore.fetchManga(mangaId.value)

        manga.value = {
          ...mangaData,
          chapters: mangaData.chapters?.map(chapter => ({
            ...chapter,
            isRead: false,
            readProgress: 0,
            thumbnail: chapter.pages?.[0]?.path 
              ? `http://localhost:8000${chapter.pages[0].path}` 
              : null
          })) || []
        }
        
        loadReadingProgress()
        
      } catch (err) {
        error.value = err.message || 'Error loading manga'
        console.error('Error loading manga:', err)
      } finally {
        loading.value = false
      }
    }

    const refreshChapters = async () => {
      await loadManga()
    }

    const loadReadingProgress = () => {
      const savedProgress = localStorage.getItem(`ohara_progress_${mangaId.value}`)
      if (savedProgress) {
        const progress = JSON.parse(savedProgress)
        currentChapterId.value = progress.currentChapterId
        
        if (manga.value?.chapters) {
          manga.value.chapters.forEach(chapter => {
            const chapterProgress = progress.chapters?.[chapter.id]
            if (chapterProgress !== undefined) {
              chapter.isRead = chapterProgress.isRead
              chapter.readProgress = Number(Number(chapterProgress.progress).toFixed(2))
            } else {
              chapter.isRead = false
              chapter.readProgress = 0.00
            }
          })
        }
      }
    }

    const continueReading = () => {
      if (!manga.value?.chapters || manga.value.chapters.length === 0) {
        showError('No chapters available')
        return
      }

      const extractNumber = (id) => {
        const match = id.match(/ch-(\d+(?:\.\d+)?)/)
        return match ? parseFloat(match[1]) : 0
      }

      const sortedChapters = [...manga.value.chapters].sort((a, b) => {
        const numA = extractNumber(a.id)
        const numB = extractNumber(b.id)
        return numA - numB
      })

      const savedProgress = localStorage.getItem(`ohara_progress_${mangaId.value}`)
      let targetChapter = null
      let targetPage = 1

      if (savedProgress) {
        const progress = JSON.parse(savedProgress)
        
        for (const chapter of sortedChapters) {
          const chapterProgress = progress.chapters?.[chapter.id]
          if (chapterProgress && chapterProgress.progress > 0 && !chapterProgress.isRead) {
            targetChapter = chapter
            targetPage = chapterProgress.currentPage || 1
            break
          }
        }

        if (!targetChapter) {
          for (const chapter of sortedChapters) {
            const chapterProgress = progress.chapters?.[chapter.id]
            if (!chapterProgress || !chapterProgress.isRead) {
              targetChapter = chapter
              targetPage = 1
              break
            }
          }
        }

        if (!targetChapter) {
          targetChapter = sortedChapters[sortedChapters.length - 1]
          targetPage = 1
        }
      } else {
        targetChapter = sortedChapters[0]
        targetPage = 1
      }

      currentChapterId.value = targetChapter.id
      saveReadingProgress()
      
      router.push({
        name: 'MangaReader',
        params: {
          mangaId: mangaId.value,
          chapterId: targetChapter.id
        },
        query: {
          page: targetPage
        }
      })
    }

    const openChapter = (chapter) => {
      currentChapterId.value = chapter.id
      saveReadingProgress()
      
      router.push({
        name: 'MangaReader',
        params: {
          mangaId: mangaId.value,
          chapterId: chapter.id
        }
      })
    }

    // Selection methods
    const toggleChapterSelection = (chapterId) => {
      const index = selectedChapters.value.indexOf(chapterId)
      if (index > -1) {
        selectedChapters.value.splice(index, 1)
      } else {
        selectedChapters.value.push(chapterId)
      }
    }

    const selectAllChapters = () => {
      if (!manga.value?.chapters) return

      selectedChapters.value = manga.value.chapters.map(ch => ch.id)
      closeAllMenus()
    }

    const clearSelection = () => {
      selectedChapters.value = []
    }

    // Bulk actions
    const markAllAsRead = () => {
      if (!manga.value?.chapters) return
      
      manga.value.chapters.forEach(chapter => {
        chapter.isRead = true
        chapter.readProgress = 100
      })
      
      saveReadingProgress()
      closeAllMenus()
    }

    const markAllAsUnread = () => {
      if (!manga.value?.chapters) return
      
      manga.value.chapters.forEach(chapter => {
        chapter.isRead = false
        chapter.readProgress = 0.00
      })
      
      saveReadingProgress()
      closeAllMenus()
    }

    const markSelectedAsRead = () => {
      if (!manga.value?.chapters) return
      
      selectedChapters.value.forEach(chapterId => {
        const chapter = manga.value.chapters.find(ch => ch.id === chapterId)
        if (chapter) {
          chapter.isRead = true
          chapter.readProgress = 100
        }
      })
      
      saveReadingProgress()
      clearSelection()
    }

    const markSelectedAsUnread = () => {
      if (!manga.value?.chapters) return
      
      selectedChapters.value.forEach(chapterId => {
        const chapter = manga.value.chapters.find(ch => ch.id === chapterId)
        if (chapter) {
          chapter.isRead = false
          chapter.readProgress = 0.00
        }
      })
      
      saveReadingProgress()
      clearSelection()
    }

    // Menu methods
    const showChapterMenu = (event, chapter) => {
      event.preventDefault()
      event.stopPropagation()
      
      const rect = event.target.getBoundingClientRect()
      
      contextMenu.value = {
        visible: true,
        x: rect.left - 200,
        y: rect.bottom + 5,
        chapter: chapter
      }
      
      activeMenuChapter.value = chapter.id
      showBulkMenu.value = false
    }

    const closeAllMenus = () => {
      contextMenu.value.visible = false
      showBulkMenu.value = false
      activeMenuChapter.value = null
    }

    const selectChapter = () => {
      const chapterId = contextMenu.value.chapter?.id
      if (chapterId) {
        toggleChapterSelection(chapterId)
      }
      closeAllMenus()
    }

    const markAsRead = () => {
      const chapter = contextMenu.value.chapter
      if (chapter) {
        chapter.isRead = !chapter.isRead
        chapter.readProgress = chapter.isRead ? 100.00 : 0.00
        saveReadingProgress()
      }
      closeAllMenus()
    }

    const markAsUnread = () => {
      const chapter = contextMenu.value.chapter
      if (chapter) {
        chapter.isRead = false
        chapter.readProgress = 0.00
        saveReadingProgress()
      }
      closeAllMenus()
    }

    const markPreviousAsRead = () => {
      const chapter = contextMenu.value.chapter
      if (!chapter || !manga.value?.chapters) return
      
      const chapterIndex = manga.value.chapters.findIndex(ch => ch.id === chapter.id)
      if (chapterIndex === -1) return

      for (let i = chapterIndex + 1; i < manga.value.chapters.length; i++) {
        manga.value.chapters[i].isRead = true
        manga.value.chapters[i].readProgress = 100.00
      }
      
      saveReadingProgress()
      closeAllMenus()
    }

    const loadMoreChapters = () => {
      chapterLimit.value += 50
    }

    const saveReadingProgress = () => {
      if (!manga.value) return
      
      const progress = {
        currentChapterId: currentChapterId.value,
        lastReadAt: new Date().toISOString(),
        chapters: {}
      }
      
      manga.value.chapters.forEach(chapter => {
        progress.chapters[chapter.id] = {
          isRead: chapter.isRead,
          progress: chapter.readProgress
        }
      })
      
      localStorage.setItem(`ohara_progress_${mangaId.value}`, JSON.stringify(progress))
    }

    const formatDate = (dateString) => {
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        })
      } catch {
        return ''
      }
    }

    // Event listeners
    const handleClickOutside = (event) => {
      if (contextMenu.value.visible && !event.target.closest('.context-menu')) {
        closeAllMenus()
      }
    }

    // Lifecycle
    onMounted(() => {
      loadManga()
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    watch(() => route.params.id, () => {
      if (route.params.id) {
        loadManga()
        clearSelection()
      }
    })

    return {
      manga,
      loading,
      error,
      sortOrder,
      searchTerm,
      currentChapterId,
      activeMenuChapter,
      contextMenu,
      selectedChapters,
      showBulkMenu,
      statusClass,
      readProgress,
      filteredChapters,
      hasMoreChapters,
      loadManga,
      refreshChapters,
      continueReading,
      openChapter,
      toggleChapterSelection,
      selectAllChapters,
      clearSelection,
      markAllAsRead,
      markAllAsUnread,
      markSelectedAsRead,
      markSelectedAsUnread,
      showChapterMenu,
      closeAllMenus,
      selectChapter,
      markAsRead,
      markAsUnread,
      markPreviousAsRead,
      loadMoreChapters,
      formatDate
    }
  }
}
</script>

<style scoped>
.manga-detail {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
}

/* Loading & Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
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
}

/* Main Layout - 35/65 Split */
.manga-layout {
  display: grid;
  grid-template-columns: 35fr 65fr;
  height: 100vh;
  overflow: hidden;
  gap: 0;
}

/* Left Panel - Manga Details (35%) */
.manga-details-panel {
  background: rgba(0, 0, 0, 0.15);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.manga-cover-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.cover-container {
  width: 280px;
  height: 390px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
}

.cover-container:hover {
  transform: translateY(-2px);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.continue-reading-btn {
  width: 100%;
  max-width: 280px;
  padding: 0.75rem 1rem;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  box-shadow: 0 3px 12px rgba(78, 205, 196, 0.3);
}

.continue-reading-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(78, 205, 196, 0.4);
}

.manga-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manga-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: white;
  line-height: 1.3;
  margin: 0;
  text-align: center;
}

.creator-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.creator-label, .status-label, .genres-label {
  font-weight: 600;
  color: #4ecdc4;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.creator-name, .status-value {
  font-weight: 500;
  color: white;
  text-align: right;
  font-size: 0.9rem;
}

.status-ongoing { color: #4CAF50; }
.status-completed { color: #2196F3; }
.status-hiatus { color: #FF9800; }

.genres-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.genre-tag {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  padding: 0.2rem 0.4rem;
  border-radius: 8px;
  font-size: 0.7rem;
  border: 1px solid rgba(78, 205, 196, 0.3);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 12px;
  margin: 0.75rem 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-item {
  text-align: center;
  padding: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4ecdc4;
  display: block;
  margin-bottom: 0.2rem;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.9;
  font-weight: 500;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.description-section h3 {
  color: #4ecdc4;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.description-text {
  line-height: 1.4;
  opacity: 0.9;
  margin: 0;
  font-size: 0.85rem;
}

/* Right Panel - Chapters (65%) */
.chapters-panel {
  background: rgba(255, 255, 255, 0.01);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chapters-header {
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.1);
}

.chapters-header h2 {
  color: white;
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input, .sort-select {
  padding: 0.6rem 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  color: white;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.search-input:focus, .sort-select:focus {
  border-color: #4ecdc4;
  background: rgba(0, 0, 0, 0.3);
  outline: none;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Refresh Button */
.refresh-btn {
  background: rgba(78, 205, 196, 0.1);
  border: 1px solid rgba(78, 205, 196, 0.3);
  color: #4ecdc4;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 1rem;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  background: rgba(78, 205, 196, 0.2);
}

/* Menu Divider */
.menu-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 0.25rem 0;
}

/* Bulk Actions - Removed from filter controls */

.menu-icon {
  font-size: 1rem;
  min-width: 18px;
}

/* Chapters List */
.chapters-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0;
}

.chapter-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  min-height: 70px;
  margin-bottom: 0.3rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.chapter-row:hover {
  background: rgba(255, 255, 255, 0.08);
  border-left: 3px solid rgba(78, 205, 196, 0.5);
}

.chapter-row.read {
  opacity: 0.5;
}

.chapter-row.current {
  background: rgba(78, 205, 196, 0.1);
  border-left: 4px solid #4ecdc4;
  box-shadow: inset 4px 0 0 #4ecdc4;
}

.chapter-row.selected {
  background: rgba(78, 205, 196, 0.15);
  border-left: 4px solid #4ecdc4;
}

/* Selection Checkbox */
.chapter-selection {
  display: flex;
  align-items: center;
  margin-right: 0.5rem;
}

.selection-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #4ecdc4;
  cursor: pointer;
}

.chapter-main-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.chapter-title {
  font-weight: 600;
  color: white;
  font-size: 1.1rem;
  line-height: 1.3;
  margin: 0;
}

.chapter-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.8rem;
  opacity: 0.7;
  flex-wrap: wrap;
}

.chapter-meta span {
  background: rgba(255, 255, 255, 0.08);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.chapter-progress {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-width: 80px;
  justify-content: flex-end;
}

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.progress-bar {
  width: 50px;
  height: 3px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ecdc4, #44a08d);
  transition: width 0.3s ease;
  border-radius: 2px;
}

.progress-text {
  font-size: 0.7rem;
  color: #4ecdc4;
  min-width: 30px;
  font-weight: 600;
}

.read-indicator {
  color: #4CAF50;
  font-size: 1rem;
  font-weight: bold;
}

.chapter-menu {
  display: flex;
  align-items: center;
  margin-left: 0.5rem;
}

.menu-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 0.6rem;
  border-radius: 6px;
  font-size: 1.2rem;
  line-height: 1;
  transition: all 0.2s;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-btn:hover, .menu-btn.active {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  transform: scale(1.05);
}

/* Context Menu */
.context-menu {
  position: fixed;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.5rem 0;
  min-width: 220px;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.context-menu-content {
  display: flex;
  flex-direction: column;
}

.menu-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
  font-size: 0.9rem;
}

.menu-option:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

/* Selection Actions Bar */
.selection-actions-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  backdrop-filter: blur(10px);
  z-index: 50;
}

.selection-info {
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
}

.selection-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.90rem;
  font-weight: 500;
  transition: all 0.2s;
}

.read-btn {
  background: #3BAF41;;
  color: white;
}

.unread-btn {
  background: #D98E04;
  color: white;
}

.cancel-btn {
  background: #E53935;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

/* Load More */
.load-more-section {
  padding: 1rem 1.5rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.load-more-btn {
  background: rgba(78, 205, 196, 0.1);
  border: 1px solid rgba(78, 205, 196, 0.3);
  color: #4ecdc4;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover {
  background: rgba(78, 205, 196, 0.2);
}

/* Responsive */
@media (max-width: 1200px) {
  .manga-layout {
    grid-template-columns: 32fr 68fr;
  }
  
  .manga-details-panel {
    padding: 1.25rem;
  }
  
  .cover-container {
    width: 250px;
    height: 350px;
  }
}

@media (max-width: 1024px) {
  .manga-layout {
    grid-template-columns: 30fr 70fr;
  }
  
  .manga-details-panel {
    padding: 1rem;
  }
  
  .cover-container {
    width: 220px;
    height: 310px;
  }
  
  .manga-title {
    font-size: 1.2rem;
  }
}

@media (max-width: 768px) {
  .manga-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    height: auto;
  }
  
  .manga-details-panel {
    padding: 1rem;
    height: auto;
    overflow: visible;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .manga-cover-section {
    flex-direction: row;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .cover-container {
    width: 100px;
    height: 140px;
    flex-shrink: 0;
  }
  
  .continue-reading-btn {
    width: auto;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }
  
  .manga-info-section {
    flex: 1;
  }
  
  .manga-title {
    font-size: 1.1rem;
    text-align: left;
  }
  
  .stats-section {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    padding: 0.75rem;
    margin: 0.5rem 0;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
  
  .chapters-panel {
    height: calc(100vh - 280px);
    min-height: 400px;
  }
  
  .chapters-header {
    padding: 1rem;
  }
  
  .filter-controls {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .search-input {
    min-width: auto;
    width: 100%;
    order: 1;
  }
  
  .refresh-btn, .sort-select, .bulk-menu-btn {
    order: 2;
  }
  
  .chapter-row {
    padding: 0.75rem 1rem;
    min-height: 60px;
  }
  
  .chapter-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .context-menu, .bulk-menu {
    min-width: 180px;
  }
  
  .selection-actions-bar {
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .selection-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .manga-details-panel {
    padding: 0.75rem;
  }
  
  .manga-cover-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .cover-container {
    width: 90px;
    height: 125px;
  }
  
  .manga-title {
    font-size: 1rem;
    text-align: center;
  }
  
  .stats-section {
    padding: 0.5rem;
  }
  
  .stat-value {
    font-size: 1rem;
  }
  
  .chapters-header h2 {
    font-size: 1.1rem;
  }
  
  .chapter-title {
    font-size: 0.85rem;
  }
  
  .chapter-meta {
    font-size: 0.7rem;
  }
  
  .filter-controls {
    gap: 0.4rem;
  }
  
  .refresh-btn, .bulk-menu-btn {
    padding: 0.5rem 0.6rem;
    min-width: 36px;
  }
}

/* Scrollbar Customization */
.manga-details-panel::-webkit-scrollbar,
.chapters-list::-webkit-scrollbar {
  width: 6px;
}

.manga-details-panel::-webkit-scrollbar-track,
.chapters-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.manga-details-panel::-webkit-scrollbar-thumb,
.chapters-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.manga-details-panel::-webkit-scrollbar-thumb:hover,
.chapters-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.context-menu, .bulk-menu {
  animation: fadeIn 0.2s ease-out;
}

.chapter-row {
  animation: fadeIn 0.3s ease-out;
}

.selection-actions-bar {
  animation: fadeIn 0.3s ease-out;
}

/* Focus States for Accessibility */
.continue-reading-btn:focus,
.search-input:focus,
.sort-select:focus,
.refresh-btn:focus,
.bulk-menu-btn:focus,
.menu-btn:focus,
.menu-option:focus,
.bulk-option:focus,
.action-btn:focus,
.load-more-btn:focus,
.selection-checkbox:focus {
  outline: 2px solid #4ecdc4;
  outline-offset: 2px;
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
  .manga-details-panel,
  .chapters-panel {
    background: black;
    border-color: white;
  }
  
  .chapter-row:hover {
    background: rgba(255, 255, 255, 0.2);
  }
  
  .context-menu, .bulk-menu {
    background: black;
    border-color: white;
  }
  
  .selection-actions-bar {
    background: black;
    border-color: white;
  }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  .continue-reading-btn,
  .chapter-row,
  .menu-btn,
  .refresh-btn,
  .action-btn {
    transition: none;
  }
  
  .context-menu,
  .selection-actions-bar {
    animation: none;
  }
  
  .progress-fill {
    transition: none;
  }
}
</style>