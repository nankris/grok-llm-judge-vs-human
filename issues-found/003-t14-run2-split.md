# 003 — Full-rubric run 2 failed `t14`

`t14` asks: "What is the price difference between a basic tune-up and a full service?"

The reply says a basic tune-up is $79, a full service is $149, and parts are extra. It does not say the difference is $70. Both prices match `data/policy.md`. $149 − $79 = $70.

- Reference label, frozen before the judge runs: PASS / correct.
- Grok full rubric, run 1: PASS.
- Grok full rubric, run 2: FAIL. The reason says the reply never states the $70 difference the customer asked for.
- Grok minimal: PASS.
- Qwen full rubric: PASS.

This is the only item where the two full-rubric runs disagree, and the only full-rubric miss against the reference. Run 2 has a real reading of "answers the question." The label was not changed after the run. Editing it to match run 2 would fit the reference to a judge that had already spoken.

Self-consistency is 59/60. Because run 1 matched the reference on every item, kappa between the two runs equals kappa between run 2 and the reference (0.97, bootstrap 95% CI 0.89–1.00, seed 0). That equality is arithmetic, not a second independent result.
