# ⚡ ELITK-8 — AI-Native Business Orchestration Platform

[![CI](https://github.com/mohamedosamaai/elitk-8/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamedosamaai/elitk-8/actions/workflows/ci.yml)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0_Strict-blue?style=flat-square&logo=typescript)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=flat-square&logo=vite)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![Google Gemini](https://img.shields.io/badge/Gemini_AI-API-4285F4?style=flat-square&logo=google)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📌 Architecture Overview

ELITK-8 is an AI Business Orchestration System that unifies 3D interactive ideation, multi-agent AI pipelines, and enterprise workflow execution into a single high-performance platform. The core runtime is built on React + Vite with TypeScript strict mode, powered by a Node.js/Express backend that proxies Google Gemini API calls and handles TTS synthesis behind rate-limiting middleware.

The system decouples heavy AI compute operations from frontend rendering using a dedicated `server.ts` edge handler, Pino structured JSON logging, and a resilient `express-rate-limit` layer protecting all `/api` routes from quota exploitation.

---

## 🏛️ System Documentation (Wiki)

Full architectural specs, schema models, and integration blueprints:

| Resource | Description |
|---|---|
| 📖 [System Architecture](../../wiki/System-Architecture) | Sequence diagrams, data flow, agent orchestrators |
| 🗄️ [Database Schema](../../wiki/Database-Schema) | ER models, indexing strategy, SQL migrations |
| 🤖 [API & AI Agent Integration](../../wiki/API-and-AI-Agent-Integration) | Gemini API pipeline, prompt orchestration, fallback handling |
| 🛠️ [Developer Setup](../../wiki/Developer-Setup) | Local dev requirements, Docker environment, CLI workflows |
| 🏡 [Wiki Home](../../wiki/Home) | Engineering principles and architectural overview |

---

## 🗺️ Roadmap & Project Board

Track active sprints, issue priorities, and component breakdowns:
👉 **[ELITK-8 System Roadmap & Architecture Board](../../projects/2)**

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript (strict), Three.js, WebGL, TailwindCSS |
| State & Rendering | Zustand, `@react-three/fiber`, `@react-three/drei` |
| Backend | Node.js, Express, Pino Logger, `express-rate-limit` |
| AI Pipeline | Google Gemini API, multi-agent orchestration, Zod validation |
| DevOps | GitHub Actions CI, Docker, Docker Compose |
| Testing | Vitest |

---

## 🚀 Quick Setup

### Prerequisites
- Node.js ≥ 22
- npm ≥ 10
- A Google Gemini API key (obtain from [Google AI Studio](https://aistudio.google.com))

### 1. Clone & Install

```bash
git clone https://github.com/mohamedosamaai/elitk-8.git
cd elitk-8
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local and populate all required keys
```

### 3. Start Development Server

```bash
npm run dev
```

The Vite frontend starts on `http://localhost:5173`.
The Express API server starts on `http://localhost:3000`.

### 4. Docker (Production)

```bash
# Copy and populate your production secrets
cp .env.example .env.production

# Build and run
docker-compose up --build
```

### 5. Docker (Local Dev with Live Reload)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

---

## 📁 Project Structure

```
elitk-8/
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # Three-job pipeline: quality → test → build
│   ├── ISSUE_TEMPLATE/         # YAML issue forms (feature, bug)
│   ├── CODEOWNERS
│   ├── COMMIT_POLICY.md
│   ├── dependabot.yml          # Grouped weekly updates
│   └── pull_request_template.md
├── public/                     # Static assets (manifest, robots, sw.js)
├── src/
│   ├── lib/
│   │   └── ai/
│   │       └── client.ts       # Gemini REST client abstraction
│   ├── types/
│   │   └── agent.ts            # Multi-agent pipeline contracts
│   ├── knowledge/              # Static knowledge routing layer
│   ├── App.tsx                 # Root application component
│   ├── AudioEngine.ts          # Web Audio API abstraction
│   ├── ErrorBoundary.tsx       # React error boundary + WebGL fallback
│   ├── Resonance3D.tsx         # Three.js / WebGL particle engine
│   ├── constants.ts            # Shared configuration constants
│   ├── types.ts                # TypeScript interface contracts
│   └── useFaceTracker.ts       # MediaPipe face tracking hook
├── tests/
│   └── tts.test.ts             # Vitest unit tests (16 tests)
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Dockerfile                  # Multi-stage production build
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Local dev with live reload
├── server.ts                   # Express API (TTS proxy, CORS, rate limiting)
├── tsconfig.json               # Frontend TS config (strict mode)
├── tsconfig.node.json          # Server-side TS config
├── vitest.config.ts            # Test runner configuration
├── vite.config.ts              # Vite build (no secrets in bundle)
└── .env.example                # Sanitized environment blueprint
```

---

## 🔐 Security

- All API keys are validated via Zod schemas at server startup — the process exits hard on missing credentials rather than silently degrading.
- Rate limiting enforced on all `/api` routes (100 req/15min), with stricter limits on `/api/tts` (20 req/15min) to protect Google Cloud billing quotas.
- No secrets are committed to the repository. See [SECURITY.md](./SECURITY.md) for the responsible disclosure policy.

---

## 📋 Governance

| Document | Purpose |
|---|---|
| [CHANGELOG](./CHANGELOG.md) | Release history and breaking changes |
| [CONTRIBUTING](./CONTRIBUTING.md) | Branch workflow, PR requirements, commit conventions |
| [CODE_OF_CONDUCT](./CODE_OF_CONDUCT.md) | Community standards |
| [SECURITY](./SECURITY.md) | Vulnerability disclosure policy |

---

## 📄 License

[MIT License](./LICENSE) — Mohamed Osama
