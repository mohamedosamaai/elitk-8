<div align="center">

  # elitk-8

  ### A real-time immersive particle world where sound, voice, presence, and AI shape a cinematic number eight

  [![Three.js](https://img.shields.io/badge/Three.js-WebGL-000000?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org)
  [![React Three Fiber](https://img.shields.io/badge/React_Three_Fiber-3D-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://docs.pmnd.rs/react-three-fiber)
  [![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
  [![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Tracking-00A67E?style=for-the-badge)](https://ai.google.dev/edge/mediapipe/solutions/guide)
  [![Gemini](https://img.shields.io/badge/Gemini-AI%20Assistant-4285F4?style=for-the-badge)](https://ai.google.dev)

  **A signature interactive experiment by [Mohamed Osama](https://github.com/mohamedosamaai)**

  [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

</div>

---

## What This Is

Mohamed Resonance is a real-time immersive 3D experience where thousands of particles respond to sound, voice, camera presence, and touch — converging around a persistent, cinematic number eight.

Built as a signature creative and technical demonstration, this experiment sits at the intersection of generative 3D, AI interaction, real-time audio analysis, and computer vision — all running in the browser.

---

## Experience Pillars

| Signal | How the Experience Responds |
|---|---|
| **Sound** | Frequency-driven pulse, glow, and particle displacement across the formation |
| **Voice** | Microphone input drives the AI assistant and ambient audio engine |
| **Presence** | Face tracking via camera influences particle behavior in real time |
| **Touch** | Mouse drag, scroll zoom, right-click scatter, and HUD controls |

---

## Key Features

### Generative 3D Engine

- Custom GPGPU physics simulation driving thousands of magnetic particles via WebGL shaders
- Real-time shape morphing between 8+ formations: Core 8, Sphere, Torus, DNA Helix, Vortex, Grid, and more
- Persistent cinematic number eight as the focal center across all particle formations
- Post-processing glow and bloom for cinematic output quality

### AI Assistant Layer

- Built-in conversational AI powered by the Gemini SDK
- Contextual local knowledge base for in-experience guidance
- Text-to-Speech output integrated directly with the audio engine
- Voice command input via browser Web Speech API

### Reactive Audio System

- Real-time FFT frequency analysis — bass, mid, and high bands each drive distinct visual reactions
- Microphone amplitude controls particle pulse intensity and ambient glow
- TTS and audio engine share a unified playback layer with no conflicts

### Computer Vision

- MediaPipe Face Mesh for head-tracking and blink detection
- Camera presence shifts particle behavior based on face position in real time
- Camera mode is optional — the experience runs fully in touch-only mode

---

## Architecture

```txt
User Input Layer
  ├── Microphone → AudioEngine (FFT + TTS)
  ├── Camera    → MediaPipe Face Mesh (head position + blink)
  ├── Mouse     → OrbitControls (drag / zoom / scatter)
  └── Voice     → Web Speech API → Gemini Assistant

React Three Fiber Scene
  ├── GPGPU Compute Shader (particle physics)
  ├── WebGL Particle Renderer (instanced geometry)
  ├── Shape Morphing System (8+ formations)
  ├── Glow / Bloom Post-Processing
  └── Number 8 Focal Geometry

AI + Knowledge Layer
  ├── Gemini SDK (conversational)
  ├── Local Knowledge Dictionary
  └── TTS → AudioEngine playback

Express Backend
  └── Static serving + API fallback endpoints
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| 3D Engine | Three.js, React Three Fiber, custom GPGPU shaders |
| AI | Google Gemini SDK (`@google/genai`) |
| Computer Vision | MediaPipe Face Mesh |
| Audio | Web Audio API, custom AudioEngine, Text-to-Speech |
| UI | React 18, TypeScript, Tailwind CSS, Framer Motion |
| Build | Vite |
| Backend | Express (static serving and API fallback) |

---

## Project Structure

```txt
src/
  App.tsx              # Main UI overlay, state, and interaction coordination
  Resonance3D.tsx      # React Three Fiber scene and GPGPU shader logic
  AudioEngine.ts       # Audio decoding, FFT analysis, TTS, microphone integration
  useFaceTracker.ts    # MediaPipe Face Mesh integration
  knowledge/           # AI contextual knowledge modules

server.ts              # Express backend — serves the built app
vite.config.ts         # Build configuration
```

---

## Getting Started

**Requirements:** Node.js 18+

```bash
# 1. Install dependencies
npm install

# 2. Create environment file
cp .env.example .env
# GEMINI_API_KEY=your_gemini_key
# VITE_GOOGLE_CLOUD_API_KEY=your_cloud_key  (for TTS)

# 3. Start development
npm run dev

# 4. Build for production
npm run build

# 5. Preview production build
npm run preview
```

---

## Controls

| Control | Action |
|---|---|
| **Mouse drag** | Orbit the 3D particle formation |
| **Scroll / trackpad** | Zoom in and out of the particle field |
| **Right click** | Scatter and reset the particle state |
| **Microphone icon** | Toggle active voice input |
| **Camera icon** | Toggle MediaPipe face tracking |
| **Speaker icon** | Toggle audio engine and TTS output |
| **Shape / HUD button** | Switch between particle formations |

---

## Known Constraints

- Camera and microphone permissions must be explicitly granted by the browser. Denying either disables the related feature gracefully.
- GPGPU particle simulation is GPU-intensive. Performance on older mobile devices or low-end GPUs may be limited.
- Voice recognition depends on the browser Web Speech API — availability varies by browser and locale.

---

## License

Proprietary — All Rights Reserved.

Copyright © 2026 Mohamed Osama.

Shared for demonstration and evaluation purposes only. No permission is granted to copy, modify, redistribute, sublicense, sell, or use any part of this project — including source code, visual system, shaders, or interaction design — without explicit written permission from the author.

See [`LICENSE`](LICENSE) for the full notice.

---

## Author

| | |
|---|---|
| **Company** | BagbackTech (Bagback Digital Solutions) — CR 218773 |
| **Author** | Mohamed Osama — Systems & AI Business Architect, Dubai UAE |
| **GitHub** | [@mohamedosamaai](https://github.com/mohamedosamaai) |
| **LinkedIn** | [@mohamedosamaai](https://www.linkedin.com/in/mohamedosamaai) |
| **Instagram** | [@mohamedosamaai](https://instagram.com/mohamedosamaai) |
| **Personal Site** | [mohamedosama.me](https://mohamedosama.me) |
| **Email** | [im@mohamedosama.me](mailto:im@mohamedosama.me) |

---

## Product Ecosystem

> All products designed, built, and operated by Mohamed Osama

| Product | Description | Live |
|---|---|---|
| **Elitk** | AI operating system for social media, ads, CRM, outreach, and growth | [![](https://img.shields.io/badge/-elitk.com-6D4AFF?style=flat-square)](https://elitk.com) |
| **Elitk Library** | 2,771 curated AI prompts, MCP profiles, and developer skill playbooks | [![](https://img.shields.io/badge/-library.elitk.com-4285F4?style=flat-square)](https://library.elitk.com) |
| **Elitk Ops** | Field operations OS for technical-service and maintenance companies | [![](https://img.shields.io/badge/-ops.elitk.com-5B20F0?style=flat-square)](https://ops.elitk.com) |
| **BagbackTech** | AI product studio, startup evaluation, and proof of work | [![](https://img.shields.io/badge/-bagbacktech.com-000000?style=flat-square)](https://bagbacktech.com) |
| **Bagback Shop** | Multi-vendor commerce — retail, affiliate, payments, and fulfillment | [![](https://img.shields.io/badge/-bagback.shop-FF2D20?style=flat-square)](https://bagback.shop) |
| **La Forma** | Bilingual technical services platform and lead-generation for UAE | [![](https://img.shields.io/badge/-laforma.ae-0A7F5A?style=flat-square)](https://laforma.ae) |
| **Personal Site** | Mohamed Osama's personal website — AI-ready SEO, project archive | [![](https://img.shields.io/badge/-mohamedosama.me-38bdf8?style=flat-square)](https://mohamedosama.me) |

---

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-mohamedosamaai-181717?style=for-the-badge&logo=github)](https://github.com/mohamedosamaai)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mohamedosamaai-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohamedosamaai)
[![Personal Site](https://img.shields.io/badge/Personal_Site-mohamedosama.me-38bdf8?style=for-the-badge)](https://mohamedosama.me)
[![Company](https://img.shields.io/badge/BagbackTech-bagbacktech.com-000000?style=for-the-badge)](https://bagbacktech.com)
[![Email](https://img.shields.io/badge/Email-hello%40bagbacktech.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hello@bagbacktech.com)

</div>
