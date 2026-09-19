# Validation protocol

## Frozen source sample

Select approximately 20 fixed-cohort products before reading extractor output. Keep all sources for a product in one split: 10 development products and 10 held-out products. Cover categories, amount formats, rate periods, ambiguity, absence, and source failures.

Label these fields where applicable: loan amount, nominal interest, APR, tenure, regulated lender, repayment frequency, processing fee, minimum credit score, income or business vintage, and documents. Every label needs a source hash, locator, exact quote, state, normalized expectation, conditions, rationale, labeler, and timestamp. A second reviewer checks all held-out labels and every high/critical review item.

## Evaluation rules

- Predictions join on product, source, capture, and field.
- Missing predictions count as incorrect; they are not removed from the denominator.
- Numeric correctness requires bound, unit, period, basis, qualifier, conditions, and tenure-approximation agreement.
- Contradictory duplicate predictions are incorrect unless the independent label is ambiguous and the assertion set matches.
- Report counts and Wilson 95% intervals, not percentages alone.
- Flag precision uses only explicitly reviewed flags. Unreviewed flags remain visible outside that denominator.
- If held-out inspection causes rule changes, treat it as development feedback and obtain a fresh held-out set before claiming a test result.

## Live release gates

1. Capture the full feed and reconcile at least the seeded titles against the visible catalogue/modal presentation.
2. Freeze 25 actual stable IDs or document an availability shortfall without replacing hard cases.
3. Review every product/source/programme mapping with capture evidence and a named reviewer.
4. Run the complete offline suite, then replay the finalized live manifest with networking disabled.
5. Take a second real observation at least 24 hours later. Report “no changes observed” when appropriate.
6. Verify every reported flag resolves to captured bytes and exact observations.
7. Render and visually inspect every PDF page and verify source links.
8. Record actual denominators and shortfalls in the acceptance ledger.

Targets (>95% held-out numeric extraction and at least 90% applicable official-source coverage) are goals, not permission to alter the cohort or labels.

