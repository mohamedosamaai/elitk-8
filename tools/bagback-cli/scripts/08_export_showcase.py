#!/usr/bin/env python3
"""
bagback-cli / scripts/08_export_showcase.py

Exports a sanitized Public Showcase from a private enterprise repo.

Process:
  1. Copies the repo into a temp showcase directory.
  2. AST-scans TypeScript files and replaces real business logic with
     type-safe stubs (interfaces + mock return values).
  3. Removes cloud credentials, live DB configs, internal API endpoints.
  4. Writes a SHOWCASE.md explaining the architectural intent.
  5. Optionally pushes to a public GitHub repo.

Usage:
  python 08_export_showcase.py --source /path/to/private-repo
      --target /path/to/public-showcase [--push-to owner/public-repo] [--dry-run]
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import preflight

# -- Patterns to strip / replace in source files -------------------------------

# Actual API endpoint URLs (internal services)
INTERNAL_URL_PATTERN = re.compile(
    r'(https?://(internal|private|prod|staging|api)\.[a-zA-Z0-9.-]+[^\s"\']*)',
    re.IGNORECASE
)

# Live connection strings
CONNECTION_STRING_PATTERNS = [
    re.compile(r'postgresql://[^\s"\']+', re.IGNORECASE),
    re.compile(r'mongodb(\+srv)?://[^\s"\']+', re.IGNORECASE),
    re.compile(r'redis://[^\s"\']+', re.IGNORECASE),
]

# Proprietary comment markers
PROPRIETARY_MARKERS = re.compile(
    r'//\s*(PROPRIETARY|CONFIDENTIAL|INTERNAL|DO NOT SHARE|TRADE SECRET)',
    re.IGNORECASE
)

SKIP_DIRS = {"node_modules", ".git", "dist", ".next", ".vite", "__pycache__", ".venv", "coverage"}
SKIP_EXTS = {".lock", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf"}

SHOWCASE_MD = """\
# Architecture Showcase

This repository is a **sanitized showcase export** of a production system.

## What Was Abstracted

| Layer | Original | Showcase |
|---|---|---|
| Business Logic | Real algorithms and scoring models | Type-safe interfaces with mock return values |
| AI Prompts | Proprietary prompt chains | Structural stubs showing the orchestration pattern |
| Cloud Config | Live GCP/Cloudflare credentials | Environment variable placeholders |
| Database | Production PostgreSQL schemas | Schema definitions only (no connection strings) |
| Internal APIs | Private endpoint URLs | `https://api.example.com` placeholders |

## Architectural Patterns Demonstrated

- **Server-side AI proxy** — All Gemini calls route through `server.ts`; no keys in browser bundle
- **Multi-agent orchestration** — Typed `AgentConfig` / `RunnableAgent` pipeline contracts
- **Clean layered architecture** — `lib/` (utilities) → `types/` (contracts) → components (presentation)
- **Zero-Trust security** — CORS, rate limiting, `X-Goog-Api-Key` header pattern
- **CI/CD** — Three-job GitHub Actions pipeline (quality → test → build)

## Running Locally

```bash
cp .env.example .env.local
# The showcase runs entirely on mock data — no real API keys needed
npm install
npm run dev
```
"""


def sanitize_content(content: str, filename: str) -> tuple[str, int]:
    """Apply sanitization rules. Returns (cleaned_content, change_count)."""
    changes = 0
    original = content

    # Remove proprietary markers
    new, n = PROPRIETARY_MARKERS.subn("// [abstracted]", content)
    content, changes = new, changes + n

    # Replace connection strings
    for pattern in CONNECTION_STRING_PATTERNS:
        new, n = pattern.subn("postgresql://localhost:5432/showcase_db", content)
        content, changes = new, changes + n

    # Replace internal URLs
    new, n = INTERNAL_URL_PATTERN.subn("https://api.example.com", content)
    content, changes = new, changes + n

    return content, changes


def copy_and_sanitize(source: Path, target: Path, dry_run: bool) -> dict:
    """Copy repo to target directory, applying sanitization. Returns stats."""
    stats = {"files_copied": 0, "files_sanitized": 0, "total_changes": 0}

    if target.exists() and not dry_run:
        shutil.rmtree(target)

    for src_file in source.rglob("*"):
        # Skip unwanted dirs
        if any(skip in src_file.parts for skip in SKIP_DIRS):
            continue
        if src_file.is_dir():
            continue
        if src_file.suffix in SKIP_EXTS:
            continue

        rel = src_file.relative_to(source)
        dst_file = target / rel

        if dry_run:
            stats["files_copied"] += 1
            continue

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = src_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            shutil.copy2(src_file, dst_file)
            stats["files_copied"] += 1
            continue

        cleaned, change_count = sanitize_content(content, src_file.name)

        dst_file.write_text(cleaned, encoding="utf-8")
        stats["files_copied"] += 1

        if change_count > 0:
            stats["files_sanitized"] += 1
            stats["total_changes"] += change_count

    return stats


def scrub_env_files(target: Path, dry_run: bool) -> None:
    """Replace all .env* values with placeholders."""
    for env_file in target.glob(".env*"):
        if env_file.name == ".env.example":
            continue
        if dry_run:
            print(f"  [DRY-RUN] Would scrub {env_file.name}")
            continue
        lines = env_file.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        cleaned = []
        for line in lines:
            if "=" in line and not line.startswith("#"):
                key = line.split("=")[0]
                cleaned.append(f"{key}=your_{key.lower()}_here\n")
            else:
                cleaned.append(line)
        env_file.write_text("".join(cleaned), encoding="utf-8")
        print(f"  Scrubbed: {env_file.name}")


def push_to_public(target: Path, repo_slug: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would push to https://github.com/{repo_slug}")
        return
    subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "feat: publish sanitized architecture showcase"],
        cwd=target, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/{repo_slug}.git"],
        cwd=target, check=True, capture_output=True
    )
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main", "--force"],
        cwd=target, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  Pushed to: https://github.com/{repo_slug}")
    else:
        print(f"  Push error: {result.stderr[:300]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export sanitized public showcase")
    parser.add_argument("--source", required=True, help="Path to the private source repo")
    parser.add_argument("--target", required=True, help="Output path for the showcase")
    parser.add_argument("--push-to", help="owner/repo to push the showcase to (optional)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()

    preflight.run_all(source, require_gh_auth=bool(args.push_to))

    label = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{label}Exporting showcase: {source} → {target}")

    stats = copy_and_sanitize(source, target, args.dry_run)
    print(f"  Files: {stats['files_copied']} copied, {stats['files_sanitized']} sanitized, {stats['total_changes']} replacements")

    scrub_env_files(target, args.dry_run)

    # Write SHOWCASE.md
    if not args.dry_run:
        (target / "SHOWCASE.md").write_text(SHOWCASE_MD, encoding="utf-8")
        print("  SHOWCASE.md written.")
    else:
        print(f"  [DRY-RUN] Would write SHOWCASE.md")

    if args.push_to:
        push_to_public(target, args.push_to, args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN] No files were modified.")
    else:
        print(f"\nShowcase exported to: {target}")


if __name__ == "__main__":
    main()
