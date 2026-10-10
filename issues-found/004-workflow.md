# 004 — Workflow notes

## Archive page

`https://archive.codenewsletter.ai/2106453816757354947` could not be fetched from this environment (the client blocked it as a private address). The newsletter claim in the README is the claim this experiment was asked to test, not a re-read of the article body, and not a rescore of the original 60 tickets.

## Bootstrap interval on a perfect run

Grok full run 1 agreed on 60/60, so every bootstrap resample also agrees and the 95% interval is [1, 1]. The chart says so. The Wilson interval on accuracy (94.0–100%) is the interval that still leaves room for a miss on a new sample. Both numbers are in `results/summary.json`.

## Token totals are not the prompt length

Qwen logged about 2,260 prompt tokens per call, which matches the policy + rubric + question + reply. Grok's `input_tokens` averaged about 12,000 on run 1. The CLI wraps the user prompt. The README reports the logged totals and does not try to subtract a system prompt that the raw `usage` object does not break out.

## Same model family

Items were written in this session, then double-checked by the same session, then judged by `grok-4.7`. High agreement is expected to be inflated relative to a separate human rater. Qwen2.5-3B is the different-family check in this repo (kappa 0.42).

## Local server

`llama-server` was started with `-ngl 0` in addition to the requested `-np 1 -c 8192 -t 6 --port 8091`, so weights stayed on CPU. It warned that no API key was set and CORS allowed all origins. The server listened on 127.0.0.1 only. It was left running until the local 60 calls finished.
