# Repository Automation and Commit Policy

This repository is administered by Mohamed Osama (`@mohamedosamaai`). Automation tools may create working branches, commits, pull requests, and Actions runs when directed by the owner.

## Required workflow

- Work on a non-default branch and open a pull request into the default branch.
- Never force-push or delete the default branch.
- Never delete repositories, branches, releases, environments, secrets, or deployment configuration.
- Keep Actions available and preserve the repository's deployment workflow.
- Use squash merge so each accepted pull request produces one intentional commit.

## Commit attribution

- Commit messages must describe the change, not the tool used to produce it.
- Do not add `Co-authored-by`, `Generated-by`, model names, tool names, or automation signatures to commit messages.
- Do not claim another human authored work they did not author.
- Owner-directed repository maintenance is committed by Mohamed Osama using `developer@mohamedosama.me`.
- Historical commit rewriting requires separate, explicit approval because it changes commit hashes and may disrupt deployments and open pull requests.

## Safety boundary

Repository contents and product terminology may legitimately mention AI providers, models, or automation. This policy applies to authorship and commit metadata; it does not permit changing functional product behavior or factual technical documentation merely to hide a technology name.
