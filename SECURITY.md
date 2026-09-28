# Security Policy

## Supported Versions

| Version | Status |
|---|---|
| `1.x` (current) | ✅ Actively maintained |
| `< 1.0` | ❌ No longer supported |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately by emailing: **im@mohamedosama.me**

Include in your report:
- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- The affected component or file path
- Any proof-of-concept code (if applicable)

We will acknowledge receipt within **72 hours** and provide a remediation timeline within **7 business days**.

## Secrets & Key Management

- All API keys are server-side only — the Vite client bundle contains no credentials
- Keys are injected at runtime via environment variables, never baked into build output or Docker image layers
- Use `.env.local` for local development (excluded from version control via `.gitignore`)
- Production secrets are managed via the hosting platform's environment configuration (Google Firebase environment variables, or Docker environment injection for self-hosted deployments)
- Never commit `.env`, `.env.local`, or any file containing real API keys to version control

## Deployment Security

This project is hosted on **Google Firebase Hosting** with the Express backend served as a containerized service.

- Frontend static assets are served via Firebase Hosting CDN
- The Express API server (`server.ts`) handles all requests requiring API keys
- CORS is restricted to the production domain (`8.elitk.com`) in production mode
- Rate limiting is enforced: 100 requests/15 min for API endpoints, 20 requests/min for TTS

## Known Security Assumptions

- The server trusts exactly one reverse proxy hop (`trust proxy: 1`). If deployed behind multiple proxy layers, adjust accordingly.
- CORS is restricted to `APP_URL` in production. Ensure this variable is set correctly in your deployment environment.
- Rate limiting is per-IP. Shared NAT environments may trigger limits earlier than expected.

## Dependency Auditing

Run `npm audit` before any production release. Dependabot is configured to submit automated PRs for vulnerable dependencies.
