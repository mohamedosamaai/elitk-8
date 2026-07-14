import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig, loadEnv } from 'vite';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

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

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react(), tailwindcss(), mediaPipeWorkaround()],
    define: {
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GOOGLE_CLOUD_API_KEY': JSON.stringify(env.GOOGLE_CLOUD_API_KEY || env.VITE_GOOGLE_CLOUD_API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
    },
  };
});
