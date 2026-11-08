import { defineConfig } from 'vite'

// Minimal Vite config. The .frag shader is imported with ?raw (built-in),
// so no extra plugin is required.
export default defineConfig({
  server: { open: true },
})
