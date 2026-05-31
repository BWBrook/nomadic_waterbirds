# Remote Hydrology Rehearsal 008 Report

## Purpose

Goal 008 tested whether `deep-server` can become the near-term host for
heavier DEA Water Observations event-window extraction.

## Remote Setup

The direct `deep-server` SSH alias timed out. The documented `deep-server-ts`
alias succeeded and landed on `deep-server` as `bwbrook`.

The remote working copy was staged at:

```text
/data/codex/repos/nomadic_waterbirds_goal008
```

Direct GitHub SSH from `deep-server` returned `Permission denied (publickey)`,
so source was staged from the Mac mini using `.git` plus
`git ls-files --cached --others --exclude-standard` through `rsync`. Raw local
artifacts were not sent as source files.

## Remote Validation

The synced remote working copy ran:

```bash
python3 -m unittest discover -s tests -p "test*.py"
```

Result: 7 tests passed.

The remote copy also ran:

```bash
python3 scripts/narran_subunit_evidence_008.py
```

Result: 44 Narran crosswalk rows and 39 DEA Waterbody parent-overlap screens.

## Hydrology Smoke

The first hydrology smoke exposed a small cross-platform bug in
`scripts/official_support_hydrology_005.py`: local GDAL accepted the OGR `MEM`
vector driver, but `deep-server` GDAL 3.8 exposed the in-memory vector driver
as `Memory`. Goal 008 added a fallback helper and regression test.

The second hydrology smoke built the Narran parent reference grid:

| Field | Value |
| --- | ---: |
| Support | `nwb002_ramsar_ref1291` |
| Month | `2024-12` |
| Grid xsize | 403 |
| Grid ysize | 414 |
| Grid pixels | 166842 |
| Support mask pixels | 93937 |

Monthly processing then stopped with:

```text
HTTP Error 503: Service Temporarily Unavailable
```

The same STAC error occurred for remote checks of `2020-03`, `2022-11`,
`2024-11`, and `2024-12`, and for local checks of `2020-03` and `2024-12`.

## Remote Outputs

Remote ignored outputs were left under:

```text
/data/codex/repos/nomadic_waterbirds_goal008/artifacts/remote_hydrology_rehearsal/output/
```

| Remote artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `goal008_remote_narran_parent_2024_12_series.csv` | 1863 | `efee69eda6c18177c521dc2145e55bfc7181b32d55bc92477ede5928a367a72c` |
| `goal008_remote_narran_parent_2024_12_summary.csv` | 814 | `270175eaf8d1858c7a799b2582e7316179b9124e33e8e099673e525aa63423ab` |
| `goal008_remote_narran_parent_2024_12_manifest.json` | 2218 | `548ae0a32b03314a28c03db046e1e8bcdcd29a04ffca87e42ec71e78f5e5698b` |

These files are proof artifacts only and were not committed.

## Conclusion

`deep-server-ts` is viable for the next hydrology scale-up: it has the CPU,
memory, disk, Python, GDAL, and NumPy needed for the current workflow after the
OGR memory-driver fallback fix. The full `2018-01` through `2024-12` run was
deferred because DEA STAC was returning service-wide `503` responses during
Goal 008.
