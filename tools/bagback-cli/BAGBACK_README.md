# bagback-cli

> Repository automation suite by Bagback Digital Solutions.
> Transforms any repo into enterprise-grade quality in minutes.

## Requirements

- Python 3.11+
- Node.js 22+
- GitHub CLI (`gh`) — authenticated via `gh auth login`
- Git

## Installation

```bash
git clone https://github.com/mohamedosamaai/bagback-cli.git
cd bagback-cli
# No pip install needed — pure stdlib + subprocess
python bagback_cli.py list
```

## Quick Start

```bash
# Dry-run the full pipeline first — see exactly what will change
python bagback_cli.py setup \
  --repo /path/to/your-repo \
  --owner mohamedosamaai \
  --mode private \
  --dry-run

# Apply (private mode — no showcase export)
python bagback_cli.py setup \
  --repo /path/to/your-repo \
  --owner mohamedosamaai \
  --mode private

# Public mode — also exports a sanitized showcase
python bagback_cli.py setup \
  --repo /path/to/your-repo \
  --owner mohamedosamaai \
  --mode public \
  --push-to mohamedosamaai/your-repo-showcase
```

## Run Individual Scripts

```bash
python bagback_cli.py run humanize --repo /path/to/repo --dry-run
python bagback_cli.py run vault    --repo /path/to/repo --dry-run
python bagback_cli.py run arch     --repo /path/to/repo --owner mohamedosamaai
python bagback_cli.py run docs     --repo /path/to/repo --project-name "ELITK-8" --owner mohamedosamaai
python bagback_cli.py run pmo      --owner mohamedosamaai --project-title "ELITK-8 Roadmap"
python bagback_cli.py run ci       --repo /path/to/repo --owner mohamedosamaai
python bagback_cli.py run release  --repo /path/to/repo
python bagback_cli.py run showcase --source /private/repo --target /public/showcase
```

## The 4 Safety Guarantees

| # | Guarantee | Implementation |
|---|---|---|
| 1 | **Backup Branch** | Every script creates `automation-backup-<timestamp>` before touching files |
| 2 | **Dry-Run Mode** | `--dry-run` on any script prints all planned changes without executing |
| 3 | **Pre-flight Checks** | Aborts on uncommitted changes, missing auth, Python < 3.11 |
| 4 | **No Regex Surgery** | File modifications use line-by-line analysis, not blind search-replace |

## Pipeline Overview

| Script | Name | What It Does |
|---|---|---|
| `01` | Humanizer | Removes AI comment markers, guides history cleanup |
| `02` | Vault Shield | Sanitizes `.env` secrets, plants `.gitignore`, Gitleaks config, Husky hooks |
| `03` | Clean Architecture | Runs Prettier + ESLint, plants `.nvmrc` and `CODEOWNERS` |
| `04` | Docs Architect | Generates enterprise `README.md` and `docs/adr/` records |
| `05` | Agile PMO | Creates GitHub Project V2 board with 8 views and custom fields |
| `06` | DevOps CI | Writes optimized `ci.yml`, `dependabot.yml`, adds CI badge to README |
| `07` | Semantic Release | Bumps version, updates `CHANGELOG.md`, creates GitHub Release |
| `08` | Export Showcase | Exports sanitized public showcase from private enterprise repo |

## License

MIT — Mohamed Osama / Bagback Digital Solutions
