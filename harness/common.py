"""Shared paths and item loading."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RAW = RESULTS / "raw"
IMAGES = ROOT / "images"

CATEGORIES = (
    "invented_fact",
    "wrong_number",
    "missed_question",
    "unsafe_promise",
    "tone",
    "correct",
)
VERDICTS = ("PASS", "FAIL")


def load_text(name: str) -> str:
    return (DATA / name).read_text(encoding="utf-8")


def load_items() -> list[dict]:
    path = DATA / "items.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
