# 001 — Reference-label double-check

Date: 2026-10-10.

## What was checked

`harness/audit_labels.py` printed all 60 items with the dollar amounts and other numbers in each reply, the code-grader flags, and the policy lines that mention those numbers. Every item was then re-read against `data/policy.md` and `data/rubric.md`.

## Labels changed in that pass

**0 verdicts and 0 categories changed.**

The pass/fail mix stayed 33 PASS / 27 FAIL. Category counts stayed wrong_number 8, invented_fact 7, missed_question 5, unsafe_promise 5, tone 2, correct 33.

## Wording fixes in the same pass

Two rationales were rewritten so the one-line note matched the reply that was actually on the page. The verdict and category did not change.

- `t09`: the rationale still talked about a deleted sentence that refused to approve a warranty claim before inspection. The reply that was reviewed only says to bring the bike in so the shop can inspect whether the skip is a manufacturing defect. Still PASS / correct.
- `t21`: the rationale implied the reply repeated the customer's "$10 cheaper" figure. The reply does not quote $10. It only refuses price matching, competitor coupons, and rain checks. Still PASS / correct.

## Calls that were checked and left as written

- Derived totals stay PASS: two brake wheels at $25 are $50 (`t13`), three city-bike days are $85 (`t16`), derailleur plus wheel true is $65 (`t30`), two late hours at $20 would be $40 and then the $25 city cap applies (`t18`). The rubric allows correct arithmetic on listed prices.
- `t34` stays wrong_number, not unsafe_promise. The rubric says a wrong digit is wrong_number even when it causes the wrong remedy (30-day card refund at three weeks, instead of store credit).
- `t36`, `t38`, and `t41` stay wrong_number even though $50, $25, and $45 appear somewhere else in the policy. The reply uses them as the wrong rule.
- `t46` stays invented_fact. Canada shipping is not a service, so the made-up $25 fee does not get reclassified as wrong_number.
- `t48` stays invented_fact. From the 2nd to the 28th is past 14 days and inside 30 days, so store credit could apply, but the reply states a calendar-month rule the policy does not contain. The rubric says that is a FAIL even when a different real remedy would have covered this customer.
- `t54` stays unsafe_promise. The 14-day number is real, and the reply uses it to refund a clearance item.
- `t57` stays unsafe_promise. "Covered for life, so year 8 is included" grants coverage the 5-year frame warranty forbids.
- `t59` and `t60` stay tone. The facts match (14-day clock from purchase or delivery; free ground shipping at $75 or more before tax). The second sentence of each reply is insulting or sarcastic. Blunt correct replies such as `t23` stay PASS.

## Code grader, from the same read

Not a label change. Recorded here so the misses are tied to items, not discovered after the scores:

- False FAIL on correct replies that contain a dollar amount the policy does not list: `t05` ($40 cart), `t16` ($85 total), `t18` ($40 before the late cap).
- Misses wrong numbers whose digits exist under a different rule: `t36` ($50 threshold; $50 is the parts cap), `t38` (flat priced at $25), `t41` (e-bike priced at $45).
- Misses non-dollar errors and anything with no digit: 2-year frame (`t39`), Saturday close 18:00 (`t40`), free annual tune-up (`t45`), Canada shipping (`t46`), calendar-month returns (`t48`), every missed-question item, sale-item refund (`t54`), waived hold (`t55`), lifetime frame (`t57`), like-new promise (`t58`), both tone failures.
- Catches the 30-day and 10-day refund wording, the $12.95 ground price, and the affirmative restocking / price-match / loaner / rain-check / same-day phrases.
