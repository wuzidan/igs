import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import vueSetupExtend from 'vite-plugin-vue-setup-extend'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    vueSetupExtend(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/graphs': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/teacher': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/api': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/student': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/historyRecord': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/question': {
        target: 'http://localhost:8090',
        changeOrigin: true,
        secure: false
      },
      '/knowledge': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/visualization': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/model': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/classInfo': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
