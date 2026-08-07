# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `CHANGELOG.md`, `CODE_OF_CONDUCT.md` — full OSS governance suite
- `.dockerignore` — prevents secrets, `.git/`, and `node_modules/` from entering Docker image layers
- `vitest.config.ts` — test runner with v8 coverage and lcov reporting
- `tsconfig.node.json` — separate TypeScript configuration for Node/server files
- `.prettierrc` — enforced code formatting (single quotes, 100-char width, LF)
- `src/lib/ai/client.ts` — real Gemini REST client with `X-Goog-Api-Key` header pattern
- `src/types/agent.ts` — multi-agent pipeline type contracts
- `zustand` — state management dependency (was listed in README but absent from `package.json`)
- `cors` package with explicit allowed-origins list in `server.ts`

### Changed
- `vite.config.ts` — removed all API keys from client-side bundle; all AI calls now proxied through `server.ts`
- `server.ts` — CORS middleware added; `trust proxy` fixed from `true` to `1`; API keys moved from URL query params to `X-Goog-Api-Key` headers; `/api/health` no longer leaks key configuration; graceful shutdown on `SIGTERM`/`SIGINT`; `startServer()` has `.catch()` handler
- `Dockerfile` — removed `ARG`/`ENV` secrets pattern; all API keys are now runtime environment variables only
- `tsconfig.json` — added `strict: true` and all strict sub-flags (`noUnusedLocals`, `noImplicitReturns`, etc.)
- `package.json` — renamed from `resonance-8` to `elitk-8`; corrected `devDependencies` split; added `test`, `format`, `lint:fix` scripts
- `.github/workflows/ci.yml` — three-job pipeline (quality → test → build); actions pinned to SHA hashes; real `npm run build` replaces `echo`; `npm test` step added; build artifact upload
- `eslint.config.js` — replaced empty config with full ruleset (`@typescript-eslint`, `react-hooks`, `no-explicit-any: error`, `no-floating-promises`)
- `src/types/agent.ts` — renamed `AgentRole` to `AgentPipelineRole` to resolve naming collision with `src/types.ts`
- `README.md` — enterprise-grade documentation with accurate tech stack, project structure, and security section
- `SECURITY.md` — updated to remove incorrect "private repository" claim
- `.env.example` — expanded with `DATABASE_URL`, `GCP_PROJECT_ID`, `CLOUDFLARE_WORKER_URL`
- `.gitignore` — added `.env.production`, `.env.staging` to exclusion list

### Removed
- `tests/tts-legacy.test.cjs` — debug script that was not a test; replaced by real Vitest suite
- `process.env.GEMINI_API_KEY` from Vite `define` block (security fix)
- `process.env.LOGGER_API_KEY` from Vite `define` block (security fix)
- `ARG GEMINI_API_KEY` / `ARG GOOGLE_TTS_API_KEY` from Dockerfile (security fix)

### Fixed
- Rate limiting bypass via IP spoofing — `trust proxy: true` → `trust proxy: 1`
- API key exposure in server logs via URL query strings (`?key=...`) → `X-Goog-Api-Key` header
- Build was never verified in CI (was an `echo` statement)
- Tests were never run in CI

---

## [1.0.0] — 2026-08-06

### Added
- Initial production release
- Vite + React 19 frontend with Three.js GPGPU particle engine
- Express server with Pino logging, Zod validation, and rate limiting
- Google Gemini AI streaming integration
- MediaPipe FaceMesh real-time face tracking
- Web Audio API synthesis engine
- CI/CD pipeline via GitHub Actions
- Docker multi-stage production build
- GitHub Project Board with 8 custom views
- YAML issue templates (feature request, bug report)
