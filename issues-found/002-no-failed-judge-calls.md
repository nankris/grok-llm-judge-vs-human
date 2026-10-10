# 002 — Judge calls

Date: 2026-10-10.

180 Grok calls (full rubric twice, minimal prompt once) and 60 local Qwen calls all returned a parseable `PASS` or `FAIL`. The runner only appends `results/failures.jsonl` on a failed attempt, and that file was never created. No call used the second attempt. No call hit the 600 s Grok timeout or the 180 s local timeout.

Grok run 1 includes two smoke calls (`t01`, `t34`) that the full batch then skipped because the saved verdict and the prompt hash matched. Their raw files are the smoke responses, not a second billed call.

The temp directory listing recorded before each Grok call was empty (`cwd_listing_before: []`).
