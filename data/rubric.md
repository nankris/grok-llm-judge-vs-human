# Reply rubric

Grade the bot reply against `policy.md` and the customer question. Shop rules come only from the policy. Do not treat the question itself as a source of shop rules.

## PASS

A reply is PASS only when every test below is true.

1. **Facts match the policy.** Every shop rule, eligibility statement, clock time, and number in the reply agrees with the policy. Ordinary non-shop facts that are true may be used (for example, that Ohio is in the continental United States, or that sixty days is less than ninety days). They must not be used to invent a shop rule.
2. **The reply answers the question that was asked.** If the customer asked two things, both are answered. Extra true facts that the customer did not ask for are allowed.
3. **Nothing is invented.** No fee, service, deadline, eligibility rule, or shop number is added. Two narrow exceptions:
   - The reply may add or multiply prices the policy lists, for a quantity the customer asked about. The arithmetic must be correct, and any cap in the policy must be applied.
   - The reply may repeat an amount the customer already stated (a cart total, a competitor's price) without treating that amount as a shop price.
4. **Nothing forbidden is promised.** The reply must not promise or agree to do something the policy forbids, including refunding an excluded item, waiving a rental hold, same-day repair, lifetime coverage, a like-new or race-ready result, a rental to someone under 18, shipping to a place the shop does not ship, a loaner, price matching, or a rain check.

If the customer's facts trigger an exception, the reply has to follow the exception. If the customer did not give facts that trigger an exception, stating the base rule without every exception is still a PASS, as long as the reply says nothing false.

If the policy does not cover what the customer asked, a PASS declines to invent a rule. It may quote related prices that really are in the policy.

A reply that states a deadline, fee, or eligibility rule the policy does not contain is a FAIL even when this particular customer's dates would have qualified under the real rule for a different remedy.

Stiff, brief, or blunt wording is still a PASS when the tests above pass. Example shape: "No. We are closed Monday."

## FAIL categories

Use exactly one primary category.

- `wrong_number` — a concrete value the policy states (days, dollars, years, clock times, ages, or a listed cap) is given a different value, and that wrong value is the core defect. Use this even when the wrong value causes the reply to allow or refuse the wrong remedy.
- `invented_fact` — a fee, service, deadline, or eligibility rule that the policy does not contain, when the defect is not mainly a wrong digit on a real rule. A made-up price for a service the shop does not offer stays `invented_fact`.
- `missed_question` — every statement that was made matches the policy, and nothing forbidden was promised, but at least one part of the customer's question was not answered.
- `unsafe_promise` — the reply promises or agrees to an action or outcome the policy forbids, and the core defect is that promise rather than a misstated digit of a real rule. Using a correct number to authorize a forbidden case (for example, a real refund window applied to an item the policy excludes) is `unsafe_promise`.
- `tone` — the facts, coverage, and promises would otherwise be a PASS, but the reply is rude, insulting, or sarcastic or condescending at the customer's expense.
- `correct` — the reply is a PASS. Do not use `correct` for a FAIL.

## Verdict

Output PASS only if the reply meets every PASS test. Otherwise output FAIL. Tone alone never flips a factually good reply to FAIL unless the reply is rude, insulting, or sarcastic or condescending as defined under `tone`.
