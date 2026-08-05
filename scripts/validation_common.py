"""Read-only, deterministic primitives shared by Goals 021-023 validators."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
UNFINISHED_MARKER_PATTERN = re.compile(
    r"\b(" + "|".join(["to" + "do", "tb" + "d", "place" + "holder", "fix" + "me", "x" * 3]) + r")\b",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON object without changing the source file."""

    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV into dictionaries without changing the source file."""

    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def file_hash(path: Path) -> str:
    """Return the SHA-256 digest of a file's current bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_row_hash(
    rows: Iterable[Mapping[str, Any]],
    sort_key: str | Sequence[str] | None = None,
) -> str:
    """Hash row content deterministically, optionally using one or more keys."""

    normalised: list[dict[str, str]] = []
    for row in rows:
        normalised_row: dict[str, str] = {}
        for key, value in row.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            normalised_row[key] = "" if value is None else str(value)
        normalised.append(normalised_row)

    sort_fields = [sort_key] if isinstance(sort_key, str) else list(sort_key or ())
    if sort_fields and all(all(field in row for field in sort_fields) for row in normalised):
        normalised.sort(key=lambda row: tuple(row.get(field, "") for field in sort_fields))
    else:
        normalised.sort(key=lambda row: json.dumps(row, sort_keys=True))

    payload = json.dumps(normalised, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
