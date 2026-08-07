# Contributing to ELITK-8

Thanks for taking the time to contribute. This document covers the workflow, commit conventions, and quality requirements for all contributions.

## Development Setup

```bash
# 1. Clone and install
git clone https://github.com/mohamedosamaai/elitk-8.git
cd elitk-8
npm install

# 2. Configure environment
cp .env.example .env.local
# Set GEMINI_API_KEY and GOOGLE_TTS_API_KEY in .env.local

# 3. Start development server
npm run dev        # Vite frontend + Express API server

# 4. Run checks before committing
npm run typecheck  # TypeScript strict mode
npm run lint       # ESLint with zero warnings allowed
npm run format     # Prettier formatting
npm test           # Vitest unit tests
```

## Branch Workflow

| Branch | Purpose |
|---|---|
| `main` | Production-ready code only. Direct pushes blocked. |
| `dev` | Integration branch. All features merge here first. |
| `feat/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation only |
| `refactor/<name>` | Code restructure, no behavior change |

Create branches from `dev`. Submit PRs targeting `dev`. `dev` → `main` via a reviewed PR.

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`, `perf`

**Examples:**
```
feat(audio): add Arabic TTS voice selection
fix(server): move API keys from URL params to X-Goog-Api-Key header
docs(readme): update architecture section with new module structure
ci: pin GitHub Actions to SHA hashes
```

Rules:
- Subject line ≤ 72 characters
- Imperative mood ("add" not "added")
- No AI-generated footers or attribution comments in commit messages
- Reference issues with `Closes #<number>` in the commit body or PR description

## Pull Request Requirements

- [ ] Targets `dev` branch (not `main`)
- [ ] CI passes (all three jobs: quality, test, build)
- [ ] New logic includes corresponding tests in `tests/`
- [ ] `npm run typecheck` passes with zero errors
- [ ] `npm run lint` passes with zero warnings
- [ ] No secrets, API keys, or hardcoded credentials

## Code Style

- **TypeScript strict mode** is enforced — no `any` types
- **Prettier** handles all formatting (run `npm run format`)
- **Import order**: React → Three.js → Google AI → project modules → relative imports
- All visible user-facing text must use the i18n `t()` function — no hardcoded strings in JSX

## Security

Do not open public issues for security vulnerabilities. See [SECURITY.md](./SECURITY.md) for the responsible disclosure process.
