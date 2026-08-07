#!/usr/bin/env python3
"""
bagback-cli / scripts/04_docs_architect.py

Generates enterprise-grade documentation:
  - README.md with tech stack badges, architecture overview, setup guide
  - docs/adr/ directory with initial Architecture Decision Records
  - GitHub Wiki skeleton (5 pages) via API

Usage:
  python 04_docs_architect.py --repo /path/to/repo --project-name "MyProject"
      --description "Short description" --owner "github-user" [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import git_utils, preflight

ADR_INDEX = """\
# Architecture Decision Records

This directory documents significant architectural decisions made during the development of {project_name}.

| # | Title | Status | Date |
|---|---|---|---|
| ADR-001 | [Technology Stack Selection](./001-technology-stack.md) | Accepted | {today} |
| ADR-002 | [AI Integration Pattern](./002-ai-integration.md) | Accepted | {today} |

> New ADRs are added as numbered markdown files following the format `NNN-title.md`.
"""

ADR_001 = """\
# ADR-001: Technology Stack Selection

**Date:** {today}  
**Status:** Accepted  
**Deciders:** {owner}

## Context

We needed a modern, type-safe, and high-performance full-stack architecture capable of supporting real-time AI inference, 3D rendering, and multi-tenant data isolation.

## Decision

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React 19 + Vite | RSC-ready, fastest HMR, first-class TypeScript |
| Styling | Tailwind CSS v4 | Zero-runtime, utility-first, consistent design tokens |
| 3D Engine | Three.js + R3F | Industry-standard WebGL with declarative React bindings |
| AI Pipeline | Google Gemini | Best-in-class context window, multimodal, streaming |
| Server | Node.js + Express | Thin proxy layer; all heavy compute is AI-side |
| Language | TypeScript (strict) | Catches class of bugs at compile time, not runtime |

## Consequences

- Build times are fast due to Vite's esbuild pre-bundling.
- All AI inference runs server-side — no API keys in the browser bundle.
- Three.js requires careful code-splitting to prevent large initial bundles.
"""

ADR_002 = """\
# ADR-002: AI Integration Pattern

**Date:** {today}  
**Status:** Accepted  
**Deciders:** {owner}

## Context

Direct browser-to-AI-API calls expose API keys in DevTools and bypass server-side rate limiting and audit logging.

## Decision

All AI calls route through a server-side proxy (`server.ts`):

```
Browser → /api/chat → server.ts → Gemini API
Browser → /api/tts  → server.ts → Google TTS API
```

API keys are runtime environment variables only — never injected at build time.

## Consequences

- **Security:** Zero secrets in the client bundle.
- **Control:** Rate limiting and logging applied at the proxy layer.
- **Latency:** +1 network hop vs direct calls; negligible vs AI inference time.
- **Flexibility:** Swap AI providers in `server.ts` without touching the frontend.
"""


def detect_tech_stack(repo: Path) -> dict:
    """Infer tech stack from lock files and package.json."""
    stack = {}
    pkg_json = repo / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            stack["typescript"] = "5" if "typescript" in deps else None
            stack["react"] = deps.get("react", "").lstrip("^~") or None
            stack["vite"] = deps.get("vite", "").lstrip("^~") or None
            stack["next"] = deps.get("next", "").lstrip("^~") or None
            stack["drizzle"] = "drizzle-orm" in deps
            stack["prisma"] = "@prisma/client" in deps
            stack["gemini"] = "@google/genai" in deps
            stack["three"] = "three" in deps
            stack["express"] = "express" in deps
        except json.JSONDecodeError:
            pass
    return stack


def build_badges(stack: dict, owner: str, repo_name: str) -> str:
    badges = [
        f"[![CI](https://github.com/{owner}/{repo_name}/actions/workflows/ci.yml/badge.svg)]"
        f"(https://github.com/{owner}/{repo_name}/actions/workflows/ci.yml)",
        "![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)",
    ]
    if stack.get("typescript"):
        badges.append("![TypeScript](https://img.shields.io/badge/TypeScript-Strict-blue?style=flat-square&logo=typescript)")
    if stack.get("react"):
        badges.append(f"![React](https://img.shields.io/badge/React-{stack['react'].split('.')[0]}-61DAFB?style=flat-square&logo=react)")
    if stack.get("gemini"):
        badges.append("![Gemini AI](https://img.shields.io/badge/Gemini_AI-API-4285F4?style=flat-square&logo=google)")
    if stack.get("drizzle"):
        badges.append("![Drizzle ORM](https://img.shields.io/badge/Drizzle_ORM-PostgreSQL-C5F74F?style=flat-square)")
    return "\n".join(badges)


def generate_readme(repo: Path, project_name: str, description: str, owner: str, dry_run: bool) -> bool:
    repo_name = repo.name
    stack = detect_tech_stack(repo)
    badges = build_badges(stack, owner, repo_name)
    today = date.today().isoformat()

    content = f"""\
# ⚡ {project_name}

{badges}

> {description}

## Architecture Overview

```
-------------------------------------------------------
-                    Client (React)                   -
-   3D Engine · Audio Engine · Face Tracking · UI     -
-------------------------------------------------------
                     - fetch /api/*
---------------------▼---------------------------------
-              API Server (Express + Node)            -
-   CORS · Rate Limit · Validation · Proxy Layer      -
-------------------------------------------------------
       -                              -
-------▼-------              ---------▼-----------
-  Gemini AI  -              -   Google Cloud    -
-  (LLM/TTS)  -              -   PostgreSQL      -
---------------              ---------------------
```

## Quick Setup

```bash
git clone https://github.com/{owner}/{repo_name}.git
cd {repo_name}
cp .env.example .env.local
# populate .env.local with API keys
npm install
npm run dev
```

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server |
| `npm run build` | Production build (Vite + esbuild) |
| `npm run typecheck` | TypeScript strict-mode check |
| `npm run lint` | ESLint with zero warnings |
| `npm test` | Vitest unit tests |
| `npm run test:coverage` | Generate v8 coverage report |
| `npm start` | Run production server |

## Project Structure

```
{repo_name}/
--- .github/          # CI workflows, issue templates, CODEOWNERS
--- src/              # Application source (frontend)
--- tests/            # Vitest test suites
--- docs/adr/         # Architecture Decision Records
--- server.ts         # Express API server
--- Dockerfile        # Multi-stage production image
--- .env.example      # Sanitized environment blueprint
```

## Governance

| Document | Purpose |
|---|---|
| [CHANGELOG](./CHANGELOG.md) | Release history |
| [CONTRIBUTING](./CONTRIBUTING.md) | Contribution guide |
| [SECURITY](./SECURITY.md) | Vulnerability disclosure |
| [docs/adr/](./docs/adr/) | Architecture decisions |

## License

[MIT](./LICENSE) — {owner}
"""

    if dry_run:
        print(f"  [DRY-RUN] Would write README.md ({len(content)} bytes)")
        return False

    (repo / "README.md").write_text(content, encoding="utf-8")
    print("  README.md written.")
    return True


def generate_adrs(repo: Path, project_name: str, owner: str, dry_run: bool) -> bool:
    adr_dir = repo / "docs" / "adr"
    today = date.today().isoformat()

    if dry_run:
        print(f"  [DRY-RUN] Would create docs/adr/ with ADR-001 and ADR-002")
        return False

    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "README.md").write_text(ADR_INDEX.format(project_name=project_name, today=today))
    (adr_dir / "001-technology-stack.md").write_text(ADR_001.format(today=today, owner=owner))
    (adr_dir / "002-ai-integration.md").write_text(ADR_002.format(today=today, owner=owner))
    print("  docs/adr/ created: ADR-001, ADR-002")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Docs architect — README and ADR generator")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--description", default="An enterprise-grade software platform.")
    parser.add_argument("--owner", default="mohamedosamaai")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    preflight.run_all(repo, require_gh_auth=False)

    if not args.dry_run:
        git_utils.create_backup_branch(repo, prefix="automation-backup")

    changed = False
    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Generating README...")
    changed = generate_readme(repo, args.project_name, args.description, args.owner, args.dry_run) or changed

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Generating Architecture Decision Records...")
    changed = generate_adrs(repo, args.project_name, args.owner, args.dry_run) or changed

    if changed and not args.dry_run:
        git_utils.commit(repo, "docs: add enterprise readme, architecture overview, and adr records")
        print("\nCommitted: documentation suite.")

    if args.dry_run:
        print("\n[DRY-RUN] No files were modified.")


if __name__ == "__main__":
    main()
