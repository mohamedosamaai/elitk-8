<div align="center">

# ⚡ ELITK-8

[![CI](https://github.com/mohamedosamaai/elitk-8/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamedosamaai/elitk-8/actions)
[![CodeQL](https://github.com/mohamedosamaai/elitk-8/actions/workflows/codeql.yml/badge.svg)](https://github.com/mohamedosamaai/elitk-8/security/code-scanning)
[![License](https://img.shields.io/github/license/mohamedosamaai/elitk-8)](LICENSE)

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Express.js](https://img.shields.io/badge/express.js-%23404d59.svg?style=for-the-badge&logo=express&logoColor=%2361DAFB)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

> **Enterprise AI orchestration platform and web application.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)](https://mohamedosamaai.github.io/elitk-8)

</div>

---

## Architecture Diagram

```text
+-------------------+       +-------------------+       +-------------------+
|   Client (SPA)    |       |   API Gateway     |       |   AI Orchestrator |
|   React + Vite    | ----> |   Express.js      | ----> |   Gemini API      |
|   Tailwind CSS    | <---- |   Rate Limiter    | <---- |   TTS Engine      |
+-------------------+       +-------------------+       +-------------------+
        |                            |                            |
        v                            v                            v
+-------------------+       +-------------------+       +-------------------+
|   State Store     |       |   Validation      |       |   Security        |
|   Zustand         |       |   Zod Schema      |       |   CodeQL Checks   |
+-------------------+       +-------------------+       +-------------------+
```

## Request Lifecycle

```text
[User] -> [React UI] -> [Express API] -> [Rate Limiter] -> [Zod Validation]
                                                                    |
                                                                    v
[UI Updates] <- [JSON Stream] <- [Express Proxy] <- [Google Gemini API]
```

## Engineering Decisions

| Category | Decision | Rationale |
|---|---|---|
| **Architecture** | Full-stack Monorepo | Reduces cognitive load and ensures type safety across boundaries. |
| **Frontend** | React 19 + Vite | Maximizes performance, fast HMR, and future-proof concurrent rendering. |
| **Backend** | Express 5 | Minimalist edge handler for proxying AI requests and enforcing rate limits. |
| **Type Safety** | Zod + Strict TS | End-to-end type validation prevents runtime crashes. |
| **Styling** | TailwindCSS | Utility-first CSS allows rapid iteration and consistent design tokens. |
| **CI/CD** | GitHub Actions | Automated quality gates (typecheck, test, build) before merging. |
| **Security** | CodeQL Scanning | Proactive vulnerability detection in the CI pipeline. |
| **State** | Zustand | Lightweight and scalable state management without Redux boilerplate. |

## Repository Structure

```text
elitk-8/
├── .github/                  # CI/CD pipelines, CodeQL, and Governance
├── public/                   # Static assets (manifest, sw.js)
├── src/                      # Frontend Application (React 19)
│   ├── lib/                  # Utilities and core abstractions
│   ├── types/                # Shared TypeScript contracts
│   ├── knowledge/            # Static knowledge routing
│   └── App.tsx               # Root Component
├── tests/                    # Vitest unit and integration tests
├── tools/                    # Automated maintenance scripts
├── server.ts                 # Backend Express API entry point
└── Dockerfile                # Multi-stage production container
```

## Quickstart

### 1. Clone
```bash
git clone https://github.com/mohamedosamaai/elitk-8.git
cd elitk-8
```

### 2. Install
```bash
npm install
```

### 3. Configure
```bash
cp .env.example .env.local
# Populate with required API keys
```

### 4. Run
```bash
npm run dev
# Vite runs on http://localhost:5173
# Express API runs on http://localhost:3000
```

## Mock Mode Instructions

To run the application without live API keys (Mock Mode):
1. In `.env.local`, set `MOCK_MODE=true`
2. The Express API will bypass the Gemini network call and return deterministic mocked JSON responses.
3. Useful for UI/UX development and offline testing.

---

*Author: Mohamed Osama — [mohamedosamaai](https://github.com/mohamedosamaai)*  
*License: [MIT](LICENSE)*
