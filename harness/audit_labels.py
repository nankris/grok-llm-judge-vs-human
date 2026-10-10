"""Print each item beside the dollar amounts, refund-day hits, and code-grader flags.

This is the double-check aid. It does not relabel items.
"""

from __future__ import annotations

import re
from collections import Counter

from harness.code_grader import grade_reply
from harness.common import load_items, load_text

DOLLAR_RE = re.compile(r"\$\s*(\d{1,5}(?:,\d{3})*(?:\.\d{1,2})?)")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def main() -> None:
    items = load_items()
    policy = load_text("policy.md")
    print(f"n={len(items)}")
    counts = Counter((row["label"], row["category"]) for row in items)
    for key, n in sorted(counts.items()):
        print(f"  {key[0]:4} {key[1]:16} {n}")
    print()
    for row in items:
        graded = grade_reply(row["reply"])
        dollars = DOLLAR_RE.findall(row["reply"])
        numbers = NUMBER_RE.findall(row["reply"])
        print("=" * 78)
        print(f"{row['id']}  {row['label']}  {row['category']}  code={graded['verdict']}  flags={graded['flags']}")
        print(f"Q: {row['question']}")
        print(f"A: {row['reply']}")
        print(f"R: {row['rationale']}")
        print(f"dollars={dollars} numbers={numbers}")
        # Policy lines that mention any dollar amount or integer from the reply.
        needles = set(dollars)
        for num in numbers:
            if num.isdigit() and int(num) >= 2:
                needles.add(num)
        hits = []
        for line in policy.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if any(n in stripped for n in needles):
                hits.append(stripped)
        for hit in hits[:8]:
            print(f"  | {hit}")
    print("=" * 78)
    n_pass = sum(row["label"] == "PASS" for row in items)
    print(f"pass_rate={n_pass}/{len(items)}")


if __name__ == "__main__":
    main()
