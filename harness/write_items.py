"""Write data/items.jsonl from the authored data/items.py list."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.items import ITEMS  # noqa: E402
from harness.common import CATEGORIES, VERDICTS  # noqa: E402


def main() -> None:
    ids = [row["id"] for row in ITEMS]
    if len(ITEMS) != 60:
        raise SystemExit(f"expected 60 items, found {len(ITEMS)}")
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    if ids != [f"t{i:02d}" for i in range(1, 61)]:
        raise SystemExit(f"ids are not t01..t60 in order: {ids}")
    for row in ITEMS:
        for key in ("id", "question", "reply", "label", "category", "rationale"):
            if not str(row.get(key, "")).strip():
                raise SystemExit(f"{row.get('id')} missing {key}")
        if row["label"] not in VERDICTS:
            raise SystemExit(f"{row['id']} bad label")
        if row["category"] not in CATEGORIES:
            raise SystemExit(f"{row['id']} bad category")
        if (row["label"] == "PASS") != (row["category"] == "correct"):
            raise SystemExit(f"{row['id']} label/category mismatch")
    out = ROOT / "data" / "items.jsonl"
    with out.open("w", encoding="utf-8") as fh:
        for row in ITEMS:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    n_pass = sum(row["label"] == "PASS" for row in ITEMS)
    print(f"wrote {out} n={len(ITEMS)} pass={n_pass} fail={len(ITEMS) - n_pass}")


if __name__ == "__main__":
    main()
