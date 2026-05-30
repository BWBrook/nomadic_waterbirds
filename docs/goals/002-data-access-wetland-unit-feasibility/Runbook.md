# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Follow `AGENTS.md`.
- Use current official sources for data-access and wetland-unit claims.
- Record URLs and access dates.
- Do not download datasets, submit requests, log in, or use private
  credentials.
- Keep outputs as Markdown decision documents.
- Commit and push only the validated feasibility package.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -5
rg --files
```

Validation:

```bash
git diff --check
find . -type f -size +5M -not -path './.git/*'
rg -n 'TO''DO|TB''D|FIX''ME|lor''em' docs AGENTS.md README.md || true
git status --short --branch
```

Use a small link-checking approach of your choice for local Markdown links in
new or edited docs. Record the command or method in the goal log.

Finish:

```bash
git add docs
git commit -m "Assess data access and wetland unit feasibility"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths if other documentation files are changed.

## Reporting Rules

Update:

- `docs/goals/002-data-access-wetland-unit-feasibility/Log.md`
- `docs/data_stream_register.md`
- `docs/decision_log.md`

Final response should include changed files, high-level sources checked,
recommended prototype, validation outcomes, commit/push status, residual risks,
and recommended Goal 003.
