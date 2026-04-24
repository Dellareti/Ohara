<template>
  <div class="library-simple">
    <!-- Header with navigation -->
    <div class="header">
      <h1>Library</h1>
      <div class="header-actions">
        <!-- Sort selector -->
        <select v-model="sortOption" class="sort-select" title="Sort by">
          <option value="alphabetical">A-Z (Default)</option>
          <option value="alphabetical-reverse">Z-A</option>
          <option value="most-read">Most Read</option>
          <option value="least-read">Least Read</option>
          <option value="chapters-desc">Most Chapters</option>
          <option value="chapters-asc">Fewest Chapters</option>
          <option value="date-added">Recently Added</option>
          <option value="date-modified">Recently Updated</option>
        </select>
        <router-link to="/setup" class="setup-btn">Setup</router-link>
        <button @click="refreshLibrary" class="refresh-btn">Refresh</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="libraryStore.loading" class="loading-section">
      <div class="spinner"></div>
      <p>Loading library...</p>
    </div>

    <ErrorState
      v-if="libraryStore.error"
      :message="libraryStore.error"
      title="Error Loading Library"
      severity="high"
      :retryable="true"
      :on-retry="loadLibrary"
      compact
    />

    <!-- Empty library -->
    <div v-if="!libraryStore.loading && !libraryStore.error && libraryStore.mangas.length === 0" class="empty-library">
      <div class="empty-icon">📚</div>
      <h2>Empty Library</h2>
      <p>Configure your library to start reading</p>
      <router-link to="/setup" class="setup-link">Configure Now</router-link>
    </div>

    <!-- Manga Grid (using paginatedMangas) -->
    <div v-if="!libraryStore.loading && !libraryStore.error && sortedMangas.length > 0" :class="['manga-grid', cardSizeClass]">
      <div 
        v-for="manga in paginatedMangas" 
        :key="manga.id"
        class="manga-card"
        @click="selectManga(manga)"
      >
        <div class="manga-thumbnail">
          <img 
            v-if="manga.thumbnail" 
            :src="getThumbnailUrl(manga.thumbnail)"
            :alt="manga.title"
            @error="onImageError"
          />
          <div v-else class="placeholder-thumbnail">
            📖
          </div>
        </div>
        
        <div class="manga-info">
          <h3>{{ manga.title }}</h3>
          <div class="manga-meta">
            <span class="chapter-count">{{ manga.chapter_count || 0 }} chapters</span>
            <span v-if="manga.author" class="author">{{ manga.author }}</span>
            <span v-if="manga.status" class="status" :class="manga.status.toLowerCase()">
              {{ manga.status }}
            </span>
          </div>
          <div v-if="manga.genres && manga.genres.length" class="genres">
            <span v-for="genre in manga.genres.slice(0, 3)" :key="genre" class="genre">
              {{ genre }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="!libraryStore.loading && !libraryStore.error && totalPages > 1" class="pagination">
      <button @click="prevPage" :disabled="currentPage <= 1" class="page-btn">« Previous</button>
      
      <div class="page-numbers">
        <button 
          v-for="page in Math.min(5, totalPages)" 
          :key="page"
          @click="goToPage(page)"
          :class="['page-number', { active: currentPage === page }]"
        >
          {{ page }}
        </button>
        <span v-if="totalPages > 5" class="page-ellipsis">...</span>
        <button 
          v-if="totalPages > 5"
          @click="goToPage(totalPages)"
          :class="['page-number', { active: currentPage === totalPages }]"
        >
          {{ totalPages }}
        </button>
      </div>
      
      <button @click="nextPage" :disabled="currentPage >= totalPages" class="page-btn">Next »</button>

      <div class="page-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ sortedMangas.length }} manga)
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ErrorState from '@/components/ErrorState.vue'
import { useLibraryStore } from '@/store/library'
import { useSettingsStore } from '@/store/settings'

export default {
  name: 'LibraryViewSimple',
  components: {
    ErrorState
  },
  setup() {
    const router = useRouter()
    const libraryStore = useLibraryStore()
    const settingsStore = useSettingsStore()
    const sortOption = ref('alphabetical')
    const currentPage = ref(1)

    const naturalSort = (a, b) => {
      const aTitle = a.title.toLowerCase()
      const bTitle = b.title.toLowerCase()

      const aParts = aTitle.match(/(\d+|\D+)/g) || []
      const bParts = bTitle.match(/(\d+|\D+)/g) || []

      const maxLength = Math.max(aParts.length, bParts.length)

      for (let i = 0; i < maxLength; i++) {
        const aPart = aParts[i] || ''
        const bPart = bParts[i] || ''

        if (!isNaN(aPart) && !isNaN(bPart)) {
          const diff = parseInt(aPart) - parseInt(bPart)
          if (diff !== 0) return diff
        }
        else if (!isNaN(aPart) && isNaN(bPart)) {
          return -1
        }
        else if (isNaN(aPart) && !isNaN(bPart)) {
          return 1
        }
        else {
          const diff = aPart.localeCompare(bPart)
          if (diff !== 0) return diff
        }
      }

      return 0
    }

    const sortedMangas = computed(() => {
      const mangas = [...libraryStore.mangas]

      switch (sortOption.value) {
        case 'alphabetical':
          return mangas.sort(naturalSort)

        case 'alphabetical-reverse':
          return mangas.sort((a, b) => -naturalSort(a, b))

        case 'most-read':
          return mangas.sort((a, b) => {
            const aProgress = a.reading_progress?.chapters_read || 0
            const bProgress = b.reading_progress?.chapters_read || 0
            if (aProgress !== bProgress) {
              return bProgress - aProgress
            }
            const aPages = a.reading_progress?.pages_read || 0
            const bPages = b.reading_progress?.pages_read || 0
            if (aPages !== bPages) {
              return bPages - aPages
            }
            return naturalSort(a, b)
          })

        case 'least-read':
          return mangas.sort((a, b) => {
            const aProgress = a.reading_progress?.chapters_read || 0
            const bProgress = b.reading_progress?.chapters_read || 0
            if (aProgress !== bProgress) {
              return aProgress - bProgress
            }
            const aPages = a.reading_progress?.pages_read || 0
            const bPages = b.reading_progress?.pages_read || 0
            if (aPages !== bPages) {
              return aPages - bPages
            }
            return naturalSort(a, b)
          })

        case 'chapters-desc':
          return mangas.sort((a, b) => {
            const diff = (b.chapter_count || 0) - (a.chapter_count || 0)
            return diff !== 0 ? diff : naturalSort(a, b)
          })

        case 'chapters-asc':
          return mangas.sort((a, b) => {
            const diff = (a.chapter_count || 0) - (b.chapter_count || 0)
            return diff !== 0 ? diff : naturalSort(a, b)
          })

        case 'date-added':
          return mangas.sort((a, b) => {
            const dateA = new Date(a.date_added || 0)
            const dateB = new Date(b.date_added || 0)
            const diff = dateB - dateA
            return diff !== 0 ? diff : naturalSort(a, b)
          })

        case 'date-modified':
          return mangas.sort((a, b) => {
            const dateA = new Date(a.date_modified || 0)
            const dateB = new Date(b.date_modified || 0)
            const diff = dateB - dateA
            return diff !== 0 ? diff : naturalSort(a, b)
          })

        default:
          return mangas.sort(naturalSort)
      }
    })

    const totalMangaPages = computed(() => {
      return sortedMangas.value.reduce((sum, manga) => sum + (manga.total_pages || 0), 0)
    })

    const totalChapters = computed(() => {
      return sortedMangas.value.reduce((sum, manga) => sum + (manga.chapter_count || 0), 0)
    })

    const paginatedMangas = computed(() => {
      const itemsPerPage = settingsStore.interface.itemsPerPage
      const startIndex = (currentPage.value - 1) * itemsPerPage
      const endIndex = startIndex + itemsPerPage
      return sortedMangas.value.slice(startIndex, endIndex)
    })

    const totalPages = computed(() => {
      return Math.ceil(sortedMangas.value.length / settingsStore.interface.itemsPerPage)
    })

    const cardSizeClass = computed(() => {
      return `card-size-${settingsStore.interface.cardSize}`
    })

    const loadLibrary = async () => {
      try {
        await libraryStore.fetchLibrary()
      } catch (error) {
        console.error('Error loading library:', error)
      }
    }

    const refreshLibrary = async () => {
      if (libraryStore.libraryPath) {
        try {
          await libraryStore.scanLibrary()
        } catch (error) {
          console.error('Error refreshing library:', error)
        }
      } else {
        await loadLibrary()
      }
    }

    const selectManga = (manga) => {
      
      router.push({
        name: 'MangaDetail',
        params: { id: manga.id }
      })
    }

    const getThumbnailUrl = (thumbnailPath) => {
      if (!thumbnailPath) return null
      
      if (thumbnailPath.startsWith('/')) {
        return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/image?path=${encodeURIComponent(thumbnailPath)}`
      }
      
      return thumbnailPath
    }

    const onImageError = (event) => {
      event.target.style.display = 'none'
      event.target.parentElement.innerHTML = '<div class="placeholder-thumbnail">📖</div>'
    }

    const formatPages = (pages) => {
      if (pages > 1000) {
        return (pages / 1000).toFixed(1) + 'k'
      }
      return pages.toString()
    }

    const saveSortPreference = () => {
      localStorage.setItem('manga-library-sort', sortOption.value)
    }

    const loadSortPreference = () => {
      const saved = localStorage.getItem('manga-library-sort')
      if (saved) {
        sortOption.value = saved
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    watch(sortOption, () => {
      currentPage.value = 1
    })

    watch(sortOption, () => {
      saveSortPreference()
    })

    onMounted(async () => {
      loadSortPreference()
      settingsStore.loadSettings()
      libraryStore.loadLibraryConfig()

      if (!libraryStore.isInitialized || libraryStore.mangas.length === 0) {
        if (libraryStore.libraryPath) {
          await refreshLibrary()
        } else {
          await loadLibrary()
        }
      }
    })

    return {
      libraryStore,
      settingsStore,
      sortOption,
      sortedMangas,
      paginatedMangas,
      totalPages,
      totalChapters,
      currentPage,
      cardSizeClass,
      loadLibrary,
      refreshLibrary,
      selectManga,
      getThumbnailUrl,
      onImageError,
      formatPages,
      nextPage,
      prevPage,
      goToPage
    }
  }
}
</script>

<style scoped>
.library-simple {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 2.5rem;
  margin: 0;
  background:#fff;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.sort-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}

.sort-select option {
  background: #1e1e2e;
  color: white;
}

.setup-btn,
.refresh-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.setup-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
}

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

.setup-btn:hover,
.refresh-btn:hover {
  transform: translateY(-2px);
}

.library-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px 30px;
  border-radius: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #4ecdc4;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-top: 5px;
}

.loading-section,
.error-section,
.empty-library {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  background: rgba(255, 107, 107, 0.1);
  border-radius: 15px;
  margin: 20px;
}

.retry-btn {
  background: #ff6b6b;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  margin-top: 15px;
}

.empty-library {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  margin: 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.setup-link {
  display: inline-block;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
  text-decoration: none;
  padding: 15px 30px;
  border-radius: 15px;
  font-weight: bold;
  margin-top: 20px;
  transition: transform 0.3s ease;
}

.setup-link:hover {
  transform: translateY(-3px);
}

.manga-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  padding: 30px;
}

.manga-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.manga-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.manga-thumbnail {
  width: 100%;
  height: 300px;
  margin-bottom: 15px;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.manga-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-thumbnail {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(255, 107, 107, 0.2));
}

.manga-info h3 {
  margin: 0 0 10px 0;
  color: #fff;
  font-size: 1.3rem;
  line-height: 1.3;
}

.manga-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
}

.chapter-count {
  font-weight: bold;
  color: #4ecdc4;
}

.author {
  font-size: 0.9rem;
  opacity: 0.8;
}

.status {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 12px;
  align-self: flex-start;
}

.status.ongoing {
  background: rgba(76, 175, 80, 0.3);
  color: #4caf50;
}

.status.completed {
  background: rgba(33, 150, 243, 0.3);
  color: #2196f3;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.genre {
  font-size: 0.7rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 8px;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .library-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .manga-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
  }
}

/* Card Sizes */
.manga-grid.card-size-small {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.manga-grid.card-size-medium {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.manga-grid.card-size-large {
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}

.manga-grid.card-size-small .manga-thumbnail {
  height: 250px;
}

.manga-grid.card-size-medium .manga-thumbnail {
  height: 300px;
}

.manga-grid.card-size-large .manga-thumbnail {
  height: 400px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
  margin: 20px 30px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.page-btn {
  background: rgba(78, 205, 196, 0.2);
  border: 2px solid #4ecdc4;
  color: #4ecdc4;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.page-btn:hover:not(:disabled) {
  background: #4ecdc4;
  color: white;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
  align-items: center;
}

.page-number {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
}

.page-number:hover {
  background: rgba(255, 255, 255, 0.2);
}

.page-number.active {
  background: #4ecdc4;
  border-color: #4ecdc4;
  color: white;
  font-weight: bold;
}

.page-ellipsis {
  color: rgba(255, 255, 255, 0.6);
  padding: 0 10px;
}

.page-info {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-left: 20px;
}

@media (max-width: 768px) {
  .pagination {
    flex-wrap: wrap;
    gap: 10px;
    margin: 10px;
    padding: 20px;
  }
  
  .page-info {
    margin-left: 0;
    width: 100%;
    text-align: center;
    margin-top: 10px;
  }
}
</style>