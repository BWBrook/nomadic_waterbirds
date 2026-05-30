# Runbook

## Working Directory

Work in:

```text
/Users/bwbrook/papers/nomadic_waterbirds
```

## Operating Rules

- Start from the repo's `README.md` and `docs/project_brief.md`.
- Once `AGENTS.md` exists, follow it for the remainder of the run.
- Keep this goal to foundation, planning, and governance.
- Do not download or request external data.
- Do not fit models or create analysis results.
- Do not launch remote compute.
- Commit and push only the validated foundation package.

## Suggested Commands

Orient:

```bash
git status --short --branch
git log --oneline --decorate -3
git remote -v
rg --files
```

Check generated files:

```bash
git diff --check
find . -type f -size +5M -not -path './.git/*'
rg -n 'TO''DO|TB''D|FIX''ME|lor''em' AGENTS.md README.md docs || true
```

Finish:

```bash
git status --short --branch
git add AGENTS.md .gitignore docs data artifacts manuscript
git commit -m "Add reproducible research foundation"
git push origin main
git status --short --branch
```

Adjust the final `git add` paths to match the files actually created.

## Reporting Rules

Update:

- `/Users/bwbrook/papers/nomadic_waterbirds/docs/goals/001-project-foundation/Log.md`
- `/Users/bwbrook/papers/nomadic_waterbirds/docs/decision_log.md`

The final response should include:

- changed files
- validation commands and outcomes
- commit hash and push status
- residual risks
- recommended Goal 002

## Decision Authority

You may choose practical document structure and lightweight scaffolding. Pause
before data acquisition, final biological choices, model fitting, remote
compute, or heavyweight dependency decisions.
