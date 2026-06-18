# Contributing

## Branches

- Work on feature or fix branches.
- Agents and automation may create branches, commits, and pull requests when instructed.
- Do not force-push or delete shared branches unless Mohamed Osama explicitly approves it.

## Pull Requests

- Keep pull requests focused and describe the user-visible impact.
- Include verification steps when code changes are made.
- Do not change secrets, deployment settings, or production environment configuration without calling it out clearly.

## Safety

- Do not commit generated credentials, `.env` files, database dumps, or private customer data.
- Avoid broad refactors unless they are required for the task.
- Preserve existing deployment behavior unless a change is explicitly requested.

## Commit and automation policy

All contributors and repository automation must follow [the repository commit policy](.github/COMMIT_POLICY.md). In particular, use a working branch and pull request, keep commit messages focused on the change, and do not add tool/model attribution or `Co-authored-by` trailers.
