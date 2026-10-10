"""Qwen2.5-3B-Instruct judge via the local llama-server OpenAI API."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request

from harness.common import RAW, RESULTS, load_items, load_text
from harness.prompts import build_prompt
from harness.run_judges import prompt_sha

SERVER = "http://127.0.0.1:8091"


def chat(prompt: str, timeout_s: int) -> tuple[int, str]:
    body = {
        "model": "qwen2.5-3b-instruct-q4_k_m",
        "temperature": 0,
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        SERVER + "/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
        return resp.status, raw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rep", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--ids", default="")
    args = parser.parse_args()
    from harness.run_judges import extract_verdict

    items = load_items()
    if args.ids:
        wanted = {part.strip() for part in args.ids.split(",") if part.strip()}
        items = [row for row in items if row["id"] in wanted]
    policy = load_text("policy.md")
    rubric = load_text("rubric.md")
    out_dir = RAW / "qwen-full" / f"rep{args.rep}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"qwen-full rep={args.rep} n={len(items)}", flush=True)
    for i, item in enumerate(items, start=1):
        prompt = build_prompt("full", policy, rubric, item["question"], item["reply"])
        digest = prompt_sha(prompt)
        dest = out_dir / f"{item['id']}.json"
        if dest.exists():
            prior = json.loads(dest.read_text(encoding="utf-8"))
            if prior.get("parsed_verdict") in ("PASS", "FAIL") and prior.get("prompt_sha256") == digest:
                print(f"[{i}/{len(items)}] {item['id']} skip {prior.get('parsed_verdict')}", flush=True)
                continue
        last = None
        for attempt in (1, 2):
            started = time.monotonic()
            record = {
                "id": item["id"],
                "judge": "qwen-full",
                "rep": args.rep,
                "attempt": attempt,
                "prompt_version": "v1",
                "prompt_sha256": digest,
                "temperature": 0,
                "skipped": False,
            }
            try:
                status, raw = chat(prompt, args.timeout)
                record["elapsed_s"] = round(time.monotonic() - started, 3)
                record["returncode"] = 0
                record["http_status"] = status
                record["stdout"] = raw
                record["stderr"] = ""
                wrapper = json.loads(raw)
                text = wrapper["choices"][0]["message"]["content"]
                verdict, reason, err = extract_verdict(text)
                record["parsed_verdict"] = verdict
                record["parsed_reason"] = reason
                record["parse_error"] = err
                record["usage"] = wrapper.get("usage")
            except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                record["elapsed_s"] = round(time.monotonic() - started, 3)
                record["returncode"] = 1
                record["stdout"] = ""
                record["stderr"] = repr(exc)
                record["parsed_verdict"] = None
                record["parsed_reason"] = None
                record["parse_error"] = repr(exc)
            payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
            (out_dir / f"{item['id']}.attempt{attempt}.json").write_text(payload, encoding="utf-8")
            dest.write_text(payload, encoding="utf-8")
            last = record
            if record.get("parsed_verdict") in ("PASS", "FAIL"):
                break
            with (RESULTS / "failures.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(
                    json.dumps(
                        {
                            "id": item["id"],
                            "judge": "qwen-full",
                            "rep": args.rep,
                            "attempt": attempt,
                            "parse_error": record.get("parse_error"),
                        }
                    )
                    + "\n"
                )
        print(
            f"[{i}/{len(items)}] {item['id']} {last.get('parsed_verdict')} "
            f"elapsed={last.get('elapsed_s')} err={last.get('parse_error')}",
            flush=True,
        )


if __name__ == "__main__":
    main()
