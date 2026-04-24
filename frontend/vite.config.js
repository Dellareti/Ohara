import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],

  // Development server settings
  server: {
    host: true,
    port: 5173,
    open: true, // Automatically opens browser
    strictPort: true, // Fail if port is already in use

    // Proxy to the backend API
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => {
          return path
        }
      }
    }
  },

  // Resolve alias
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },

  // Build settings
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },

  // Project root (important for SPAs)
  root: './',
  publicDir: 'public',

  // SPA-specific settings
  appType: 'spa'
})
