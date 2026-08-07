#!/usr/bin/env python3
"""
bagback-cli / scripts/02_vault_shield.py

Zero-Trust security hardening:
  - Purges live secrets from .env files, replaces with .env.example placeholders
  - Plants enterprise-grade .gitignore
  - Installs Husky + lint-staged pre-commit hooks
  - Writes gitleaks config to block future secret commits

Usage:
  python 02_vault_shield.py --repo /path/to/repo [--dry-run]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import git_utils, preflight

# -- Secret patterns — values that look like real credentials ------------------
SECRET_VALUE_PATTERN = re.compile(
    r"^([A-Z_]+)\s*=\s*(?!your_|<|#|\s*$)(.+)$"
)

GITIGNORE_ENTERPRISE = """\
# -- Environment & secrets -----------------------------------------------------
.env
.env.local
.env.*.local
.env.production
.env.staging
.env.test
!.env.example

# -- Build output --------------------------------------------------------------
dist/
build/
out/
.next/
.vite/
*.tsbuildinfo

# -- Dependencies --------------------------------------------------------------
node_modules/
.pnp
.pnp.js

# -- Test & coverage -----------------------------------------------------------
coverage/
.nyc_output/
playwright-report/
test-results/

# -- Logs ----------------------------------------------------------------------
*.log
npm-debug.log*
yarn-debug.log*
pino.log*
logs/

# -- Editor artifacts ----------------------------------------------------------
.DS_Store
Thumbs.db
*.swp
*.swo
.idea/
.vscode/settings.json
!.vscode/extensions.json

# -- OS ------------------------------------------------------------------------
Desktop.ini
ehthumbs.db

# -- Deployment ----------------------------------------------------------------
.vercel
.netlify
.wrangler/

# -- Python --------------------------------------------------------------------
__pycache__/
*.py[cod]
.venv/
*.egg-info/
"""

GITLEAKS_CONFIG = """\
title = "Bagback Gitleaks Config"

[extend]
useDefault = true

[[rules]]
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey|api[_-]?secret)\\s*[=:]+\\s*['\"]?[a-zA-Z0-9_\\-]{20,}['\"]?'''
tags = ["key", "API"]

[[rules]]
description = "Google API Key"
regex = '''AIza[0-9A-Za-z\\-_]{35}'''
tags = ["key", "Google"]

[allowlist]
description = "Allow placeholder patterns"
regexes = [
    '''your_.*_here''',
    '''<[A-Z_]+>''',
    '''placeholder''',
]
"""

HUSKY_PRE_COMMIT = """\
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
"""

LINT_STAGED_CONFIG = """\
{
  "*.{ts,tsx,js,jsx}": ["eslint --fix --max-warnings 0", "prettier --write"],
  "*.{json,md,yml,yaml}": ["prettier --write"],
  "*.{ts,tsx}": ["bash -c 'tsc --noEmit'"]
}
"""


def sanitize_env_file(env_path: Path, dry_run: bool) -> list[str]:
    """Strip real values from an .env file, return list of changes."""
    if not env_path.exists():
        return []

    lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    changes = []
    cleaned = []

    for line in lines:
        m = SECRET_VALUE_PATTERN.match(line.rstrip())
        if m:
            key = m.group(1)
            changes.append(f"  Cleared: {key}=***")
            cleaned.append(f"{key}=your_{key.lower()}_here\n")
        else:
            cleaned.append(line)

    if changes and not dry_run:
        env_path.write_text("".join(cleaned), encoding="utf-8")

    return changes


def harden_repo(repo: Path, dry_run: bool) -> None:
    label = "[DRY-RUN] " if dry_run else ""
    changed = False

    # 1. Sanitize all .env* files (except .env.example)
    print(f"\n{label}Scanning for live secrets in .env files...")
    for env_file in repo.glob(".env*"):
        if env_file.name == ".env.example":
            continue
        changes = sanitize_env_file(env_file, dry_run)
        if changes:
            print(f"  {label}Processing {env_file.name}:")
            for c in changes:
                print(f"  {c}")
            changed = True
        else:
            print(f"  {env_file.name}: no real secrets found.")

    # 2. Plant .gitignore
    print(f"\n{label}Installing enterprise .gitignore...")
    gitignore = repo / ".gitignore"
    if dry_run:
        print(f"  Would write {len(GITIGNORE_ENTERPRISE.splitlines())} lines to .gitignore")
    else:
        gitignore.write_text(GITIGNORE_ENTERPRISE, encoding="utf-8")
        changed = True
        print("  .gitignore written.")

    # 3. Gitleaks config
    print(f"\n{label}Installing gitleaks secret scanner config...")
    gl_config = repo / ".gitleaks.toml"
    if dry_run:
        print(f"  Would write .gitleaks.toml ({len(GITLEAKS_CONFIG)} bytes)")
    else:
        gl_config.write_text(GITLEAKS_CONFIG, encoding="utf-8")
        changed = True
        print("  .gitleaks.toml written.")

    # 4. Husky + lint-staged (only for npm projects)
    pkg = repo / "package.json"
    if pkg.exists():
        print(f"\n{label}Installing Husky pre-commit hooks...")
        if dry_run:
            print("  Would run: npm install --save-dev husky lint-staged")
            print("  Would create: .husky/pre-commit")
            print("  Would write: .lintstagedrc.json")
        else:
            import subprocess
            subprocess.run(
                ["npm", "install", "--save-dev", "husky", "lint-staged"],
                cwd=repo, check=False, capture_output=True
            )
            subprocess.run(
                ["npx", "husky", "init"],
                cwd=repo, check=False, capture_output=True
            )
            husky_dir = repo / ".husky"
            husky_dir.mkdir(exist_ok=True)
            (husky_dir / "pre-commit").write_text(HUSKY_PRE_COMMIT, encoding="utf-8")
            (repo / ".lintstagedrc.json").write_text(LINT_STAGED_CONFIG, encoding="utf-8")
            changed = True
            print("  Husky + lint-staged installed.")

    if changed and not dry_run:
        git_utils.commit(
            repo,
            "security: apply zero-trust secret hygiene, gitignore, gitleaks config, and pre-commit hooks",
        )
        print("\nCommitted: security hardening.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Vault Shield — zero-trust security hardening")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    preflight.run_all(repo, require_gh_auth=False)

    if not args.dry_run:
        git_utils.create_backup_branch(repo, prefix="automation-backup")

    harden_repo(repo, dry_run=args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN] No files were modified.")


if __name__ == "__main__":
    main()
