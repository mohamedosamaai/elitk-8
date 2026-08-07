#!/usr/bin/env python3
"""
bagback-cli — Master Orchestrator

Central CLI that coordinates all 8 sub-scripts in the correct sequence.
Supports running individual scripts or full pipeline modes.

Usage:
  # Full pipeline — public showcase mode
  python bagback_cli.py setup --repo /path/to/repo --mode public --owner mohamedosamaai

  # Full pipeline — private/internal mode (skip showcase export)
  python bagback_cli.py setup --repo /path/to/repo --mode private --owner mohamedosamaai

  # Individual scripts
  python bagback_cli.py run humanize  --repo /path/to/repo [--dry-run]
  python bagback_cli.py run vault     --repo /path/to/repo [--dry-run]
  python bagback_cli.py run arch      --repo /path/to/repo [--dry-run]
  python bagback_cli.py run docs      --repo /path/to/repo --project-name "MyApp"
  python bagback_cli.py run pmo       --owner github-user --project-title "Board"
  python bagback_cli.py run ci        --repo /path/to/repo --owner github-user
  python bagback_cli.py run release   --repo /path/to/repo [--dry-run]
  python bagback_cli.py run showcase  --source /private --target /public [--push-to owner/repo]

  # Dry-run any step
  python bagback_cli.py run humanize --repo /path/to/repo --dry-run
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPTS_DIR = Path(__file__).parent / "scripts"
LIB_DIR     = Path(__file__).parent / "lib"

SCRIPT_MAP = {
    "humanize": SCRIPTS_DIR / "01_humanizer.py",
    "vault":    SCRIPTS_DIR / "02_vault_shield.py",
    "arch":     SCRIPTS_DIR / "03_clean_arch.py",
    "docs":     SCRIPTS_DIR / "04_docs_architect.py",
    "pmo":      SCRIPTS_DIR / "05_agile_pmo.py",
    "ci":       SCRIPTS_DIR / "06_devops_ci.py",
    "release":  SCRIPTS_DIR / "07_semantic_release.py",
    "showcase": SCRIPTS_DIR / "08_export_showcase.py",
}

PIPELINE_ORDER_PUBLIC  = ["vault", "humanize", "arch", "docs", "ci", "release", "showcase"]
PIPELINE_ORDER_PRIVATE = ["vault", "humanize", "arch", "docs", "ci", "release"]

BANNER = """
+------------------------------------------------------------------+
|       bagback-cli  *  Repository Automation Suite                |
|       github.com/mohamedosamaai  *  Bagback Digital              |
+------------------------------------------------------------------+
"""


def run_script(script: Path, extra_args: list[str]) -> int:
    cmd = [sys.executable, str(script)] + extra_args
    print(f"\n  ▶  {script.name}  {' '.join(extra_args)}")
    print("  " + "─" * 62)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n  [ABORT] {script.name} failed with code {result.returncode}.")
        print("          Fix the error above before continuing.")
    return result.returncode


def cmd_run(args: argparse.Namespace) -> int:
    script = SCRIPT_MAP.get(args.script)
    if script is None:
        print(f"Unknown script: '{args.script}'. Choose from: {list(SCRIPT_MAP)}")
        return 1
    return run_script(script, args.extra)


def cmd_setup(args: argparse.Namespace) -> int:
    mode = args.mode.lower()
    pipeline = PIPELINE_ORDER_PUBLIC if mode == "public" else PIPELINE_ORDER_PRIVATE

    print(BANNER)
    print(f"  Mode    : {mode}")
    print(f"  Repo    : {args.repo}")
    print(f"  Owner   : {args.owner}")
    print(f"  Pipeline: {' → '.join(pipeline)}")
    if args.dry_run:
        print("  ⚡ DRY-RUN — no changes will be made")
    print()

    dry_flag = ["--dry-run"] if args.dry_run else []

    step_args_map: dict[str, list[str]] = {
        "humanize": ["--repo", args.repo] + dry_flag,
        "vault":    ["--repo", args.repo] + dry_flag,
        "arch":     ["--repo", args.repo, "--owner", args.owner] + dry_flag,
        "docs":     ["--repo", args.repo, "--project-name", args.project_name or Path(args.repo).name,
                     "--owner", args.owner] + dry_flag,
        "pmo":      ["--owner", args.owner, "--project-title", args.project_name or Path(args.repo).name] + dry_flag,
        "ci":       ["--repo", args.repo, "--owner", args.owner] + dry_flag,
        "release":  ["--repo", args.repo] + dry_flag,
        "showcase": ["--source", args.repo, "--target", f"{args.repo}-showcase",
                     *(["--push-to", args.push_to] if args.push_to else [])] + dry_flag,
    }

    for step in pipeline:
        script = SCRIPT_MAP[step]
        extra = step_args_map.get(step, [])
        rc = run_script(script, extra)
        if rc != 0:
            print(f"\n  Pipeline stopped at step: {step}")
            return rc

    print("\n  ✅  Pipeline complete.")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    print(BANNER)
    print("  Available scripts:\n")
    for name, path in SCRIPT_MAP.items():
        print(f"    {name:<12} →  {path.name}")
    print()
    print("  Modes:  public (runs all 8)  |  private (skips showcase)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bagback-cli",
        description="Repository automation suite — Bagback Digital Solutions",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── setup ──────────────────────────────────────────────────────────────────
    setup_p = sub.add_parser("setup", help="Run full pipeline")
    setup_p.add_argument("--repo",         required=True,  help="Absolute path to the repo")
    setup_p.add_argument("--owner",        required=True,  help="GitHub username")
    setup_p.add_argument("--mode",         default="private", choices=["public", "private"])
    setup_p.add_argument("--project-name", help="Display name for docs and project board")
    setup_p.add_argument("--push-to",      help="owner/repo for public showcase push (mode=public)")
    setup_p.add_argument("--dry-run",      action="store_true")
    setup_p.set_defaults(func=cmd_setup)

    # ── run ────────────────────────────────────────────────────────────────────
    run_p = sub.add_parser("run", help="Run a single script")
    run_p.add_argument("script", choices=list(SCRIPT_MAP))
    run_p.add_argument("extra", nargs=argparse.REMAINDER, help="Arguments forwarded to the script")
    run_p.set_defaults(func=cmd_run)

    # ── list ───────────────────────────────────────────────────────────────────
    list_p = sub.add_parser("list", help="List available scripts")
    list_p.set_defaults(func=cmd_list)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
