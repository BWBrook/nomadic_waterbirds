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

`nomad` should update this log during execution.
