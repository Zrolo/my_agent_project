import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'node:path';

export default defineConfig({
  root: path.resolve(__dirname, 'frontend'),
  base: '/static/dist/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'frontend/src'),
    },
  },
  build: {
    outDir: path.resolve(__dirname, 'static/dist'),
    emptyOutDir: true,
    sourcemap: false,
    // Mermaid is loaded only when a student opens a diagram. Keep warnings focused on eager chunks.
    chunkSizeWarningLimit: 700,
  },
});
