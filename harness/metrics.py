"""Accuracy, Cohen's kappa, confusion, and per-category agreement."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from harness.code_grader import grade_reply
from harness.common import CATEGORIES, RAW, RESULTS, load_items, write_json

N_BOOT = 10000
BOOT_SEED = 0


def cohen_kappa(y_true: list[str], y_pred: list[str]) -> float | None:
    n = len(y_true)
    if n == 0:
        return None
    po = sum(a == b for a, b in zip(y_true, y_pred)) / n

    def rate(label: str, values: list[str]) -> float:
        return sum(v == label for v in values) / n

    pe = rate("PASS", y_true) * rate("PASS", y_pred) + rate("FAIL", y_true) * rate("FAIL", y_pred)
    if abs(1.0 - pe) < 1e-12:
        return None
    return (po - pe) / (1.0 - pe)


def bootstrap_kappa(y_true: list[str], y_pred: list[str], n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    point = cohen_kappa(y_true, y_pred)
    n = len(y_true)
    if n == 0 or point is None:
        return {"kappa": point, "ci_low": None, "ci_high": None, "n_boot_defined": 0, "n_boot": n_boot}
    rng = np.random.default_rng(seed)
    true_arr = np.array(y_true)
    pred_arr = np.array(y_pred)
    defined: list[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        value = cohen_kappa(true_arr[idx].tolist(), pred_arr[idx].tolist())
        if value is not None:
            defined.append(float(value))
    if not defined:
        return {"kappa": point, "ci_low": None, "ci_high": None, "n_boot_defined": 0, "n_boot": n_boot}
    low, high = np.percentile(defined, [2.5, 97.5])
    return {
        "kappa": point,
        "ci_low": float(low),
        "ci_high": float(high),
        "n_boot_defined": len(defined),
        "n_boot": n_boot,
        "seed": seed,
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = k / n
    z2 = z * z
    den = 1.0 + z2 / n
    center = (p + z2 / (2 * n)) / den
    margin = z * math.sqrt((p * (1.0 - p) / n) + z2 / (4.0 * n * n)) / den
    return max(0.0, center - margin), min(1.0, center + margin)


def confusion(y_true: list[str], y_pred: list[str]) -> dict:
    matrix = {"PASS": {"PASS": 0, "FAIL": 0}, "FAIL": {"PASS": 0, "FAIL": 0}}
    for true, pred in zip(y_true, y_pred):
        matrix[true][pred] += 1
    return matrix


def pr_fail(y_true: list[str], y_pred: list[str]) -> dict:
    tp = sum(t == "FAIL" and p == "FAIL" for t, p in zip(y_true, y_pred))
    fp = sum(t == "PASS" and p == "FAIL" for t, p in zip(y_true, y_pred))
    fn = sum(t == "FAIL" and p == "PASS" for t, p in zip(y_true, y_pred))
    tn = sum(t == "PASS" and p == "PASS" for t, p in zip(y_true, y_pred))
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    return {
        "tp_fail": tp,
        "fp_fail": fp,
        "fn_fail": fn,
        "tn_pass": tn,
        "precision_fail": precision,
        "recall_fail": recall,
    }


def load_judge(judge: str, rep: int) -> dict[str, dict]:
    folder = RAW / judge / f"rep{rep}"
    found: dict[str, dict] = {}
    if not folder.exists():
        return found
    for path in sorted(folder.glob("t??.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        found[row["id"]] = row
    return found


def score_pair(items: list[dict], preds: dict[str, str]) -> dict:
    paired = [item for item in items if item["id"] in preds]
    y_true = [item["label"] for item in paired]
    y_pred = [preds[item["id"]] for item in paired]
    n = len(paired)
    correct = sum(a == b for a, b in zip(y_true, y_pred))
    acc_ci = wilson(correct, n)
    pass_pred = sum(v == "PASS" for v in y_pred)
    pass_ref = sum(v == "PASS" for v in y_true)
    kappa = bootstrap_kappa(y_true, y_pred)
    by_cat = {}
    for cat in CATEGORIES:
        subset = [item for item in paired if item["category"] == cat]
        if not subset:
            by_cat[cat] = {"n": 0, "rate": None, "k": 0}
            continue
        if cat == "correct":
            k = sum(preds[item["id"]] == "PASS" for item in subset)
            meaning = "share_judged_PASS"
        else:
            k = sum(preds[item["id"]] == "FAIL" for item in subset)
            meaning = "share_judged_FAIL"
        by_cat[cat] = {"n": len(subset), "k": k, "rate": k / len(subset), "meaning": meaning}
    return {
        "n_scored": n,
        "n_correct": correct,
        "accuracy": correct / n if n else None,
        "accuracy_wilson95": list(acc_ci) if acc_ci else None,
        "pass_pred": pass_pred,
        "pass_pred_rate": pass_pred / n if n else None,
        "pass_ref_on_scored": pass_ref,
        "kappa": kappa,
        "confusion": confusion(y_true, y_pred),
        "fail_detection": pr_fail(y_true, y_pred),
        "by_category": by_cat,
    }


def self_consistency(rep1: dict[str, dict], rep2: dict[str, dict]) -> dict | None:
    ids = sorted(set(rep1) & set(rep2))
    paired = []
    for item_id in ids:
        a = rep1[item_id].get("parsed_verdict")
        b = rep2[item_id].get("parsed_verdict")
        if a in ("PASS", "FAIL") and b in ("PASS", "FAIL"):
            paired.append((a, b))
    if not paired:
        return None
    y1 = [a for a, _ in paired]
    y2 = [b for _, b in paired]
    same = sum(a == b for a, b in paired)
    return {
        "n": len(paired),
        "n_same": same,
        "agreement": same / len(paired),
        "agreement_wilson95": list(wilson(same, len(paired))),
        "kappa": bootstrap_kappa(y1, y2),
    }


def usage_summary(rows: dict[str, dict]) -> dict:
    cost = 0.0
    cost_n = 0
    tokens: dict[str, int] = {}
    elapsed = []
    for row in rows.values():
        if row.get("total_cost_usd") is not None:
            cost += float(row["total_cost_usd"])
            cost_n += 1
        usage = row.get("usage") or {}
        if isinstance(usage, dict):
            for key, value in usage.items():
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    continue
                tokens[key] = tokens.get(key, 0) + int(value)
        if row.get("elapsed_s") is not None and not row.get("skipped"):
            elapsed.append(float(row["elapsed_s"]))
    elapsed_sorted = sorted(elapsed)
    def pct(p: float) -> float | None:
        if not elapsed_sorted:
            return None
        k = (len(elapsed_sorted) - 1) * p
        lo = math.floor(k)
        hi = math.ceil(k)
        if lo == hi:
            return elapsed_sorted[lo]
        return elapsed_sorted[lo] * (hi - k) + elapsed_sorted[hi] * (k - lo)

    return {
        "n_with_cost": cost_n,
        "total_cost_usd": cost if cost_n else None,
        "tokens": tokens,
        "n_elapsed": len(elapsed_sorted),
        "elapsed_p50_s": pct(0.5),
        "elapsed_p95_s": pct(0.95),
    }


def write_disagreements(path: Path, items: list[dict], columns: list[tuple[str, dict[str, dict]]], code_rows: dict[str, dict]) -> None:
    lines = [
        "# Disagreements with the author reference labels",
        "",
        "An item is listed when at least one scored judge, including the code grader, disagrees with the reference label.",
        "Reference labels are author labels against `data/rubric.md`, not independent human labels.",
        "",
    ]
    n_listed = 0
    for item in items:
        diffs = []
        if code_rows[item["id"]]["verdict"] != item["label"]:
            diffs.append(("code", code_rows[item["id"]]["verdict"], ", ".join(code_rows[item["id"]]["flags"]) or "(no flags)"))
        for name, rows in columns:
            row = rows.get(item["id"])
            if not row or row.get("parsed_verdict") not in ("PASS", "FAIL"):
                if row is not None:
                    diffs.append((name, "UNPARSED", row.get("parse_error") or ""))
                continue
            if row["parsed_verdict"] != item["label"]:
                diffs.append((name, row["parsed_verdict"], row.get("parsed_reason") or ""))
        if not diffs:
            continue
        n_listed += 1
        lines.append(f"## {item['id']} reference {item['label']} / {item['category']}")
        lines.append("")
        lines.append(f"Question: {item['question']}")
        lines.append("")
        lines.append(f"Reply: {item['reply']}")
        lines.append("")
        lines.append(f"Reference rationale: {item['rationale']}")
        lines.append("")
        for name, verdict, reason in diffs:
            lines.append(f"- {name}: {verdict}. {reason}")
        lines.append("")
    lines.insert(4, f"Listed items: {n_listed} of {len(items)}.")
    lines.insert(5, "")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    items = load_items()
    code = {}
    for item in items:
        graded = grade_reply(item["reply"])
        code[item["id"]] = {"id": item["id"], "verdict": graded["verdict"], "flags": graded["flags"]}

    judge_specs = [
        ("code", None),
        ("grok-full", 1),
        ("grok-full", 2),
        ("grok-minimal", 1),
        ("qwen-full", 1),
    ]
    loaded = {}
    for judge, rep in judge_specs:
        if judge == "code":
            continue
        loaded[(judge, rep)] = load_judge(judge, rep)

    ref_pass = sum(item["label"] == "PASS" for item in items)
    summary = {
        "n_items": len(items),
        "reference_pass": ref_pass,
        "reference_fail": len(items) - ref_pass,
        "reference_pass_rate": ref_pass / len(items),
        "reference_pass_wilson95": list(wilson(ref_pass, len(items))),
        "newsletter_pass_count_cited": "34/60",
        "bootstrap": {"n_boot": N_BOOT, "seed": BOOT_SEED, "ci": "percentile 2.5/97.5"},
        "judges": {},
    }

    def add_judge(name: str, preds: dict[str, str], extra: dict | None = None) -> None:
        block = score_pair(items, preds)
        if extra:
            block.update(extra)
        summary["judges"][name] = block

    add_judge("code", {item_id: row["verdict"] for item_id, row in code.items()}, {"n_unparsed": 0})

    for (judge, rep), rows in loaded.items():
        if not rows:
            continue
        parsed = {item_id: row["parsed_verdict"] for item_id, row in rows.items() if row.get("parsed_verdict") in ("PASS", "FAIL")}
        unparsed = [item_id for item_id, row in rows.items() if row.get("parsed_verdict") not in ("PASS", "FAIL")]
        missing = [item["id"] for item in items if item["id"] not in rows]
        name = f"{judge}/rep{rep}"
        add_judge(
            name,
            parsed,
            {
                "n_raw_files": len(rows),
                "n_unparsed": len(unparsed),
                "unparsed_ids": unparsed,
                "missing_ids": missing,
                "usage": usage_summary(rows),
            },
        )

    if loaded.get(("grok-full", 1)) and loaded.get(("grok-full", 2)):
        summary["grok_full_self_consistency"] = self_consistency(loaded[("grok-full", 1)], loaded[("grok-full", 2)])

    write_json(RESULTS / "summary.json", summary)
    write_json(RESULTS / "code_grader.json", [code[item["id"]] for item in items])

    # CSV of judge-level metrics
    csv_path = RESULTS / "summary.csv"
    fields = [
        "judge",
        "n_scored",
        "n_unparsed",
        "accuracy",
        "accuracy_wilson95_low",
        "accuracy_wilson95_high",
        "kappa",
        "kappa_ci_low",
        "kappa_ci_high",
        "precision_fail",
        "recall_fail",
        "pass_pred",
        "pass_pred_rate",
        "tn_pass",
        "fp_fail",
        "fn_fail",
        "tp_fail",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for name, block in summary["judges"].items():
            kappa = block["kappa"]
            acc_ci = block["accuracy_wilson95"] or [None, None]
            fail = block["fail_detection"]
            writer.writerow(
                {
                    "judge": name,
                    "n_scored": block["n_scored"],
                    "n_unparsed": block.get("n_unparsed", 0),
                    "accuracy": block["accuracy"],
                    "accuracy_wilson95_low": acc_ci[0],
                    "accuracy_wilson95_high": acc_ci[1],
                    "kappa": kappa["kappa"],
                    "kappa_ci_low": kappa["ci_low"],
                    "kappa_ci_high": kappa["ci_high"],
                    "precision_fail": fail["precision_fail"],
                    "recall_fail": fail["recall_fail"],
                    "pass_pred": block["pass_pred"],
                    "pass_pred_rate": block["pass_pred_rate"],
                    "tn_pass": fail["tn_pass"],
                    "fp_fail": fail["fp_fail"],
                    "fn_fail": fail["fn_fail"],
                    "tp_fail": fail["tp_fail"],
                }
            )

    # per item
    per_path = RESULTS / "per_item.csv"
    per_fields = ["id", "label", "category", "code_verdict", "code_flags"]
    judge_cols = []
    for (judge, rep), rows in loaded.items():
        if not rows:
            continue
        prefix = f"{judge}_rep{rep}"
        judge_cols.append((prefix, rows))
        per_fields.extend([f"{prefix}_verdict", f"{prefix}_reason"])
    with per_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=per_fields)
        writer.writeheader()
        for item in items:
            out = {
                "id": item["id"],
                "label": item["label"],
                "category": item["category"],
                "code_verdict": code[item["id"]]["verdict"],
                "code_flags": "|".join(code[item["id"]]["flags"]),
            }
            for prefix, rows in judge_cols:
                row = rows.get(item["id"], {})
                out[f"{prefix}_verdict"] = row.get("parsed_verdict")
                out[f"{prefix}_reason"] = row.get("parsed_reason")
            writer.writerow(out)

    columns = []
    for (judge, rep), rows in loaded.items():
        if rows:
            columns.append((f"{judge}/rep{rep}", rows))
    write_disagreements(RESULTS / "disagreements.md", items, columns, code)

    # short text table for the README author
    lines = [f"n={len(items)} reference PASS {ref_pass}/{len(items)}"]
    for name, block in summary["judges"].items():
        kappa = block["kappa"]
        lines.append(
            f"{name}: n={block['n_scored']} acc={block['accuracy']} "
            f"kappa={kappa['kappa']} CI=({kappa['ci_low']}, {kappa['ci_high']}) "
            f"pass={block['pass_pred']}/{block['n_scored']} "
            f"recall_fail={block['fail_detection']['recall_fail']} "
            f"precision_fail={block['fail_detection']['precision_fail']}"
        )
    if "grok_full_self_consistency" in summary and summary["grok_full_self_consistency"]:
        sc = summary["grok_full_self_consistency"]
        lines.append(
            f"self: n={sc['n']} agree={sc['agreement']} kappa={sc['kappa']['kappa']} "
            f"CI=({sc['kappa']['ci_low']}, {sc['kappa']['ci_high']})"
        )
    text = "\n".join(lines) + "\n"
    (RESULTS / "summary.txt").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
