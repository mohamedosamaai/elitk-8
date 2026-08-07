#!/usr/bin/env python3
"""
bagback-cli / scripts/06_devops_ci.py

CI/CD hardening:
  - Audits .github/workflows/ for broken or billing-triggering workflows
  - Writes optimized ci.yml (typecheck → test → build)
  - Plants dependabot.yml with grouping
  - Ensures CI badge in README reflects the real workflow

Usage:
  python 06_devops_ci.py --repo /path/to/repo --owner github-user [--dry-run]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import git_utils, preflight

CI_YML = """\
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  quality:
    name: Type-check & Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af # v4.1.0
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run typecheck
      - run: npm run lint

  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: quality
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af # v4.1.0
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test

  build:
    name: Build Verification
    runs-on: ubuntu-latest
    needs: quality
    env:
      NODE_ENV: production
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af # v4.1.0
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@65c4c4a1ddee5b72f698fdd19549f0f0fb45cf08 # v4.6.0
        with:
          name: dist
          path: dist/
          retention-days: 7
"""

DEPENDABOT_YML = """\
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      development-dependencies:
        dependency-type: "development"
        update-types: ["minor", "patch"]
      production-dependencies:
        dependency-type: "production"
        update-types: ["minor", "patch"]
    open-pull-requests-limit: 10
    labels: ["dependencies", "automated"]
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels: ["dependencies", "ci", "automated"]
"""

KNOWN_BILLING_HEAVY_WORKFLOWS = [
    "codeql",
    "code-scanning",
    "dependency-review",
    "advanced-security",
    "security-and-quality",
]


def audit_workflows(workflows_dir: Path) -> list[str]:
    """Returns list of workflow files that may cause billing issues."""
    risky = []
    if not workflows_dir.exists():
        return risky
    for wf in workflows_dir.glob("*.yml"):
        content = wf.read_text(encoding="utf-8", errors="ignore").lower()
        for pattern in KNOWN_BILLING_HEAVY_WORKFLOWS:
            if pattern in content:
                risky.append(str(wf.name))
                break
    return risky


def setup_ci(repo: Path, owner: str, dry_run: bool) -> None:
    wf_dir = repo / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)

    # 1. Audit existing workflows
    print("\n  Auditing existing workflows...")
    risky = audit_workflows(wf_dir)
    if risky:
        print(f"  ⚠  Potential billing-heavy workflows found: {', '.join(risky)}")
        print("     These require GitHub Advanced Security (paid). Consider disabling.")
    else:
        print("  No billing-heavy workflows detected.")

    # 2. Write ci.yml
    ci_path = wf_dir / "ci.yml"
    if dry_run:
        print(f"\n  [DRY-RUN] Would write .github/workflows/ci.yml ({len(CI_YML)} bytes)")
    else:
        ci_path.write_text(CI_YML, encoding="utf-8")
        print(f"\n  ci.yml written.")

    # 3. Write dependabot.yml
    dep_path = repo / ".github" / "dependabot.yml"
    if dry_run:
        print(f"  [DRY-RUN] Would write .github/dependabot.yml")
    else:
        dep_path.write_text(DEPENDABOT_YML, encoding="utf-8")
        print("  dependabot.yml written.")

    # 4. Update README CI badge
    readme = repo / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8")
        badge = f"[![CI](https://github.com/{owner}/{repo.name}/actions/workflows/ci.yml/badge.svg)](https://github.com/{owner}/{repo.name}/actions/workflows/ci.yml)"
        if "ci.yml/badge.svg" not in content:
            if dry_run:
                print("  [DRY-RUN] Would add CI badge to README.md")
            else:
                # Insert badge after the first heading
                lines = content.splitlines(keepends=True)
                for i, line in enumerate(lines):
                    if line.startswith("# "):
                        lines.insert(i + 1, f"\n{badge}\n")
                        break
                readme.write_text("".join(lines), encoding="utf-8")
                print("  README.md: CI badge added.")

    if not dry_run:
        git_utils.commit(repo, "ci: optimize pipeline with three-job quality/test/build strategy and sha-pinned actions")
        print("\nCommitted: CI hardening.")


def main() -> None:
    parser = argparse.ArgumentParser(description="DevOps CI/CD setup")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    preflight.run_all(repo, require_gh_auth=False)

    if not args.dry_run:
        git_utils.create_backup_branch(repo, prefix="automation-backup")

    setup_ci(repo, args.owner, args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN] No files were modified.")


if __name__ == "__main__":
    main()
