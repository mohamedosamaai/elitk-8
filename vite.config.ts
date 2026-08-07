import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vite';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// MediaPipe CJS shims — their UMD bundles rely on globals that Vite's ESM transform drops.
// Injecting the exports manually restores compatibility without patching node_modules.
function mediaPipeWorkaround() {
  return {
    name: 'mediapipe-workaround',
    load(id: string) {
      if (id.endsWith('face_mesh.js')) {
        let code = fs.readFileSync(id, 'utf-8');
        if (!code.includes('exports.FaceMesh =')) {
          code += '\nexports.FaceMesh = (typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : self).FaceMesh;';
        }
        return { code };
      }
      if (id.endsWith('camera_utils.js')) {
        let code = fs.readFileSync(id, 'utf-8');
        if (!code.includes('exports.Camera =')) {
          code += '\nexports.Camera = (typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : self).Camera;';
        }
        return { code };
      }
      return null;
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), mediaPipeWorkaround()],
  // No server-side secrets are injected here.
  // All AI and TTS operations are proxied through server.ts to keep API keys server-side only.
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    },
  },
  server: {
    hmr: process.env.DISABLE_HMR !== 'true',
    proxy: {
      '/api': {
        target: `http://localhost:${process.env.PORT || 3000}`,
        changeOrigin: true,
      },
    },
  },
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          three: ['three', '@react-three/fiber', '@react-three/drei'],
        },
      },
    },
  },
});
