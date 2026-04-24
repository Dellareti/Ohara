<template>
  <div class="setup-container">
    <!-- Header -->
    <div class="setup-header">
      <h1>Configure Ohara Library</h1>
      <p>Configure your manga library to start reading</p>
    </div>

    <!-- Main Setup -->
    <div class="setup-main">
      <div class="setup-card">
        <div class="card-header">
          <h2>Library Folder</h2>
          <p>Choose the folder where your manga is organized</p>
        </div>

        <div class="input-section">
          <label for="libraryPath">Library Path:</label>
          <input
            id="libraryPath"
            v-model="libraryPath"
            type="text"
            placeholder="/home/user/Library or C:\Manga"
            class="path-input"
            @input="validatePathDebounced"
          />

          <!-- Validation Status -->
          <div v-if="validation.checked" class="validation-status">
            <div v-if="validation.valid" class="status valid">
              {{ validation.message }}
            </div>
            <div v-else class="status invalid">
              ❌ {{ validation.message }}
            </div>
          </div>
        </div>

        <!-- Previous Library (if it exists) -->
        <div v-if="previousLibrary" class="previous-section">
          <h3>Previous Library</h3>
          <div class="previous-path">
            <span class="path-text">{{ previousLibrary }}</span>
            <button
              @click="usePreviousLibrary"
              class="use-previous-btn"
            >
              Use This Folder
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button
            @click="configureLibrary"
            :disabled="!validation.valid || isConfiguring"
            class="configure-btn"
          >
            <span v-if="isConfiguring">Configuring...</span>
            <span v-else>Configure Library</span>
          </button>

          <router-link to="/library" class="back-btn">
            Back to Library
          </router-link>
        </div>
      </div>

      <!-- Recommended Structure -->
      <div class="help-card">
        <h3>Recommended Structure</h3>
        <div class="structure-example">
          <div class="structure-good">
            <h4>✅ Organized</h4>
            <pre>📁 Library/
├── 📁 One Piece/
│   ├── 📁 Chapter 01/
│   │   ├── 01.jpg
│   │   └── 02.jpg
│   └── 📁 Chapter 02/
├── 📁 Naruto/
└── 📁 Solo Leveling/</pre>
          </div>

          <div class="structure-bad">
            <h4>❌ Problematic</h4>
            <pre>📁 Manga_Folder/
├── one_piece_ch1.zip
├── naruto.pdf
├── 📁 Mixed/
│   ├── onepiece_001.jpg
│   └── naruto_001.jpg
└── loose_image.jpg</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '@/store/library'
import { useToast } from '@/composables/useToast'

export default {
  name: 'LibrarySetup',
  setup() {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const router = useRouter()
    const libraryStore = useLibraryStore()
    const { showError } = useToast()
    
    const libraryPath = ref('')
    const validation = ref({ checked: false, valid: false, message: '' })
    const previousLibrary = ref('')
    const isConfiguring = ref(false)

    let validationTimeout = null

    const validatePathDebounced = () => {
      clearTimeout(validationTimeout)
      validationTimeout = setTimeout(validatePath, 500)
    }

    const validatePath = async () => {
      if (!libraryPath.value.trim()) {
        validation.value = { checked: false, valid: false, message: '' }
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/validate-path?path=${encodeURIComponent(libraryPath.value)}`)
        const data = await response.json()

        validation.value = {
          checked: true,
          valid: data.is_valid,
          message: data.message || (data.is_valid ? 'Valid path!' : 'Invalid path')
        }


      } catch (error) {
        console.error('Validation error:', error)
        validation.value = {
          checked: true,
          valid: false,
          message: 'Error validating path'
        }
      }
    }

    const configureLibrary = async () => {
      if (!validation.value.valid) return

      isConfiguring.value = true

      try {
        await libraryStore.setLibraryPath(libraryPath.value)

        const formData = new FormData()
        formData.append('library_path', libraryPath.value)

        const response = await fetch(`${API_BASE_URL}/api/scan-library`, {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error(`HTTP Error ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        if (data.library) {
          libraryStore.mangas = data.library.mangas || []
          libraryStore.totalMangas = data.library.total_mangas || 0
          libraryStore.totalChapters = data.library.total_chapters || 0
          libraryStore.totalPages = data.library.total_pages || 0
          libraryStore.isInitialized = true

          router.push('/library')
        } else {
          throw new Error(data.message || 'Error scanning library')
        }

      } catch (error) {
        console.error('Error configuring library:', error)
        showError('Error configuring library: ' + error.message)
      } finally {
        isConfiguring.value = false
      }
    }

    const usePreviousLibrary = () => {
      libraryPath.value = previousLibrary.value
      validatePath()
    }

    onMounted(() => {
      if (libraryStore.libraryPath) {
        previousLibrary.value = libraryStore.libraryPath
      }

      if (libraryStore.libraryPath && !libraryPath.value) {
        libraryPath.value = libraryStore.libraryPath
        validatePath()
      }
    })
    
    return {
      libraryPath,
      validation,
      previousLibrary,
      isConfiguring,
      validatePathDebounced,
      configureLibrary,
      usePreviousLibrary
    }
  }
}
</script>

<style scoped>
.setup-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  padding: 20px;
}

.setup-header {
  text-align: center;
  margin-bottom: 40px;
}

.setup-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: white;
}

.setup-header p {
  font-size: 1.2rem;
  opacity: 0.8;
}

.setup-main {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.setup-card,
.help-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.card-header h2 {
  color: #fff;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.card-header p {
  opacity: 0.8;
  margin-bottom: 30px;
}

.input-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #fff;
}

.path-input {
  width: 100%;
  padding: 15px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 1rem;
  margin-bottom: 15px;
}

.path-input:focus {
  outline: none;
  border-color: #4ecdc4;
}

.validation-status {
  margin-bottom: 20px;
}

.status {
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: bold;
}

.status.valid {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid #4caf50;
  color: #4caf50;
}

.status.invalid {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid #f44336;
  color: #f44336;
}

.previous-section {
  margin: 20px 0;
  padding: 15px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.previous-section h3 {
  color: #ffc107;
  margin-bottom: 10px;
}

.previous-path {
  display: flex;
  align-items: center;
  gap: 15px;
}

.path-text {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  padding: 8px 12px;
  border-radius: 5px;
  font-family: monospace;
  font-size: 0.9rem;
}

.use-previous-btn {
  padding: 8px 15px;
  background: #ffc107;
  color: #1e1e2e;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  white-space: nowrap;
}

.use-previous-btn:hover {
  background: #ffb300;
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.configure-btn {
  flex: 1;
  padding: 15px 30px;
  background: #3BAF41;
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.configure-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(78, 205, 196, 0.4);
}

.configure-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.back-btn {
  padding: 15px 25px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  color: white;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  font-weight: 500;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.help-card h3 {
  color: #fff;
  margin-bottom: 20px;
}

.structure-example {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.structure-good,
.structure-bad {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
}

.structure-good h4 {
  color: #4caf50;
  margin-bottom: 10px;
}

.structure-bad h4 {
  color: #f44336;
  margin-bottom: 10px;
}

.structure-good pre,
.structure-bad pre {
  font-size: 0.8rem;
  line-height: 1.4;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .setup-main {
    grid-template-columns: 1fr;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .configure-btn {
    flex: none;
  }
}
</style>  