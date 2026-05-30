# Reproducibility Plan

## Purpose

This project should be reproducible as a public scientific workflow while
respecting data-use agreements, sensitive biodiversity records, and large-file
boundaries. The repository should make every analytical decision, derived
artifact, and manuscript output traceable to documented inputs and code.

## Intended Repository Structure

Current lightweight scaffold:

- `AGENTS.md`: repo-local operating rules.
- `README.md`: project entry point.
- `docs/`: project brief, plans, registers, goal logs, and decision records.
- `data/`: data policy notes and, later, untracked local data subdirectories.
- `artifacts/`: policy notes for generated reports, models, figures, and
  validation outputs.
- `manuscript/`: manuscript build notes and, later, source files connected to
  `makedoc`.

Expected future source areas:

- `scripts/` or `R/`: reusable extraction, cleaning, modelling, and validation
  code.
- `config/`: declarative settings for geography, species lists, covariate
  definitions, and model runs.
- `references/`: bibliography and citation metadata if not managed directly by
  the manuscript pipeline.
- `logs/` or `docs/provenance/`: human-readable run records and data-decision
  notes when the workflow becomes executable.

Add these future directories only when a goal needs them.

## Environment Strategy

- Keep the foundation phase dependency-light.
- Prefer `renv` for R isolation when R analysis code begins.
- Prefer `uv` for Python utilities if Python scripts become necessary.
- Do not add heavyweight dependencies until a goal justifies the workflow
  stack and records why the dependency is needed.
- Record exact package versions, system requirements, and restore commands once
  an executable analysis environment exists.

## Generated Artifact Policy

Do not commit:

- raw external biodiversity or hydrology data
- private exports or permission-restricted survey files
- credentials, API keys, request tokens, or data-use agreements
- bulky intermediate rasters, model objects, cache directories, or build output

Commit only:

- source code
- configuration
- small public fixtures when licensing allows
- data dictionaries
- provenance summaries
- validation summaries
- final manuscript source and policy-approved figures/tables

Generated data and artefacts should be reproducible from documented sources.
When licensing prevents redistribution, commit the scripts, metadata schema,
checksums where allowed, and clear rebuild instructions instead of the data.

## Provenance Logging

Every data or analysis goal should record:

- input source, access route, access date, and license status
- filtering rules and exclusion counts
- spatial and temporal aggregation choices
- software environment and command used
- output location, checksum when appropriate, and sensitivity status
- reviewer-facing rationale for major decisions

Major scientific and workflow decisions belong in
`docs/decision_log.md`. Goal-specific execution evidence belongs in the
corresponding `docs/goals/*/Log.md`.

## Manuscript Build Pathway

Substantive manuscript sources should live under `manuscript/` once drafting
begins. The build pathway should use the external manuscript tooling at:

```text
/Users/bwbrook/work/makedoc
```

The later manuscript goal should:

- create manuscript source files in this repo
- define the profile needed by `makedoc`
- keep manuscript figures and tables generated from documented artifact paths
- record how `.pdf` and `.docx` outputs are built
- keep generated submission files out of source control unless explicitly
  approved for release

## Archive Expectations

Before submission or public release, the project should provide:

- frozen analysis plan and decision log
- data-stream register with inclusion/exclusion decisions
- reproducible code and environment lockfiles
- data dictionaries and provenance summaries
- validation reports and bias-simulation results
- manuscript source, figures, tables, and build instructions
- archive manifest identifying which derived products can be shared and which
  must be rebuilt from restricted inputs
