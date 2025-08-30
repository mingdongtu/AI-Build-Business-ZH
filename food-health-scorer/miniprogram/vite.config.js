import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    uni(),
  ],
  server: {
    port: 8080,
    open: true,
    cors: true
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './')
    }
  },
  publicDir: 'public',
  build: {
    assetsDir: 'static',
    cssCodeSplit: true
  }
})
