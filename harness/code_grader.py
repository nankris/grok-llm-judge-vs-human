"""Cheap regex / keyword grader.

Rules were taken from policy.md before any judge scores existed.
Do not add keywords to chase a higher score after seeing results.

1. Every dollar amount in the reply must be one of the dollar figures
   written in the policy (customer totals and correct arithmetic totals
   that are not themselves listed will be flagged).
2. A day count in a sentence about a refund or a return must be 14,
   or 30 when that sentence also says credit, or 5 when that sentence
   says business (the mailed-refund processing time). Words such as
   "a month" or "two weeks" are not parsed.
3. Affirmative mentions of these policy prohibitions are flagged unless
   the same sentence contains a negation word: restocking, price match,
   lifetime, same-day, loaner, rain check.
"""

from __future__ import annotations

import re

# Dollar figures that appear in data/policy.md.
ALLOWED_DOLLARS = frozenset(
    {
        7500,  # $75 free-shipping threshold
        895,  # $8.95 ground
        1895,  # $18.95 express
        4500,  # $45 mail-order assembly
        1500,  # $15 flat
        2500,  # $25 brake pads per wheel, and city additional day
        7900,  # $79 tune-up
        14900,  # $149 full service
        3500,  # $35 wheel true, and city first day
        3000,  # $30 derailleur
        5000,  # $50 extra-parts approval cap
        6500,  # $65 e-bike day, and e-bike late cap
        10000,  # $100 city hold
        20000,  # $200 e-bike hold
        2000,  # $20 per late hour
        40000,  # $400 lost city bike
        180000,  # $1800 lost e-bike
    }
)

DOLLAR_RE = re.compile(r"\$\s*(\d{1,5}(?:,\d{3})*(?:\.\d{1,2})?)")
DAY_RE = re.compile(r"\b(\d+)\s*-?\s*days?\b", re.I)
DAY_OF_RE = re.compile(r"\bday\s+(\d+)\b", re.I)
REFUND_RE = re.compile(r"\b(refund|refunded|refunds|return|returns|money-back|money back)\b", re.I)
SENTENCE_RE = re.compile(r"[^.!?\n]+")
NEGATION_RE = re.compile(
    r"\b(no|not|never|don't|dont|doesn't|does not|do not|won't|will not|cannot|can't|aren't|without)\b",
    re.I,
)

# (phrase, flag). Longer phrases are listed first so they win inside a sentence.
KEYWORD_PHRASES = (
    ("price-match", "keyword:price_match"),
    ("price match", "keyword:price_match"),
    ("restocking", "keyword:restocking"),
    ("lifetime", "keyword:lifetime"),
    ("same-day", "keyword:same_day"),
    ("same day", "keyword:same_day"),
    ("loaner", "keyword:loaner"),
    ("rain check", "keyword:rain_check"),
)


def _cents(text: str) -> int:
    whole, _, frac = text.replace(",", "").partition(".")
    frac = (frac + "00")[:2]
    return int(whole) * 100 + int(frac)


def _sentences(reply: str) -> list[str]:
    return [part.strip() for part in SENTENCE_RE.findall(reply) if part.strip()]


def grade_reply(reply: str) -> dict:
    flags: list[str] = []
    for match in DOLLAR_RE.finditer(reply):
        cents = _cents(match.group(1))
        if cents not in ALLOWED_DOLLARS:
            flags.append(f"dollar:{match.group(1)}")

    for sentence in _sentences(reply):
        if not REFUND_RE.search(sentence):
            continue
        credit = re.search(r"\bcredit\b", sentence, re.I) is not None
        business = re.search(r"\bbusiness\b", sentence, re.I) is not None
        allowed = {14, 30} if credit else {14}
        if business:
            allowed.add(5)
        numbers = [int(n) for n in DAY_RE.findall(sentence)]
        numbers += [int(n) for n in DAY_OF_RE.findall(sentence)]
        for number in numbers:
            if number not in allowed:
                flags.append(f"refund_day:{number}")

    for sentence in _sentences(reply):
        if NEGATION_RE.search(sentence):
            continue
        lower = sentence.lower()
        seen: set[str] = set()
        for phrase, flag in KEYWORD_PHRASES:
            if phrase in lower and flag not in seen:
                seen.add(flag)
                flags.append(flag)

    # Stable unique list, first-seen order.
    uniq: list[str] = []
    for flag in flags:
        if flag not in uniq:
            uniq.append(flag)
    return {"verdict": "FAIL" if uniq else "PASS", "flags": uniq}


def grade_items(items: list[dict]) -> list[dict]:
    rows = []
    for item in items:
        graded = grade_reply(item["reply"])
        rows.append({"id": item["id"], "verdict": graded["verdict"], "flags": graded["flags"]})
    return rows
