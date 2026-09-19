# Data dictionary

All financial numerics use decimal strings in JSON and Arrow-compatible columns in exports. Datetimes are timezone-aware ISO 8601 values. Every present observation has an immutable capture, SHA-256 hash, URL, exact raw quote, locator, retrieval time, extractor version, context, and confidence.

## Core records

| Record | Stable grain | Purpose |
|---|---|---|
| Product | native `product_id` | Catalogue identity; display-name/provider edits do not create a new product |
| Capture | `capture_id` | One source response in one run, including explicit failure state |
| Observation | `observation_id` | One field assertion, source span, and extraction version |
| Mapping | `mapping_id` | Reviewed product/source/entity/programme applicability |
| Comparison | `comparison_id` | Pairwise or single-source decision with reason code |
| Change | `change_id` | Verified semantic transition between comparable snapshots |

Observation states are `present`, `absent`, `ambiguous`, `unsupported`, and `failed`. `absent` requires a successfully inspected, field-supported scope. Context is one of `offer`, `marketing`, `calculator`, `example`, `form_config`, or `unknown`.

Comparison statuses are `MATCH`, `DIFFERENT`, `MISSING_CLICKPE`, `MISSING_PROVIDER`, `UNCOMPARABLE`, and `AMBIGUOUS`.

## Value semantics

`Value` preserves lower/upper bounds, text, boolean, discrete options, unit, rate period (`annual`, `monthly`, `daily`, `unknown`), rate basis (`flat`, `reducing`, `unknown`), qualifier (`exact`, `range`, `from`, `up_to`, `policy`, `conditional`), and approximation. Unknown is NULL, never zero.

## Field registry

| Group | Fields | Normalized kind/unit |
|---|---|---|
| Amount | `loan_amount` | money/INR |
| Interest | `interest_rate`, `apr` | rate/% with period and basis |
| Tenure | `tenure` | tenure/days; month/year conversion is approximate |
| Lender | `regulated_lender`, `provider_identity` | text |
| Repayment | `repayment_frequency`, `emi_type`, `auto_pay_available`, `enach_available` | text/boolean |
| Fees | `processing_fee`, `foreclosure_fee`, `prepayment_fee`, `late_payment_fee`, `stamp_duty`, `other_charges`, `fees_raw_text` | money/INR or scoped raw text |
| Eligibility | `minimum_age`, `maximum_age`, `minimum_income`, `minimum_turnover`, `minimum_business_vintage`, `minimum_credit_score`, `employment_type`, `business_type`, `citizenship`, `residency`, `location_restrictions` | number, money, tenure, set, or text |
| Documents | `pan_required`, `aadhaar_required`, `bank_statement_months`, `gst_required`, `income_proof_required`, `salary_slip_required`, `business_proof_required`, `address_proof_required`, `documents_raw` | boolean/number/text |
| Processing/claims | `approval_time`, `disbursal_time`, `application_mode`, `paperless`, `instant_disbursal`, `marketing_claim` | tenure/text/boolean |
| Review-only | `category_content` | ambiguous text used by internal checks |

Range fields export one normalized object plus `min_*` and `max_*` convenience columns. Multiple non-equivalent claims leave wide values NULL/ambiguous and retain every linked observation.

