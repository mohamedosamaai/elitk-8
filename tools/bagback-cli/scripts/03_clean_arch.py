#!/usr/bin/env python3
"""
bagback-cli / scripts/03_clean_arch.py

Enforces Clean Architecture folder conventions, runs Prettier + ESLint,
plants .nvmrc and CODEOWNERS.

Does NOT move files automatically (too risky without AST analysis of all
imports). Instead generates a migration report with the exact shell commands
to execute.

Usage:
  python 03_clean_arch.py --repo /path/to/repo [--dry-run]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import git_utils, preflight

NVMRC_CONTENT = "22\n"

CODEOWNERS_TEMPLATE = """\
# CODEOWNERS — code ownership and review assignments.
# Format: <pattern> @<github-username>
#
# Every PR that modifies a matched path requires approval from the listed owner(s).

# Global fallback
*                          @{owner}

# Infrastructure & CI
.github/                   @{owner}
Dockerfile                 @{owner}
docker-compose*.yml        @{owner}

# Application source
src/lib/                   @{owner}
src/types/                 @{owner}

# Database & data layer (lock down schema changes)
src/db/                    @{owner}
drizzle/                   @{owner}

# Documentation
*.md                       @{owner}
docs/                      @{owner}
"""

ARCH_LAYERS = {
    "src/app": "Next.js App Router pages, layouts, loading, error boundaries",
    "src/domain": "Business entities, value objects, domain services",
    "src/infrastructure": "DB adapters, external API clients, cloud integrations",
    "src/presentation": "UI components, hooks, state management",
    "src/lib": "Shared utilities, AI client, config",
}


def get_package_manager(repo: Path) -> str:
    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (repo / "yarn.lock").exists():
        return "yarn"
    return "npm"


def run_formatter(repo: Path, dry_run: bool) -> None:
    pkg = repo / "package.json"
    if not pkg.exists():
        print("  No package.json found — skipping Prettier.")
        return

    pm = get_package_manager(repo)

    if dry_run:
        print(f"  [DRY-RUN] Would run: {pm} exec prettier --check .")
        return

    result = subprocess.run(
        [pm, "exec", "prettier", "--write", "src/", "tests/", "--ignore-unknown"],
        cwd=repo, capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Prettier: formatting applied.")
    else:
        print(f"  Prettier warning: {result.stderr[:300]}")


def run_linter(repo: Path, dry_run: bool) -> None:
    pkg = repo / "package.json"
    if not pkg.exists():
        return

    pm = get_package_manager(repo)

    if dry_run:
        print(f"  [DRY-RUN] Would run: {pm} exec eslint . --fix --max-warnings 0")
        return

    result = subprocess.run(
        [pm, "exec", "eslint", ".", "--fix", "--max-warnings", "0"],
        cwd=repo, capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  ESLint: all issues fixed.")
    else:
        print(f"  ESLint: {result.returncode} issue(s) remaining (manual fix required).")
        if result.stdout:
            print(f"  {result.stdout[:500]}")


def plant_nvmrc(repo: Path, dry_run: bool) -> bool:
    nvmrc = repo / ".nvmrc"
    if dry_run:
        print(f"  [DRY-RUN] Would write .nvmrc: Node.js {NVMRC_CONTENT.strip()}")
        return False
    nvmrc.write_text(NVMRC_CONTENT, encoding="utf-8")
    print(f"  .nvmrc written: Node.js {NVMRC_CONTENT.strip()}")
    return True


def plant_codeowners(repo: Path, owner: str, dry_run: bool) -> bool:
    gh_dir = repo / ".github"
    gh_dir.mkdir(exist_ok=True)
    target = gh_dir / "CODEOWNERS"
    content = CODEOWNERS_TEMPLATE.format(owner=owner)

    if dry_run:
        print(f"  [DRY-RUN] Would write .github/CODEOWNERS ({len(content)} bytes, owner={owner})")
        return False

    target.write_text(content, encoding="utf-8")
    print(f"  CODEOWNERS written.")
    return True


def generate_arch_migration_report(repo: Path) -> None:
    print("\n  ----------------------------------------------------------------")
    print("  -  Architecture Migration Report — Execute manually            -")
    print("  ----------------------------------------------------------------")
    print()
    print("  Target Clean Architecture structure:")
    for path, purpose in ARCH_LAYERS.items():
        exists = "✓" if (repo / path).exists() else "○"
        print(f"  {exists}  {path}/  — {purpose}")
    print()
    print("  To create missing directories:")
    for path in ARCH_LAYERS:
        if not (repo / path).exists():
            print(f"    mkdir -p {path}")
    print()
    print("  ⚠  Import paths must be updated after moving files.")
    print("     Use your IDE's 'Move Symbol' / 'Update Imports' refactoring tools.")
    print("     Or run: npx ts-morph-tools migrate-imports --from src/ --to src/domain/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean Architecture enforcer")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--owner", default="mohamedosamaai", help="GitHub username for CODEOWNERS")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    preflight.run_all(repo, require_gh_auth=False)

    if not args.dry_run:
        git_utils.create_backup_branch(repo, prefix="automation-backup")

    label = "\n[DRY-RUN] " if args.dry_run else "\n"
    print(f"{label}Running formatter and linter...")
    run_formatter(repo, args.dry_run)
    run_linter(repo, args.dry_run)

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Planting .nvmrc and CODEOWNERS...")
    changed = plant_nvmrc(repo, args.dry_run)
    changed = plant_codeowners(repo, args.owner, args.dry_run) or changed

    if changed and not args.dry_run:
        git_utils.commit(repo, "chore: add .nvmrc, codeowners, and enforce code formatting standards")
        print("\nCommitted: clean architecture tooling.")

    generate_arch_migration_report(repo)

    if args.dry_run:
        print("\n[DRY-RUN] No files were modified.")


if __name__ == "__main__":
    main()
