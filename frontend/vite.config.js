import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward API calls to the FastAPI backend in development.
      // Frontend uses /api/v1 by default (see src/config.js); the backend
      // also mounts routes at the bare prefix, so the proxy targets /api/v1.
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
