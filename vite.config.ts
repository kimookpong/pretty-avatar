/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // Served from GitHub Pages under /pretty-avatar/; plain / for local dev.
  base: process.env.SITE_BASE ?? '/',
  build: { outDir: 'site-build' },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
  },
})
