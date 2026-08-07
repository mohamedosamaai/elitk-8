#!/usr/bin/env python3
"""
bagback-cli / scripts/07_semantic_release.py

Semantic versioning and release management:
  - Reads git log since last tag
  - Bumps version per Conventional Commits spec
  - Updates CHANGELOG.md
  - Creates GitHub Release with release notes

Usage:
  python 07_semantic_release.py --repo /path/to/repo [--dry-run]
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib import git_utils, preflight

BREAKING_PREFIXES = {"feat!", "fix!", "refactor!", "chore!"}
FEAT_PREFIXES = {"feat"}
FIX_PREFIXES = {"fix", "perf"}

CHANGELOG_SECTION_MAP = {
    "feat":     "### Added",
    "fix":      "### Fixed",
    "perf":     "### Performance",
    "refactor": "### Changed",
    "docs":     "### Documentation",
    "ci":       "### CI/CD",
    "chore":    "### Maintenance",
    "security": "### Security",
}


def get_last_tag(repo: Path) -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True, cwd=repo
    )
    return result.stdout.strip() if result.returncode == 0 else None


def get_commits_since(repo: Path, ref: str | None) -> list[dict]:
    """Return list of commit dicts with keys: hash, subject, body."""
    range_spec = f"{ref}..HEAD" if ref else "HEAD"
    result = subprocess.run(
        ["git", "log", range_spec, "--pretty=format:%H|||%s|||%b---END---"],
        capture_output=True, text=True, cwd=repo
    )
    commits = []
    for block in result.stdout.split("---END---"):
        block = block.strip()
        if not block:
            continue
        parts = block.split("|||")
        if len(parts) >= 2:
            commits.append({"hash": parts[0].strip(), "subject": parts[1].strip(), "body": parts[2].strip() if len(parts) > 2 else ""})
    return commits


def parse_commit(subject: str) -> tuple[str, str]:
    """Returns (type, description) from a Conventional Commits subject."""
    m = re.match(r"^(\w+)(\([^)]+\))?(!)?:\s*(.+)$", subject)
    if not m:
        return "chore", subject
    commit_type = m.group(1) + ("!" if m.group(3) else "")
    desc = m.group(4)
    return commit_type, desc


def bump_version(current: str, bump: str) -> str:
    """Bump semver string. bump = 'major' | 'minor' | 'patch'."""
    parts = current.lstrip("v").split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2].split("-")[0])
    if bump == "major":
        return f"v{major + 1}.0.0"
    elif bump == "minor":
        return f"v{major}.{minor + 1}.0"
    else:
        return f"v{major}.{minor}.{patch + 1}"


def determine_bump(commits: list[dict]) -> str:
    for c in commits:
        t, _ = parse_commit(c["subject"])
        if t in BREAKING_PREFIXES or "BREAKING CHANGE" in c.get("body", ""):
            return "major"
    for c in commits:
        t, _ = parse_commit(c["subject"])
        if t in FEAT_PREFIXES:
            return "minor"
    return "patch"


def build_release_notes(commits: list[dict], new_version: str) -> str:
    today = date.today().isoformat()
    sections: dict[str, list[str]] = {}

    for c in commits:
        t, desc = parse_commit(c["subject"])
        base_type = t.rstrip("!")
        section = CHANGELOG_SECTION_MAP.get(base_type, "### Other")
        sections.setdefault(section, []).append(f"- {desc} ({c['hash'][:7]})")

    lines = [f"## [{new_version}] — {today}\n"]
    for header in CHANGELOG_SECTION_MAP.values():
        if header in sections:
            lines.append(header)
            lines.extend(sections[header])
            lines.append("")

    return "\n".join(lines)


def update_changelog(repo: Path, release_notes: str, dry_run: bool) -> None:
    changelog = repo / "CHANGELOG.md"
    if dry_run:
        print(f"  [DRY-RUN] Would prepend to CHANGELOG.md:\n{release_notes[:300]}...")
        return
    if changelog.exists():
        existing = changelog.read_text(encoding="utf-8")
        # Insert after the first heading
        lines = existing.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                insert_at = i
                break
        lines.insert(insert_at, release_notes + "\n---\n\n")
        changelog.write_text("".join(lines), encoding="utf-8")
    else:
        changelog.write_text(f"# Changelog\n\n{release_notes}", encoding="utf-8")
    print("  CHANGELOG.md updated.")


def create_git_tag(repo: Path, version: str, message: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would create tag: {version}")
        return
    subprocess.run(["git", "tag", "-a", version, "-m", message], cwd=repo, check=True)
    subprocess.run(["git", "push", "origin", version], cwd=repo, check=True)
    print(f"  Git tag created and pushed: {version}")


def create_github_release(repo: Path, slug: str, version: str, notes: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would create GitHub Release: {version}")
        return
    result = subprocess.run(
        ["gh", "release", "create", version,
         "--title", version,
         "--notes", notes,
         "--repo", slug],
        capture_output=True, text=True, cwd=repo
    )
    if result.returncode == 0:
        print(f"  GitHub Release created: {result.stdout.strip()}")
    else:
        print(f"  Warning: {result.stderr[:200]}")


def update_package_version(repo: Path, version: str, dry_run: bool) -> None:
    pkg = repo / "package.json"
    if not pkg.exists():
        return
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
        old = data.get("version", "0.0.0")
        data["version"] = version.lstrip("v")
        if dry_run:
            print(f"  [DRY-RUN] Would update package.json: {old} → {version.lstrip('v')}")
        else:
            pkg.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(f"  package.json: {old} → {version.lstrip('v')}")
    except json.JSONDecodeError:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic release manager")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    preflight.run_all(repo, require_gh_auth=True)

    last_tag = get_last_tag(repo)
    print(f"\n  Last tag: {last_tag or '(none — full history)'}")

    commits = get_commits_since(repo, last_tag)
    print(f"  Commits since last tag: {len(commits)}")

    if not commits:
        print("  Nothing to release.")
        return

    bump = determine_bump(commits)
    current = last_tag or "v0.0.0"
    new_version = bump_version(current, bump)
    print(f"  Bump type: {bump} → {new_version}")

    release_notes = build_release_notes(commits, new_version)
    print(f"\n  Release notes preview:\n{release_notes[:400]}\n")

    if not args.dry_run:
        git_utils.create_backup_branch(repo, prefix="pre-release-backup")

    update_package_version(repo, new_version, args.dry_run)
    update_changelog(repo, release_notes, args.dry_run)

    if not args.dry_run:
        git_utils.commit(repo, f"chore(release): {new_version}")
        git_utils.push(repo)

    slug = git_utils.get_repo_slug(repo)
    create_git_tag(repo, new_version, f"Release {new_version}", args.dry_run)
    create_github_release(repo, slug, new_version, release_notes, args.dry_run)

    if args.dry_run:
        print("\n[DRY-RUN] No changes made.")
    else:
        print(f"\n  Released: {new_version}")


if __name__ == "__main__":
    main()
