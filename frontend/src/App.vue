<template>
  <div id="app">
    <!-- Header/Navigation -->
    <header class="app-header">
      <nav class="main-nav">
        <div class="nav-brand">
          <router-link to="/library" class="brand-link">
            <h1>🏴‍☠️ Ohara</h1>
          </router-link>
          <span class="version">v1.0.0</span>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link">Library</router-link>
          <router-link to="/setup" class="nav-link">Setup</router-link>
          <router-link to="/settings" class="nav-link">Settings</router-link>
          <router-link to="/manual" class="nav-link">Manual</router-link>
        </div>
      </nav>
    </header>

    <!-- Main Content Area -->
    <main class="app-main">
      <!-- Vue Router View - pages are rendered here -->
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>Ohara Manga Reader - Read your favorite stories</p>
    </footer>

    <div class="toast-container">
      <transition-group name="toast" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast-${toast.type}`]"
          @click="removeToast(toast.id)"
        >
          <div class="toast-content">
            <span class="toast-message">{{ toast.message }}</span>
          </div>
          <button class="toast-close" @click.stop="removeToast(toast.id)">×</button>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from './composables/useToast.js'

export default {
  name: 'App',
  setup() {
    const isConnected = ref(false)
    const { toasts, removeToast } = useToast()
    
    const checkConnection = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/test`)
        if (response.ok) {
          isConnected.value = true
        } else {
          isConnected.value = false
        }
      } catch (error) {
        isConnected.value = false
      }
    }
    
    onMounted(() => {
      checkConnection()

      setInterval(checkConnection, 30000)
    })
    
    return { 
      isConnected,
      toasts,
      removeToast
    }
  }
}
</script>

<style>
/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  display: flex;
  flex-direction: column;
}

body:has(.manga-reader) .app-header,
body:has(.manga-reader) .app-footer {
  display: none !important;
}

.manga-reader ~ * .app-header,
.manga-reader ~ * .app-footer,
.manga-reader + * .app-header,
.manga-reader + * .app-footer {
  display: none !important;
}

/* When on the reader page, remove padding from main */
body:has(.manga-reader) .app-main {
  padding: 0;
  margin: 0;
  max-width: none;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* Header */
.app-header {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem 2rem;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.main-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-link {
  text-decoration: none;
  color: white;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.brand-link:hover {
  opacity: 0.8;
}

.nav-brand h1 {
  font-size: 1.8rem;
  color: white;
  margin: 0;
}

.version {
  font-size: 0.8rem;
  opacity: 0.6;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s;
  border: 1px solid transparent;
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(78, 205, 196, 0.2);
  border-color: #4ecdc4;
}

/* Connection Status */
.connection-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.connection-status.connected {
  background: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.connection-status.disconnected {
  background: rgba(244, 67, 54, 0.15);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 0.75rem;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Main Content */
.app-main {
  flex: 1;
  max-width: auto;
  margin: 0 auto;
  width: 100%;
  padding: 2rem;
}

/* Footer */
.app-footer {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem 2rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
  opacity: 0.8;
}

.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid;
}

.toast:hover {
  transform: translateX(-5px);
}

.toast-error {
  background: rgba(239, 68, 68, 0.9);
  border-left-color: #dc2626;
  color: white;
}

.toast-success {
  background: rgba(34, 197, 94, 0.9);
  border-left-color: #16a34a;
  color: white;
}

.toast-warning {
  background: rgba(245, 158, 11, 0.9);
  border-left-color: #d97706;
  color: white;
}

.toast-info {
  background: rgba(59, 130, 246, 0.9);
  border-left-color: #2563eb;
  color: white;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toast-message {
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
}

.toast-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 0 4px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .app-main {
    padding: 1rem;
  }
  
  .connection-status {
    order: -1;
    margin-bottom: 0.5rem;
  }
  
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .toast {
    margin: 0 auto;
    max-width: 100%;
  }
}
</style>