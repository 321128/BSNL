import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/ws': {
        target: 'http://localhost:8000',
        ws: true
      },
      '/translate': 'http://localhost:8000',
      '/tts': 'http://localhost:8000'
    }
  }
})