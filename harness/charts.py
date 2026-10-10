"""Charts from results/summary.json. Titles use the scored n in that file."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from harness.common import CATEGORIES, IMAGES, RESULTS

DISPLAY = {
    "code": "Code grader",
    "grok-full/rep1": "Grok full rubric",
    "grok-full/rep2": "Grok full, run 2",
    "grok-minimal/rep1": "Grok minimal prompt",
    "qwen-full/rep1": "Qwen2.5-3B full rubric",
}
COLORS = {
    "code": "#4C78A8",
    "grok-full/rep1": "#F58518",
    "grok-full/rep2": "#FFB86B",
    "grok-minimal/rep1": "#54A24B",
    "qwen-full/rep1": "#E45756",
}


def _name(key: str) -> str:
    return DISPLAY.get(key, key)


def _judges(summary: dict) -> list[str]:
    order = list(DISPLAY)
    present = [key for key in order if key in summary["judges"] and summary["judges"][key]["n_scored"]]
    for key in summary["judges"]:
        if key not in present and summary["judges"][key]["n_scored"]:
            present.append(key)
    return present


def plot_confusion(summary: dict, path) -> None:
    keys = _judges(summary)
    n = len(keys)
    cols = 2 if n > 1 else 1
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5.2 * cols, 4.4 * rows), squeeze=False)
    for ax, key in zip(axes.ravel(), keys):
        block = summary["judges"][key]
        matrix = block["confusion"]
        grid = np.array(
            [
                [matrix["PASS"]["PASS"], matrix["PASS"]["FAIL"]],
                [matrix["FAIL"]["PASS"], matrix["FAIL"]["FAIL"]],
            ],
            dtype=float,
        )
        ax.imshow(grid, cmap="Blues", vmin=0)
        ax.set_xticks([0, 1], ["Judge PASS", "Judge FAIL"])
        ax.set_yticks([0, 1], ["Reference PASS", "Reference FAIL"])
        for (r, c), value in np.ndenumerate(grid):
            ax.text(c, r, str(int(value)), ha="center", va="center", fontsize=14, color="black")
        acc = block["accuracy"]
        acc_s = "n/a" if acc is None else f"{acc:.1%}"
        ax.set_title(f"{_name(key)}\nscored n={block['n_scored']}, accuracy {acc_s}")
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    fig.suptitle("Confusion matrices against author reference labels", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_kappa(summary: dict, path) -> None:
    keys = _judges(summary)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    xs = np.arange(len(keys))
    for i, key in enumerate(keys):
        kappa = summary["judges"][key]["kappa"]
        point = kappa["kappa"]
        if point is None:
            continue
        yerr = None
        if kappa["ci_low"] is not None and kappa["ci_high"] is not None:
            yerr = np.array([[point - kappa["ci_low"]], [kappa["ci_high"] - point]])
        ax.errorbar(
            [i],
            [point],
            yerr=yerr,
            fmt="o",
            color=COLORS.get(key, "#333333"),
            markersize=8,
            capsize=5,
            label=_name(key),
        )
        if point >= 0.85:
            ax.text(i, point - 0.045, f"{point:.2f}", ha="center", va="top", fontsize=9)
        else:
            ax.text(i, point + 0.045, f"{point:.2f}", ha="center", va="bottom", fontsize=9)
    ax.axhline(0.6, color="#B00020", linestyle="--", linewidth=1.2, label="0.6 release bar")
    ax.axhline(0.0, color="#888888", linewidth=0.8)
    ax.set_xticks(xs, [_name(k) for k in keys], rotation=15, ha="right")
    ax.set_ylabel("Cohen's kappa vs reference")
    ax.set_ylim(-0.35, 1.12)
    n_ref = summary["n_items"]
    boot = summary["bootstrap"]
    ax.set_title(
        f"Cohen's kappa vs author reference labels (n={n_ref})\n"
        f"Bootstrap percentile 95% CI, {boot['n_boot']} resamples, seed {boot['seed']}.\n"
        "If every item agrees, the interval collapses to [1, 1]."
    )
    ax.legend(bbox_to_anchor=(1.02, 1.0), loc="upper left", fontsize=8, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_categories(summary: dict, path) -> None:
    keys = _judges(summary)
    cats = list(CATEGORIES)
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    x = np.arange(len(cats))
    width = 0.8 / max(len(keys), 1)
    for i, key in enumerate(keys):
        rates = []
        for cat in cats:
            block = summary["judges"][key]["by_category"][cat]
            rates.append(np.nan if block["rate"] is None else block["rate"])
        offset = (i - (len(keys) - 1) / 2) * width
        ax.bar(x + offset, rates, width=width * 0.92, color=COLORS.get(key, "#333333"), label=_name(key))
    labels = []
    # n is a property of the reference set, same for every judge when all items scored.
    # Pull n from the first judge, and if a judge scored a subset the bar still uses that judge's rate.
    ref_n = {}
    first = summary["judges"][keys[0]]["by_category"]
    for cat in cats:
        ref_n[cat] = first[cat]["n"]
        if cat == "correct":
            labels.append(f"correct\nn={ref_n[cat]}\n(judged PASS)")
        else:
            labels.append(f"{cat}\nn={ref_n[cat]}\n(judged FAIL)")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Rate")
    ax.set_title("Per-category agreement with author reference labels\nFAIL categories: share the judge marked FAIL. correct: share the judge marked PASS.")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8, framealpha=0.92)
    ax.axhline(1.0, color="#dddddd", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    IMAGES.mkdir(parents=True, exist_ok=True)
    plot_confusion(summary, IMAGES / "confusion_matrices.png")
    plot_kappa(summary, IMAGES / "kappa_ci.png")
    plot_categories(summary, IMAGES / "category_agreement.png")
    print(f"wrote charts under {IMAGES}")


if __name__ == "__main__":
    main()
