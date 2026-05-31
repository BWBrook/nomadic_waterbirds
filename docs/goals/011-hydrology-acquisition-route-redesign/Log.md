# Goal 011 Log - Hydrology Acquisition Route Redesign

## Supervisor Preparation

- 2026-05-31: Supervisor reviewed Goal 010 outputs and verified the action
  repo was clean and synced at `fdb22dc` (`Run Goal 010 hydrology recovery
  preflight`).
- 2026-05-31: Supervisor confirmed Goal 010 stopped correctly: Mac mini STAC
  probes returned `HTTP 503` for all three months after bounded retry, and
  `deep-server-ts` remained unstable with one exhausted timeout and two
  success-after-retry months.
- 2026-05-31: Supervisor inspected the hydrology code and noted that
  `stac_search` is called inside the support/month processing loop, implying
  that the 11-support, 84-month window can depend on hundreds of live STAC
  searches.
- 2026-05-31: Goal package written for publication into the action repo under
  `docs/goals/011-hydrology-acquisition-route-redesign/`.

## Executor Checkpoints

- 2026-05-31: Confirmed starting Git state was clean on `main` at `29d749f`,
  with `origin/main` aligned and the Goal 010 checkpoint (`fdb22dc`) present
  in history.
- 2026-05-31: Re-read `Goal.md`, `Plan.md`, and `Runbook.md`, then audited the
  current hydrology path. `stac_search` is called inside the support/month loop
  in `scripts/event_window_hydrology_007.py`, giving 924 live STAC searches for
  the 11-support by 84-month Goal 009 window and up to 2772 HTTP attempts under
  the current three-attempt retry policy.
- 2026-05-31: Rechecked official DEA source documentation for Water
  Observations, AWS/S3 access, STAC metadata/streaming, direct S3 download
  guidance, Water Observations Statistics, DEA Waterbodies, DEA Sandbox, and
  Open Data Cube loading.
- 2026-05-31: Added focused Goal 011 tests and
  `scripts/hydrology_acquisition_route_probe_011.py`; the focused test command
  `python3 -m unittest tests.test_goal011_hydrology_acquisition_route` passed.
- 2026-05-31: Ran bounded live probe:
  `python3 scripts/hydrology_acquisition_route_probe_011.py --host-label mac-mini-goal011 --output artifacts/hydrology_access_route_011/output/route_probe_macmini_011.json`.
  The S3 prefix list and known COG HEAD returned HTTP 200; the one-item STAC
  search returned HTTP 503. The probe JSON remains in ignored `artifacts/`.
- 2026-05-31: Drafted Goal 011 report, manifest, route comparison CSV, query
  pattern CSV, source-register updates, data-stream update, decision-log entry,
  and docs navigation entry. Recommendation: do not rerun the status quo; make
  Goal 012 a bounded candidate-month STAC cache plus direct S3/index prototype.
- 2026-05-31: Validation checkpoint passed before staging: `rg --files`
  confirmed expected Goal 011 files; `python3 -m json.tool
  docs/hydrology_acquisition_route_011_manifest.json` passed; CSV required
  columns parsed with 7 route rows and 5 query-pattern rows; `git diff --check`
  passed; `python3 -m unittest tests.test_goal011_hydrology_acquisition_route`
  passed; `python3 -m unittest discover -s tests -p 'test*.py'` passed with 19
  tests; committed-size and raw-extension checks passed; unfinished-marker scan
  returned no hits; local Markdown link check passed; source URL coverage check
  passed against the source register and Goal 011 manifest.
