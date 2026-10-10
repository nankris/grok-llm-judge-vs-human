# Disagreements with the author reference labels

An item is listed when at least one scored judge, including the code grader, disagrees with the reference label.
Reference labels are author labels against `data/rubric.md`, not independent human labels.
Listed items: 31 of 60.


## t02 reference PASS / correct

Question: I bought a light in the store 20 days ago. It is unused and still in the box. Can I get my money back?

Reply: A full refund is only available within 14 days of an in-store purchase. You are past that window. Store credit is still possible through day 30 if the light is unused and in its original packaging.

Reference rationale: Day 20 is past the 14-day refund and inside the day-30 store-credit window, which is what the reply says.

- grok-minimal/rep1: FAIL. The reply correctly denies a cash refund on day 20 and offers store credit through day 30, but it treats unused condition and original packaging as enough and leaves out the required receipt.
- qwen-full/rep1: FAIL. The reply misses answering the question by not mentioning that the refund policy for in-store purchases starts on the purchase date and is 14 days long. It also incorrectly states the store credit period ends on day 30, when the policy states it ends on day 30 and the customer must return the item within 14 days of the purchase date.

## t05 reference PASS / correct

Question: How much is shipping on a $40 order to Ohio?

Reply: A $40 order is under the $75 free-shipping threshold, so ground shipping is $8.95 and takes 3-5 business days in the continental US. Ohio is included. Express, if you want it, is $18.95 and takes 1-2 business days.

Reference rationale: $40 is the customer's cart total. The $75 threshold, $8.95 ground price, $18.95 express price, and both transit ranges match the policy.

- code: FAIL. dollar:40

## t07 reference PASS / correct

Question: I ordered a bike to my house. Is assembly included?

Reply: Bikes ship unassembled in the carton. Assembly is free only when we build a bike we sold, in the store, before you take it. If you bring a mail-order carton in for us to assemble, that costs $45.

Reference rationale: Shipped bikes are unassembled. In-store assembly of a bike the shop sold is free, and mail-order assembly is $45.

- qwen-full/rep1: FAIL. The reply misses answering the question that the customer asked. The customer specifically inquired about assembly when the bike is shipped to their house. The reply only mentions assembly costs for mail-order bikes and does not address the assembly of a bike shipped directly to the customer's house.

## t14 reference PASS / correct

Question: What is the price difference between a basic tune-up and a full service?

Reply: A basic tune-up is $79. A full service is $149. Parts are extra on both.

Reference rationale: Both labor prices match the repair list, and parts are extra unless a line says otherwise.

- grok-full/rep2: FAIL. The $79 tune-up, $149 full service, and extra-parts note match the policy, but the reply never states the price difference the customer asked for ($70).

## t16 reference PASS / correct

Question: How much is a city bike rental for 3 days?

Reply: A city bike is $35 for the first day and $25 for each additional day. Three days is $35 + $25 + $25, which is $85. A helmet is included. We place a $100 card hold, which is not charged unless the bike is damaged beyond normal wear or returned late. The renter must be 18 or older with a government photo ID.

Reference rationale: The day rates match. $85 is 35+25+25. Helmet, hold, and age match. The extra facts are true.

- code: FAIL. dollar:85

## t18 reference PASS / correct

Question: What do I owe if I bring a city bike back two hours late?

Reply: The late fee is $20 per hour, capped at one additional day's rental rate. Two hours would be $40, but the city-bike cap is $25, so the late fee is $25.

Reference rationale: The hourly rate is $20 and the city-bike cap is $25. $40 is two times $20 before the cap, and the reply applies the cap.

- code: FAIL. dollar:40

## t23 reference PASS / correct

Question: If I buy a gift card and the person does not want it, can they get cash back?

Reply: No. Gift cards are not refundable.

Reference rationale: Gift cards cannot be refunded. The short wording is not rude.

- qwen-full/rep1: FAIL. The reply misses answering the question. It does not mention gift cards or cash back, which is the customer's second part of the question.

## t24 reference PASS / correct

Question: I ordered a custom build and changed my mind before pickup. Can I cancel for a refund?

Reply: No. Custom builds are not eligible for a refund or for store credit.

Reference rationale: Custom builds are excluded. The reply does not invent a cancellation fee.

- qwen-full/rep1: FAIL. invented_fact

## t26 reference PASS / correct

Question: The jacket does not fit. I paid $8.95 for ground shipping. Will you refund that shipping and send me a label?

Reply: You can return an unused jacket in its original packaging within 14 days for a refund of the jacket. On a fit return, you pay the return shipping, and that cost is not reimbursed. The $8.95 outbound shipping is refunded only when we shipped the wrong item or a defective one, so it is not refunded here.

Reference rationale: A fit return can use the 14-day unused-item rule. The customer pays return shipping, and outbound shipping is refunded only for wrong or defective shipments.

- qwen-full/rep1: FAIL. The reply misses the customer's question about refunding the $8.95 shipping cost and instead focuses on the 14-day return window and the refund policy for the jacket itself. It also incorrectly states that the $8.95 outbound shipping is refunded only in specific cases, which is not a correct interpretation of the policy.

## t31 reference PASS / correct

Question: If a tune-up uncovers a lot of worn parts, will you just install them?

Reply: A basic tune-up is $79, with parts extra. We will not start extra parts totaling more than $50 without asking you first.

Reference rationale: The tune-up price and the more-than-$50 extra-parts approval rule both match.

- qwen-full/rep1: FAIL. unsafe_promise

## t33 reference PASS / correct

Question: Do you buy used bikes for cash?

Reply: Used-bike buying is not in our support policy, so I cannot offer a purchase price or a trade-in. We can still do a paid repair. A basic tune-up is $79 and a full service is $149, and parts are extra.

Reference rationale: The policy says not to invent a used-bike purchase price. The repair prices that are quoted are the listed ones.

- qwen-full/rep1: FAIL. invented_fact

## t36 reference FAIL / wrong_number

Question: My cart is $60. Is ground shipping free?

Reply: Yes. Ground shipping is free on orders of $50 or more.

Reference rationale: Free ground shipping starts at $75 before tax, so a $60 cart is not free. $50 is not the threshold.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply correctly states that ground shipping is free on orders of $50 or more, which matches the policy.

## t37 reference FAIL / wrong_number

Question: What does ground shipping cost, and how long does it take?

Reply: Ground shipping is $12.95 and takes 3-5 business days in the continental US.

Reference rationale: The 3-5 business day range is right, but ground shipping is $8.95, not $12.95.

- qwen-full/rep1: PASS. The reply answers the question and matches the policy without inventing facts or promises.

## t38 reference FAIL / wrong_number

Question: How much to fix a flat?

Reply: A flat repair is $25, and that includes a standard tube.

Reference rationale: Flat repair is $15 with a standard tube. $25 is the per-wheel brake-pad price, not the flat price.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply matches the policy, answers the question, and does not invent any facts or promises that are forbidden.

## t39 reference FAIL / wrong_number

Question: How long is the frame warranty?

Reply: Frames we sell are warranted for 2 years against manufacturing defects.

Reference rationale: Frame warranty is 5 years from purchase, not 2 years.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply matches the policy and answers the question. It does not invent any facts or promises that are forbidden by the policy.

## t40 reference FAIL / wrong_number

Question: Are you open Saturday afternoon?

Reply: Yes. Saturday we are open 09:00-18:00.

Reference rationale: Saturday hours are 09:00-16:00. 18:00 is the Tuesday-Friday close, not Saturday's.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply correctly states the shop's hours for Saturday and does not add any invented facts or promises.

## t41 reference FAIL / wrong_number

Question: How much is the e-bike rental per day?

Reply: An e-bike is $45 per day. A helmet is included, and we place a $200 card hold. The renter must be 18 or older.

Reference rationale: The e-bike rate is $65 per day, not $45. $45 is the mail-order assembly fee. The hold, helmet, and age are right, but the rental price is wrong.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply answers the question, matches the policy, and does not invent any facts or promises.

## t45 reference FAIL / invented_fact

Question: Does a new bike include any ongoing service plan?

Reply: Yes. Every new bike includes one free tune-up each year for as long as you own it.

Reference rationale: No annual free tune-up plan is in the policy. A basic tune-up is a $79 paid job.

- code: PASS. (no flags)

## t46 reference FAIL / invented_fact

Question: Can you ship a helmet to Canada?

Reply: Yes. We ship to Canada for a flat $25 international fee, and it takes about 10 business days.

Reference rationale: The shop does not ship outside the United States. The Canada service, the $25 fee, and the 10-day transit time are invented.

- code: PASS. (no flags)

## t48 reference FAIL / invented_fact

Question: I bought a bell in the store on the 2nd, and today is the 28th of the same month. It is unused. Can I still return it?

Reply: Yes. You can return unused items any time in the same calendar month.

Reference rationale: The real rules are a 14-day refund and store credit through day 30. From the 2nd to the 28th is past 14 days and still inside 30 days, so store credit could apply, but a same-calendar-month rule is not the policy.

- code: PASS. (no flags)

## t49 reference FAIL / missed_question

Question: Are you open Saturday, and how much is a flat repair?

Reply: Saturday we are open 09:00-16:00.

Reference rationale: Saturday hours are correct, but the flat-repair price of $15 is never answered.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply correctly states the shop's hours for Saturday and provides the flat repair price without adding any fees or promises that are not in the policy.

## t50 reference FAIL / missed_question

Question: Can I return an unused water bottle I bought in the store five days ago, and what would ground shipping cost on a separate $20 parts order?

Reply: An unused water bottle in its original packaging can be refunded within 14 days, and five days ago is inside that window.

Reference rationale: The refund half is correct. Ground shipping on a $20 order, which is $8.95 because it is under $75, is not answered.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply matches the policy, answers the question, and does not invent, promise forbidden actions, or use unsafe language.

## t51 reference FAIL / missed_question

Question: What is the component warranty, and does it cover a crash?

Reply: Components we sell are covered for 1 year from purchase.

Reference rationale: The 1-year length is correct. The crash question is unanswered, and crash damage is excluded.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply matches the policy regarding component warranty and does not invent any facts or promises.

## t52 reference FAIL / missed_question

Question: How much is a city bike for one day, and can a 17-year-old rent it?

Reply: A city bike is $35 for the first day, and a helmet is included.

Reference rationale: The one-day price and the included helmet are correct. Whether a 17-year-old can rent is not answered.

- code: PASS. (no flags)

## t53 reference FAIL / missed_question

Question: Do you ship to Alaska, and what does express shipping cost if I stay in the continental US?

Reply: We do not ship to Alaska.

Reference rationale: The Alaska answer is correct. Express shipping, which is $18.95 and 1-2 business days, is not answered.

- code: PASS. (no flags)

## t54 reference FAIL / unsafe_promise

Question: This clearance helmet itches. Can I get a refund?

Reply: Yes. Bring sale items back within 14 days and we will refund those too.

Reference rationale: The 14-day figure matches the normal window, but sale and clearance items cannot be refunded. The reply promises a refund the policy forbids.

- code: PASS. (no flags)

## t55 reference FAIL / unsafe_promise

Question: I have rented from you before. Can you skip the card hold on a city bike this time?

Reply: Of course. We will waive the card hold for a returning renter.

Reference rationale: Staff must not waive the rental card hold. The city-bike hold is $100.

- code: PASS. (no flags)
- qwen-full/rep1: PASS. The reply answers the question and does not invent any facts or promises that are forbidden by the policy.

## t57 reference FAIL / unsafe_promise

Question: If the frame cracks in year 8 from a manufacturing defect, am I covered?

Reply: Yes. Our frames are covered for life, so year 8 is included.

Reference rationale: Frame coverage is 5 years, not for life. The reply tells the customer that year 8 is covered, which the warranty forbids.

- code: PASS. (no flags)

## t58 reference FAIL / unsafe_promise

Question: After you straighten the wheel I crashed, will the bike be as good as new?

Reply: Yes. We guarantee the crash repair will make it like new and safe to race.

Reference rationale: The shop must not guarantee that a repair will make a bike like new, race-ready, or safe for a particular event.

- code: PASS. (no flags)

## t59 reference FAIL / tone

Question: What is your refund window?

Reply: Unused items in the original packaging with a receipt can be refunded within 14 days of the in-store purchase date, or within 14 days of delivery if we shipped the item. Try reading the receipt next time instead of making us repeat ourselves.

Reference rationale: The 14-day unused-item rule is right, but the second sentence insults the customer. Rudeness fails the reply even though the facts hold.

- code: PASS. (no flags)

## t60 reference FAIL / tone

Question: Is ground shipping free on orders over $75?

Reply: Obviously yes. Ground shipping is free on merchandise of $75 or more before tax. Not sure why that is confusing.

Reference rationale: Free ground shipping at $75 before tax is correct, but the reply is sarcastic at the customer's expense.

- code: PASS. (no flags)
- grok-minimal/rep1: PASS. The reply correctly states that ground shipping is free on merchandise of $75 or more before tax, matching the shop policy without adding fees, services, or exceptions.
