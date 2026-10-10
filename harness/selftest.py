"""Local checks that do not call a model."""

from __future__ import annotations

from harness.code_grader import grade_reply
from harness.common import load_items, load_text
from harness.metrics import cohen_kappa, wilson
from harness.prompts import build_prompt


def expect(cond: bool, message: str) -> None:
    if not cond:
        raise SystemExit(message)


def test_kappa() -> None:
    y1 = ["PASS", "PASS", "PASS", "PASS", "FAIL", "FAIL", "FAIL", "FAIL", "PASS", "FAIL"]
    y2 = ["PASS", "PASS", "PASS", "FAIL", "FAIL", "FAIL", "FAIL", "PASS", "PASS", "FAIL"]
    value = cohen_kappa(y1, y2)
    expect(value is not None and abs(value - 0.6) < 1e-9, f"kappa {value}")
    expect(cohen_kappa([], []) is None, "empty kappa")
    perfect = ["PASS", "FAIL", "PASS"]
    expect(cohen_kappa(perfect, perfect) == 1.0, "perfect kappa")


def test_wilson() -> None:
    low, high = wilson(33, 60)
    expect(low < 33 / 60 < high, "wilson center")
    expect(wilson(0, 0) is None, "wilson empty")


def test_grader() -> None:
    cases = [
        ("No. Eligible returns do not have a restocking fee.", "PASS"),
        ("The return is eligible, but we deduct a 15% restocking fee from the refund.", "FAIL"),
        ("It is not a lifetime warranty.", "PASS"),
        ("We do not promise same-day service, so I can't guarantee it will be done today.", "PASS"),
        ("Yes. We guarantee same-day flat repairs.", "FAIL"),
        ("Ground shipping is $12.95 and takes 3-5 business days.", "FAIL"),
        ("Yes. You have a 30-day refund window, so 3 weeks is still fine.", "FAIL"),
        ("A mailed return is refunded within 5 business days after we receive the item.", "PASS"),
        ("Store credit is still possible through day 30 if the light is unused.", "PASS"),
        ("A $40 order is under the $75 free-shipping threshold, so ground shipping is $8.95.", "FAIL"),
        ("Our refund window is 10 days, so day 12 is too late for a refund or for store credit.", "FAIL"),
        ("We do not price match. We also do not offer rain checks.", "PASS"),
        ("Yes. We price match an identical in-stock item.", "FAIL"),
        ("Yes. Every repair includes a free loaner city bike.", "FAIL"),
    ]
    for text, want in cases:
        got = grade_reply(text)["verdict"]
        expect(got == want, f"grader {got} != {want} for {text}")


def test_prompts_hide_labels() -> None:
    policy = load_text("policy.md")
    rubric = load_text("rubric.md")
    items = load_items()
    expect(len(items) == 60, "n")
    n_pass = sum(item["label"] == "PASS" for item in items)
    expect(n_pass == 33, f"pass count {n_pass}")
    for item in items:
        for config in ("full", "minimal"):
            prompt = build_prompt(config, policy, rubric, item["question"], item["reply"])
            expect(item["rationale"] not in prompt, f"rationale leaked {item['id']} {config}")
            expect("Reference rationale" not in prompt, "rationale header")
            expect(f'"label": "{item["label"]}"' not in prompt, "label field leaked")
        full = build_prompt("full", policy, rubric, item["question"], item["reply"])
        minimal = build_prompt("minimal", policy, rubric, item["question"], item["reply"])
        expect("418 Cedar Ave" in full and "418 Cedar Ave" in minimal, "policy in prompt")
        expect("unsafe_promise" in full, "rubric in full")
        expect("unsafe_promise" not in minimal, "rubric leaked into minimal")
        expect("Is this reply good?" in minimal, "minimal question")
        expect("Do not use tools." in full and "Do not use tools." in minimal, "no tools")


def test_authored_edges() -> None:
    items = {item["id"]: item for item in load_items()}
    expect(items["t34"]["category"] == "wrong_number" and "30-day" in items["t34"]["reply"], "t34")
    expect(items["t36"]["category"] == "wrong_number" and "$50" in items["t36"]["reply"], "t36")
    expect(items["t38"]["category"] == "wrong_number" and "$25" in items["t38"]["reply"], "t38")
    expect(items["t48"]["category"] == "invented_fact" and "calendar month" in items["t48"]["reply"], "t48")
    expect(items["t49"]["category"] == "missed_question" and "flat" not in items["t49"]["reply"].lower(), "t49")
    expect(items["t54"]["category"] == "unsafe_promise" and "14 days" in items["t54"]["reply"], "t54")
    expect(items["t59"]["category"] == "tone" and "14 days" in items["t59"]["reply"], "t59")
    expect(items["t13"]["label"] == "PASS" and "$50" in items["t13"]["reply"], "t13")
    expect(items["t16"]["label"] == "PASS" and "$85" in items["t16"]["reply"], "t16")
    expect(items["t18"]["label"] == "PASS" and "$40" in items["t18"]["reply"] and "$25" in items["t18"]["reply"], "t18")
    # Arithmetic the rubric allows.
    expect(35 + 25 + 25 == 85, "rental math")
    expect(25 * 2 == 50, "pads math")
    expect(30 + 35 == 65, "jobs math")
    expect(20 * 2 == 40, "late math")


def main() -> None:
    test_kappa()
    test_wilson()
    test_grader()
    test_prompts_hide_labels()
    test_authored_edges()
    print("selftest ok")


if __name__ == "__main__":
    main()
