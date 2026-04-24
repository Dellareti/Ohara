<template>
  <div class="settings-view">
    <div class="settings-header">
      <h1>System Settings</h1>
      <p>Customize your reading experience and general settings</p>
    </div>

    <div class="settings-content">
      <!-- Reading Settings -->
      <div class="settings-section">
        <h2>Reading Settings</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Default Reading Mode:</label>
            <select
              :value="readerStore.readingMode"
              @change="updateReaderSetting('readingMode', $event.target.value)"
              class="setting-input">
              <option value="single">Single Page (Horizontal)</option>
              <option value="vertical">Vertical (Scroll)</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Default Image Fit:</label>
            <select
              :value="readerStore.fitMode"
              @change="updateReaderSetting('fitMode', $event.target.value)"
              class="setting-input">
              <option value="width">Fit Width</option>
              <option value="height">Fit Height</option>
              <option value="screen">Fit Screen</option>
              <option value="original">Original Size</option>
            </select>
          </div>


          <div class="setting-item">
            <label>Default Theme:</label>
            <select
              :value="readerStore.theme"
              @change="updateReaderSetting('theme', $event.target.value)"
              class="setting-input">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="sepia">Sepia</option>
            </select>
          </div>


        </div>
      </div>

      <!-- Interface Settings -->
      <div class="settings-section">
        <h2>Interface</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Library Card Size:</label>
            <select
              :value="settingsStore.interface.cardSize"
              @change="updateInterfaceSetting('cardSize', $event.target.value)"
              class="setting-input">
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Items per Page:</label>
            <select
              :value="settingsStore.interface.itemsPerPage"
              @change="updateInterfaceSetting('itemsPerPage', Number($event.target.value))"
              class="setting-input">
              <option :value="20">20 items</option>
              <option :value="50">50 items</option>
              <option :value="100">100 items</option>
            </select>
          </div>

        </div>
      </div>

      <!-- Performance Settings -->
      <div class="settings-section">
        <h2>Performance</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Image Cache (MB):</label>
            <select
              :value="settingsStore.performance.cacheSize"
              @change="updatePerformanceSetting('cacheSize', Number($event.target.value))"
              class="setting-input">
              <option :value="50">50 MB</option>
              <option :value="100">100 MB</option>
              <option :value="200">200 MB</option>
              <option :value="500">500 MB</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Page Preloading:</label>
            <select
              :value="settingsStore.performance.preloadPages"
              @change="updatePerformanceSetting('preloadPages', Number($event.target.value))"
              class="setting-input">
              <option :value="1">1 page</option>
              <option :value="3">3 pages</option>
              <option :value="5">5 pages</option>
              <option :value="10">10 pages</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Reader Max Cache:</label>
            <select
              :value="settingsStore.performance.maxCacheSize"
              @change="updatePerformanceSetting('maxCacheSize', Number($event.target.value))"
              class="setting-input">
              <option :value="25">25 pages</option>
              <option :value="50">50 pages</option>
              <option :value="100">100 pages</option>
              <option :value="200">200 pages</option>
            </select>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input
                type="checkbox"
                :checked="settingsStore.performance.enableCache"
                @change="updatePerformanceSetting('enableCache', $event.target.checked)" />
              Enable Library Cache
            </label>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input
                type="checkbox"
                :checked="settingsStore.performance.compressImages"
                @change="updatePerformanceSetting('compressImages', $event.target.checked)" />
              Compress Images Automatically
            </label>
          </div>

          <div class="setting-item">
            <button @click="clearCache" class="action-btn secondary">
              Clear Cache ({{ cacheUsed }} MB in use)
            </button>
          </div>
        </div>
      </div>

      <!-- Backup Settings -->
      <div class="settings-section">
        <h2>Backup and Data</h2>
        <div class="settings-grid">
          <div class="setting-item checkbox-item">
            <label>
              <input
                type="checkbox"
                :checked="settingsStore.system.autoSaveProgress"
                @change="updateSystemSetting('autoSaveProgress', $event.target.checked)" />
              Auto-Save Progress
            </label>
          </div>

          <div class="setting-item">
            <label>Backup Status:</label>
            <div class="backup-status">
              <span class="status-indicator">Use export/import for manual backup</span>
            </div>
          </div>
        </div>
      </div>

            <!-- System Information -->
      <div class="settings-section">
        <h2>System Information</h2>
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">Ohara Version:</span>
            <span class="info-value">v{{ settingsStore.system.version }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Preloaded Pages:</span>
            <span class="info-value">{{ readerStore.preloadedPages.size }} pages</span>
          </div>
          <div class="info-item">
            <span class="info-label">Cache in Use:</span>
            <span class="info-value">{{ cacheUsed }} MB / {{ settingsStore.performance.cacheSize }} MB</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="settings-actions">
        <button @click="exportSettings" class="action-btn secondary">
          Export Settings
        </button>
        <button @click="importSettings" class="action-btn secondary">
          Import Settings
        </button>
        <button @click="resetToDefaults" class="action-btn danger">
          Restore Defaults
        </button>
        <button @click="saveSettings" class="action-btn primary">
          Save Settings
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useLibraryStore } from '@/store/library'
import { useReaderStore } from '@/store/reader'
import { useSettingsStore } from '@/store/settings'
import { useToast } from '@/composables/useToast'

export default {
  name: 'SettingsView',
  setup() {
    const libraryStore = useLibraryStore()
    const readerStore = useReaderStore()
    const settingsStore = useSettingsStore()
    const { showSuccess, showError } = useToast()

    const backendOnline = ref(false)
    const libraryPath = ref('')

    const cacheUsed = computed(() => settingsStore.cacheUsed)

    const updateReaderSetting = (key, value) => {
      if (key === 'readingMode') {
        readerStore.setReadingMode(value)
      } else {
        readerStore.updateReadingSettings({ [key]: value })
      }
    }

    const updateInterfaceSetting = (key, value) => {
      settingsStore.updateInterfaceSettings({ [key]: value })
    }

    const updatePerformanceSetting = (key, value) => {
      settingsStore.updatePerformanceSettings({ [key]: value })
    }

    const updateSystemSetting = (key, value) => {
      settingsStore.system[key] = value
      settingsStore.saveSettings()
    }

    const clearCache = () => {
      settingsStore.clearCache()
      showSuccess('Cache cleared successfully!')
    }

    const loadSettings = () => {
      try {
        readerStore.loadSettings()
        settingsStore.loadSettings()
      } catch (error) {
        console.error('Error loading settings:', error)
      }
    }

    const saveSettings = () => {
      try {
        readerStore.saveSettings()

        const success = settingsStore.saveSettings()

        if (success) {
          showSuccess('Settings saved successfully!')
        } else {
          showError('Error saving settings')
        }

      } catch (error) {
        console.error('Error saving settings:', error)
        showError('Error saving settings')
      }
    }

    const resetToDefaults = () => {
      if (confirm('Are you sure you want to restore all settings to default values?')) {
        settingsStore.resetToDefaults()

        showSuccess('Settings restored to defaults!')
      }
    }

    const exportSettings = () => {
      try {
        const settings = settingsStore.allSettings

        const dataStr = JSON.stringify(settings, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })

        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = `ohara_settings_${new Date().toISOString().split('T')[0]}.json`
        link.click()

        showSuccess('Settings exported successfully!')

      } catch (error) {
        console.error('Error exporting settings:', error)
        showError('Error exporting settings')
      }
    }

    const importSettings = () => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'

      input.onchange = (event) => {
        const file = event.target.files[0]
        if (!file) return

        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const settingsData = e.target.result
            const success = settingsStore.importSettings(settingsData)

            if (success) {
              showSuccess('Settings imported successfully!')
            } else {
              showError('Error importing settings: invalid file')
            }
          } catch (error) {
            console.error('Error importing settings:', error)
            showError('Error importing settings: invalid file')
          }
        }
        reader.readAsText(file)
      }

      input.click()
    }

    const checkSystemInfo = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/test')
        backendOnline.value = response.ok
      } catch {
        backendOnline.value = false
      }

      libraryPath.value = libraryStore.libraryPath || 'Not configured'
    }

    onMounted(() => {
      loadSettings()
      checkSystemInfo()
    })


    return {
      readerStore,
      settingsStore,
      backendOnline,
      libraryPath,
      cacheUsed,
      updateReaderSetting,
      updateInterfaceSetting,
      updatePerformanceSetting,
      updateSystemSetting,
      saveSettings,
      resetToDefaults,
      exportSettings,
      importSettings,
      clearCache
    }
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  padding: 20px;
}

.settings-header {
  text-align: center;
  margin-bottom: 40px;
}

.settings-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: white;
}

.settings-header p {
  font-size: 1.2rem;
  opacity: 0.8;
}

.settings-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.settings-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 25px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.settings-section h2 {
  color: #4ecdc4;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item.checkbox-item {
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.setting-item.full-width {
  grid-column: 1 / -1;
}

.setting-item label {
  font-weight: 500;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-input {
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 1rem;
}

.setting-input:focus {
  outline: none;
  border-color: #4ecdc4;
}

.range-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.range-input {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.range-value {
  min-width: 80px;
  text-align: right;
  font-weight: 500;
  color: #4ecdc4;
}


.backup-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-indicator.simple {
  color: #4ecdc4;
  font-weight: 500;
}

.settings-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: transform 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.primary {
  background: #3BAF41;

  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.danger {
  background:#E53935;
  color: white;
}

.system-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.info-label {
  font-weight: 500;
}

.info-value {
  font-weight: bold;
}

.status-online {
  color: #4caf50;
}

.status-offline {
  color: #f44336;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-actions {
    flex-direction: column;
  }
  
  .system-info {
    grid-template-columns: 1fr;
  }
  
}
</style>