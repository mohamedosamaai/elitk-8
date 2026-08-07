#!/usr/bin/env python3
"""
bagback-cli / lib/git_utils.py
Git and GitHub CLI helper utilities.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        print(result.stderr or result.stdout)
        sys.exit(1)
    return result


def current_branch(repo: Path) -> str:
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo).stdout.strip()


def create_backup_branch(repo: Path, prefix: str = "automation-backup") -> str:
    """
    Create a timestamped backup branch from the current HEAD.
    Returns the branch name.
    """
    stamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M")
    branch = f"{prefix}-{stamp}"
    run(["git", "checkout", "-b", branch], cwd=repo)
    run(["git", "push", "origin", branch], cwd=repo)
    run(["git", "checkout", "-"], cwd=repo)
    print(f"  Backup branch created: {branch}")
    return branch


def get_remote_url(repo: Path) -> str:
    return run(["git", "remote", "get-url", "origin"], cwd=repo).stdout.strip()


def get_repo_slug(repo: Path) -> str:
    """Returns 'owner/repo' from the origin remote URL."""
    url = get_remote_url(repo)
    url = url.removeprefix("https://github.com/").removeprefix("git@github.com:")
    return url.removesuffix(".git")


def commit(repo: Path, message: str, allow_empty: bool = False) -> None:
    cmd = ["git", "commit", "-m", message]
    if allow_empty:
        cmd.append("--allow-empty")
    result = run(["git", "status", "--porcelain"], cwd=repo)
    if not result.stdout.strip() and not allow_empty:
        print("  Nothing to commit — working tree clean.")
        return
    run(["git", "add", "-A"], cwd=repo)
    run(cmd, cwd=repo)


def push(repo: Path, branch: str | None = None) -> None:
    branch = branch or current_branch(repo)
    run(["git", "push", "origin", branch], cwd=repo)
