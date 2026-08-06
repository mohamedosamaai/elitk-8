import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig, loadEnv } from 'vite';
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

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react(), tailwindcss(), mediaPipeWorkaround()],
    define: {
      // Runtime secrets are read server-side; only GEMINI_API_KEY is needed client-side
      // because the Gemini SDK is instantiated in the browser for streaming responses.
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY || ''),
      'process.env.GOOGLE_CLOUD_API_KEY': JSON.stringify(env.GOOGLE_CLOUD_API_KEY || env.VITE_GOOGLE_CLOUD_API_KEY || ''),
      'process.env.CHAT_LOGGER_URL': JSON.stringify(env.CHAT_LOGGER_URL || ''),
      'process.env.LOGGER_API_KEY': JSON.stringify(env.LOGGER_API_KEY || ''),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      hmr: process.env.DISABLE_HMR !== 'true',
    },
  };
});
