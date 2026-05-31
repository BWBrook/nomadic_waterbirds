#!/usr/bin/env python3
"""Run Goal 009 full-window event hydrology with the Goal 009 config."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

os.environ.setdefault(
    "NOMADIC_WATERBIRDS_EVENT_CONFIG",
    str(REPO / "settings" / "remote_full_window_hydrology_009.json"),
)

from event_window_hydrology_007 import run  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run())
