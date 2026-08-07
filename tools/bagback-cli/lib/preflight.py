#!/usr/bin/env python3
"""
bagback-cli / lib/preflight.py
Pre-flight safety checks run before any script modifies the repository.
"""
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def check_git_repo(path: Path) -> None:
    result = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
    if result.returncode != 0:
        print(f"[ABORT] {path} is not a git repository.")
        sys.exit(1)


def check_clean_working_tree(path: Path) -> None:
    result = _run(["git", "status", "--porcelain"], cwd=path)
    if result.stdout.strip():
        print("[ABORT] Uncommitted changes detected. Commit or stash before running bagback-cli.")
        print(result.stdout)
        sys.exit(1)


def check_gh_auth() -> None:
    result = _run(["gh", "auth", "status"])
    if result.returncode != 0:
        print("[ABORT] GitHub CLI not authenticated. Run: gh auth login")
        sys.exit(1)


def check_python_version() -> None:
    if sys.version_info < (3, 11):
        print(f"[ABORT] Python 3.11+ required. Found: {sys.version}")
        sys.exit(1)


def check_node_available() -> None:
    result = _run(["node", "--version"])
    if result.returncode != 0:
        print("[ABORT] Node.js is not installed or not on PATH.")
        sys.exit(1)


def run_all(repo_path: Path, require_gh_auth: bool = True) -> None:
    """Run all pre-flight checks. Exits with code 1 on first failure."""
    print("  Running pre-flight checks...")
    check_python_version()
    check_git_repo(repo_path)
    check_clean_working_tree(repo_path)
    if require_gh_auth:
        check_gh_auth()
    check_node_available()
    print("  Pre-flight checks passed.\n")
