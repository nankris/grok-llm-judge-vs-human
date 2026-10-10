"""Run Grok judges in a fresh empty temp directory so labels are not on disk there."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from harness.common import RAW, RESULTS, load_items, load_text

FAIL_LOCK = threading.Lock()
from harness.prompts import JUDGE_SCHEMA, build_prompt

GROK = os.path.expanduser("~/.grok/bin/grok")
PROMPT_VERSION = "v1"


def prompt_sha(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def extract_verdict(text: str) -> tuple[str | None, str | None, str | None]:
    """Return verdict, reason, error from model text."""
    if text is None:
        return None, None, "empty text"
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    candidates = [raw]
    decoder = json.JSONDecoder()
    for i, ch in enumerate(raw):
        if ch != "{":
            continue
        try:
            obj, _end = decoder.raw_decode(raw[i:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "verdict" in obj:
            candidates.append(obj)
            break
    for cand in candidates:
        obj = cand
        if isinstance(cand, str):
            try:
                obj = json.loads(cand)
            except json.JSONDecodeError:
                continue
        if not isinstance(obj, dict):
            continue
        verdict = str(obj.get("verdict", "")).strip().upper()
        if verdict not in ("PASS", "FAIL"):
            continue
        reason = obj.get("reason", "")
        reason = "" if reason is None else str(reason).strip()
        return verdict, reason, None
    return None, None, "no PASS/FAIL verdict in model text"


def parse_wrapper(stdout: str) -> tuple[dict | None, str | None]:
    stdout = stdout.strip()
    if not stdout:
        return None, "empty stdout"
    try:
        obj = json.loads(stdout)
    except json.JSONDecodeError:
        start = stdout.find("{")
        end = stdout.rfind("}")
        if start < 0 or end <= start:
            return None, "stdout is not JSON"
        try:
            obj = json.loads(stdout[start : end + 1])
        except json.JSONDecodeError as exc:
            return None, f"stdout JSON failed: {exc}"
    if not isinstance(obj, dict):
        return None, "stdout JSON is not an object"
    return obj, None


def judge_one(item: dict, judge: str, rep: int, policy: str, rubric: str, timeout_s: int) -> dict:
    config = "full" if judge.endswith("full") else "minimal"
    prompt = build_prompt(config, policy, rubric, item["question"], item["reply"])
    digest = prompt_sha(prompt)
    out_dir = RAW / judge / f"rep{rep}"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{item['id']}.json"
    if dest.exists():
        try:
            prior = json.loads(dest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior = None
        if prior and prior.get("parsed_verdict") in ("PASS", "FAIL") and prior.get("prompt_sha256") == digest:
            prior["skipped"] = True
            return prior

    schema = json.dumps(JUDGE_SCHEMA, separators=(",", ":"))
    last: dict | None = None
    for attempt in (1, 2):
        cwd = tempfile.mkdtemp(prefix="llm-judge-", dir="/tmp")
        # The directory stays empty. The prompt is passed as an argument, not as a file
        # the model is invited to browse, and labels are not copied in.
        started = time.monotonic()
        cmd = [
            GROK,
            "-p",
            prompt,
            "--always-approve",
            "--output-format",
            "json",
            "--cwd",
            cwd,
            "--disable-web-search",
            "--no-subagents",
            "--max-turns",
            "3",
            "-m",
            "grok-4.7",
            "--json-schema",
            schema,
        ]
        record: dict = {
            "id": item["id"],
            "judge": judge,
            "rep": rep,
            "attempt": attempt,
            "prompt_version": PROMPT_VERSION,
            "prompt_sha256": digest,
            "cwd": cwd,
            "cwd_listing_before": sorted(os.listdir(cwd)),
            "skipped": False,
        }
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            record["elapsed_s"] = round(time.monotonic() - started, 3)
            record["returncode"] = proc.returncode
            record["stdout"] = proc.stdout
            record["stderr"] = proc.stderr
            wrapper, wrap_err = parse_wrapper(proc.stdout)
            record["wrapper_error"] = wrap_err
            if wrapper:
                record["usage"] = wrapper.get("usage")
                record["num_turns"] = wrapper.get("num_turns")
                record["total_cost_usd"] = wrapper.get("total_cost_usd")
                record["model"] = wrapper.get("model") or wrapper.get("model_id")
                model_usage = wrapper.get("modelUsage")
                if isinstance(model_usage, dict) and model_usage:
                    record["model"] = next(iter(model_usage))
                text = wrapper.get("text")
                if not isinstance(text, str):
                    text = json.dumps(text) if text is not None else ""
            else:
                text = ""
            verdict, reason, parse_error = extract_verdict(text)
            record["parsed_verdict"] = verdict
            record["parsed_reason"] = reason
            record["parse_error"] = parse_error
            if proc.returncode != 0 and parse_error is None:
                record["parse_error"] = record["parse_error"] or f"returncode {proc.returncode}"
        except subprocess.TimeoutExpired as exc:
            record["elapsed_s"] = round(time.monotonic() - started, 3)
            record["returncode"] = None
            record["stdout"] = exc.stdout or ""
            record["stderr"] = exc.stderr or ""
            record["parsed_verdict"] = None
            record["parsed_reason"] = None
            record["parse_error"] = f"timeout after {timeout_s}s"
        finally:
            shutil.rmtree(cwd, ignore_errors=True)
        payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
        (out_dir / f"{item['id']}.attempt{attempt}.json").write_text(payload, encoding="utf-8")
        dest.write_text(payload, encoding="utf-8")
        last = record
        if record.get("parsed_verdict") in ("PASS", "FAIL"):
            break
        fail_path = RESULTS / "failures.jsonl"
        fail_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "id": item["id"],
                "judge": judge,
                "rep": rep,
                "attempt": attempt,
                "parse_error": record.get("parse_error"),
                "returncode": record.get("returncode"),
                "elapsed_s": record.get("elapsed_s"),
            }
        )
        with FAIL_LOCK:
            with fail_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        if attempt == 1:
            time.sleep(15)
    return last or {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", required=True, choices=("grok-full", "grok-minimal"))
    parser.add_argument("--rep", type=int, default=1)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--ids", default="", help="Comma-separated ids. Default: all.")
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 2:
        raise SystemExit("workers must be 1 or 2 (shared plan quota)")

    items = load_items()
    if args.ids:
        wanted = {part.strip() for part in args.ids.split(",") if part.strip()}
        items = [row for row in items if row["id"] in wanted]
        missing = wanted - {row["id"] for row in items}
        if missing:
            raise SystemExit(f"unknown ids: {sorted(missing)}")
    policy = load_text("policy.md")
    rubric = load_text("rubric.md")
    sample = items[0]
    config = "full" if args.judge.endswith("full") else "minimal"
    sample_prompt = build_prompt(config, policy, rubric, sample["question"], sample["reply"])
    prompt_dir = RESULTS / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    (prompt_dir / f"{args.judge}.txt").write_text(sample_prompt, encoding="utf-8")
    print(f"judge={args.judge} rep={args.rep} n={len(items)} workers={args.workers}", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [
            pool.submit(judge_one, item, args.judge, args.rep, policy, rubric, args.timeout)
            for item in items
        ]
        for fut in as_completed(futures):
            record = fut.result()
            done += 1
            print(
                f"[{done}/{len(items)}] {record.get('id')} {record.get('parsed_verdict')} "
                f"attempt={record.get('attempt')} elapsed={record.get('elapsed_s')} "
                f"skipped={record.get('skipped')} err={record.get('parse_error')}",
                flush=True,
            )
    print("done", flush=True)


if __name__ == "__main__":
    main()
