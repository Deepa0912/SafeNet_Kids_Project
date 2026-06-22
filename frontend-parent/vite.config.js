import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    strictPort: false,
    host: true,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/socket.io': { target: 'http://localhost:8000', changeOrigin: true, ws: true },
    }
  }
})
