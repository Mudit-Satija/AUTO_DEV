import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true
  },
  define: {
    'import.meta.env': JSON.stringify({
      VITE_API_BASE_URL: 'http://localhost:8000'
    })
  }
})