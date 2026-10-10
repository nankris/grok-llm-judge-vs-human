# Final summary

Question: on 60 fictional bike-shop tickets, how well does an LLM judge agree with author reference labels written against an explicit policy and rubric?

Sample: n=60. Reference 33 PASS / 27 FAIL (55%, Wilson 95% CI 42.5–66.9%). Not the newsletter's original tickets. Those were cited as 34/60 passing and kappa 0.15 vs a 0.6 bar.

| Judge | n | Accuracy | Kappa (bootstrap 95% CI, 10,000 resamples, seed 0) | Judged PASS |
|---|---|---|---|---|
| Code grader | 60 | 38/60 = 63.3% | 0.22 (0.01–0.43) | 49/60 |
| Grok full rubric, run 1 | 60 | 60/60 = 100% | 1.00 (1.00–1.00) | 33/60 |
| Grok full rubric, run 2 | 60 | 59/60 = 98.3% | 0.97 (0.89–1.00) | 32/60 |
| Grok minimal prompt | 60 | 58/60 = 96.7% | 0.93 (0.83–1.00) | 33/60 |
| Qwen2.5-3B full rubric | 60 | 43/60 = 71.7% | 0.42 (0.19–0.63) | 36/60 |

Full-rubric self-consistency: 59/60, kappa 0.97. The only split is `t14` (run 2 wanted the $70 price difference stated). Minimal-prompt splits: `t02`, `t60`. No unparsed calls. Grok logged cost $1.764 over 180 calls.

Headline: with the policy and the rubric in the prompt, Grok's kappa vs these author labels is about 0.97–1.00, above 0.6, not 0.15. The cheap regex grader (0.22) is the one that misses an invented refund rule when it has no digit, and misses wrong numbers that also appear elsewhere in the policy. A 3B model given the same full prompt lands at 0.42, and its CI reaches 0.6.

Issues: 0 labels changed in the double-check. 0 failed judge calls. Labels are author reference labels, and the item writer and the Grok judge share a model family. Run 1's bootstrap CI has no width; the Wilson interval on that accuracy is 94.0–100%. The newsletter archive page could not be re-fetched here.

Nothing incomplete on the planned judges: full rubric, minimal prompt, second full-rubric run, and the local Qwen run all finished for all 60 items.
