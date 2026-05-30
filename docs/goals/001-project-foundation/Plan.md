# Plan

## Purpose

Create the project foundation for `nomadic_waterbirds`, preserving the central
scientific thesis and giving future action-agent goals a stable operating
surface.

## Expected File Responsibilities

- `AGENTS.md`: repo-local rules for future agents.
- `docs/analysis_plan.md`: scientific and statistical analysis architecture.
- `docs/data_stream_register.md`: data-source roles, access constraints, and
  inclusion rules.
- `docs/reproducibility_plan.md`: environment, artefact, provenance, and
  manuscript-build architecture.
- `docs/validation_plan.md`: blocked validation and synthetic-bias strategy.
- `docs/manuscript_plan.md`: paper framing, claims, figures, and tables.
- `docs/decision_log.md`: dated decisions and rationale.
- `docs/goals/001-project-foundation/Log.md`: executor work log.
- Optional small README/scaffold files: clarify data, artefact, and manuscript
  conventions without implementing the analysis.

## Task Sequence

1. Confirm repository state and read the brief.
2. Draft `AGENTS.md` first so the rest of the goal has local rules.
3. Draft the analysis, data, reproducibility, validation, and manuscript plans.
4. Add a decision log and update the goal log with checkpoints.
5. Add only lightweight scaffolding needed to make future workflow boundaries
   clear.
6. Validate Markdown, links, Git diff hygiene, and absence of large data files.
7. Commit and push the foundation package if validation passes.

## Self-Review Questions

- Does the plan prevent drift into a static SDM?
- Are data roles and access constraints explicit enough for a later acquisition
  goal?
- Are effort/detectability and sampling bias visible from the start?
- Are uncertainty and blocked validation built into the workflow?
- Does the manuscript plan state what evidence each central claim will need?
- Would a fresh action agent know what to do next without reading supervisor
  notes outside the action repo?
