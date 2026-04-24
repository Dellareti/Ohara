import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import store from './store/index.js'
import { useToast } from './composables/useToast.js'

const app = createApp(App)

app.config.errorHandler = (error, instance, info) => {
  console.error('Global Error Handler:', error, info)
  const { showError } = useToast()
  showError(`Unexpected error: ${error.message || 'Unknown error'}`)
}

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  const { showError } = useToast()
  showError(`Connection error: ${event.reason?.message || 'Operation failed'}`)
  event.preventDefault()
})

app.use(router)

app.use(store)

app.mount('#app')

import { useLibraryStore } from './store/library.js'
const libraryStore = useLibraryStore()
libraryStore.initialize()