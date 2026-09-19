# ClickPe Product Intelligence Monitor — implementation specification

Source: the user's 90-section project brief in this conversation, dated 2026-09-19. This document preserves its requirements and identifies the delivery boundary; numerical examples in that brief are not measured results.

## Purpose and product boundary

Answer whether ClickPe's public financial-product information is complete, internally consistent, current, and aligned with applicable official provider information. Findings are review items: a difference is not proof of an error or regulatory violation. Preserve possible explanations such as programmes, segments, geography, campaigns, different LSP arrangements, dates, and variants.

Build an automated discovery, collection, normalization, entity/programme mapping, comparison, evidence, history, prioritization, and Streamlit monitoring system. Do not add lending recommendations, credit-risk ML, chat, customer applications, authentication, microservices, or a generic comparison website.

## Delivery scope

1. First working checkpoint: 10–15 actual loan offerings; amount, interest/APR, tenure, lender identity, repayment; evidence; four dashboard views.
2. First complete release: a fixed cohort of 25 actual discovered offerings, expandable to 20–30, from personal loans, business loans, credit lines, and loan against property. Add fees, eligibility, documentation, processing claims, weighted completeness, review priority, source-health and history, provider intelligence, repeatable evaluation, report, and demo.
3. Discover the whole public catalogue, report its category counts, and distinguish that inventory from the monitored cohort. Do not invent products or providers to reach a target. Credit lines may have zero observed offerings. Generic lead-generation entries with unknown providers remain unresolved and reduce coverage.
4. Credit cards, savings/demat schemas, competitors, persona coverage, embeddings/LLMs, and statistical change anomalies are separate future releases. Competitor observations must never serve as authoritative validation.

The live planning inspection is recorded in `docs/research/2026-09-19-source-feasibility.md`. It is a feasibility observation, not a completed pipeline run or labeled evaluation.

## Mandatory data and evidence

- Products: stable product ID, raw/display name, category, raw provider name, resolved provider ID, public ClickPe URL, active state, first/last seen, cohort membership.
- Providers/entities: stable ID, name, legal name, type, regulatory-status claim, registration claim, parent, official website. Regulatory facts remain attributed claims unless independently verified. Brand, LSP, lender, marketplace and parent are different entity roles; alias matching cannot merge them.
- Product/party relationships and source mappings: one product can have several entities/lenders; retain role, evidence, programme/segment/geography, effective dates, review state and rationale.
- Loan terms: amounts/currency; nominal interest range, basis and period; APR range; tenure range and discrete options, source unit and approximate days; repayment frequency/EMI/autopay/eNACH; fees including processing/foreclosure/prepayment/late/stamp/other; eligibility including age/income/turnover/business vintage/score/employment/business/citizenship/residency/location; document requirements; approval/disbursal/application/paperless/instant claims.
- Preserve raw text for every field, including policy-based rates, complex fees, documentation and marketing claims. Unknown is NULL, never zero or false. Marketing copy is not an observed approval time or guarantee.
- Every assertion carries source URL/type, immutable capture ID and content hash, retrieval time, evidence locator/quote, extractor version, confidence and parse state. Every flag links to these assertions. Repeated and contradictory assertions survive extraction.
- Keep raw JSON/HTML/PDF, processed Parquet exports, immutable historical snapshots, SQLite records, collection logs and config/mapping/extractor version provenance.
- Source preference within the same applicable programme: official product page, official terms/KFS, official FAQ, official website. Preserve a contradiction between official sources; do not silently choose a winner. A programme-specific document has stronger applicability than a generic brand page even when the latter ranks higher by source type.
- ClickPe partner/support material is an internal comparison source, never an independent authoritative provider source. Secondary marketplaces cannot improve authoritative-source coverage.

## Normalization and comparison

- Normalize INR strings with Indian grouping and K/L/lakh/crore; preserve units, raw value and lower/upper qualifiers.
- Distinguish annual, monthly, daily and unknown rate periods; distinguish nominal interest, APR, flat/reducing/unknown basis. Do not annualize or equate nominal interest and APR automatically.
- Use Decimal for finance. A bare rate keeps an unknown period. Policy text has no numeric rate.
- Use 365 days/year and 365/12 days/month only as an explicit approximate tenure convention. Preserve original months/years and discrete allowed tenures. Approximate conversion cannot manufacture exact differences.
- Compare only after entity, programme, currency, period, basis, conditional scope and source-health checks. Unreviewed mappings remain ambiguous.
- Statuses: MATCH, DIFFERENT, MISSING_CLICKPE, MISSING_PROVIDER, UNCOMPARABLE, AMBIGUOUS. A missing field is supported absence in a successfully examined scope; a failed or unsupported extractor is not missing information.
- Apply configurable tolerances in matching units. Text rules cover explicit credit-score, age, income, employment and document equivalence. Preserve exceptions such as new-to-credit applicants; do not simplify qualified thresholds to universal requirements.
- Check ClickPe catalogue against partner/support sources and check contradictory claims inside one source. Detect incompatible product-category copy, inverted ranges, incompatible units and role mismatches.

## Monitoring and decisions

- Record VALUE_CHANGED, PRODUCT_ADDED, PRODUCT_REMOVED, SOURCE_DISAPPEARED, FIELD_ADDED and FIELD_REMOVED with previous/current evidence. First run establishes a baseline, not historical change evidence.
- A fetch failure, parse failure, CAPTCHA, empty payload or incomplete catalogue must not remove products/fields or overwrite the last good observation. Cache replays do not refresh retrieval/verification dates. Confirm disappearance on two distinct successful complete observations at least 24 hours apart.
- Freshness bands are project policy: 0–7 days Fresh, 8–30 Monitor, 31–90 Stale, over 90 High priority; unknown stays Unknown. Track fetch, extraction and applicable verification separately.
- Weighted completeness: lender 20%, interest/APR 20%, amount range 15%, fees 15%, tenure 10%, eligibility 10%, repayment 5%, documents 5%. Publish each numerator/denominator and applicability rule. Missing rate period or ambiguous lender cannot earn full credit.
- Rule-based priority 0–100 uses severity, field importance, extraction/mapping confidence and freshness; expose its components. A separate mapping/source-health queue prevents low confidence from burying unresolved identities. Severity Low/Medium/High/Critical indicates urgency, never a legal finding.
- Review outcomes: open, confirmed useful, legitimate programme difference, extraction issue, dismissed, resolved. Preserve notes, reviewer, timestamp and fingerprint; changed evidence reopens a finding. Never auto-claim precision from the presence of flags.

## Dashboard and outputs

- Overview: monitored products/providers/categories, authoritative coverage, comparable fields, review items, high-priority items, recent changes, completeness/freshness, failed sources. Show inventory/cohort and internal/external distinctions.
- Review queue: sortable priorities, category/provider/severity/field/status filters, row detail, both raw/normalized values, URLs, quotes, dates, reason, mapping uncertainty and review action.
- Product explorer: per-field side-by-side comparison, multiple claims, legal entities and LSP links, missingness/parse states, direct source links.
- History: product/provider/time filters and old/new values; real and synthetic runs explicitly separated.
- Provider intelligence: product count, coverage/completeness, review counts and last checked; ranges only where currency/period/programme permit meaningful aggregation. No arbitrary provider ranking.
- Report: 5–10 pages covering inventory, schema, method, measured findings, evidence, data quality, validation, history, limitations and coverage. Competitor section explicitly absent until that release exists.
- Deliver dataset, rerunnable pipeline, genuine historical snapshots when available, documented local Git repository, and a 60–120 second recording following overview → flag → comparison → evidence → history.
- README starts with the business problem and includes architecture, sources, schema, normalization, comparison, dashboard, measured results, validation, limitations and Windows run commands.

## Validation and operating constraints

- Python, SQLite, requests/BeautifulSoup, pandas/Parquet, Streamlit/Plotly, regex and optional RapidFuzz. Browser rendering only when ordinary public HTTP cannot expose required content. SQLite is sufficient; no cloud requirement.
- Local baseline is Windows/PowerShell and Python 3.12.6. Use an isolated project environment; record a reproducible dependency lock. No dependency floors were mandated in the user brief.
- Requests have timeouts, host delays, bounded retries, caching, structured run counters and explicit failures. Respect published robots instructions and source terms; never bypass access controls or CAPTCHA.
- Collect public product/company data only. Do not submit forms, log in, collect customer PAN/phone/financial data, follow private document downloads, or use application validation metadata as publicly displayed loan terms without establishing its display/applicability.
- Default tests are offline. Live collection is an explicit CLI mode. Scheduling is prepared only after replay/persistence works; registration/publication/outreach are separate execution actions, not part of this planning request.
- Gold sample: approximately 20 products × 10 fields, including absence, ambiguity and unsupported cases, labeled against frozen evidence independently of extractor outputs. Keep development and held-out products separate. Numeric extraction target >95%; authoritative-source coverage target ≥90%; conflict precision measured only on explicitly reviewed flags. Report actual sample size, failures and uncertainty, even below target.
- No manufactured findings, histories, provider identities, coverage, accuracy or resume numbers. A clean dashboard and passing unit tests alone are not completion.

## Original-brief coverage index

| Brief sections | Requirement retained here | Implementation-plan tasks |
|---|---|---|
| 1–6, 72–74, 86, 88–90 | Purpose, scope, stages, success boundaries | 1, 6, 12–17 |
| 7–9, 21–23, 65–66, 80 | Public sources, provider mapping, responsible collection | 5–8, 17 |
| 10–20, 49–50, 63 | Entities, loan schema, field provenance, persistence | 1–4, 7–8, 12 |
| 24–29, 55, 75–76 | Normalization and rule-based resolution/extraction | 2–3, 7–8 |
| 30–33, 38–41, 67–68 | Comparisons, internal checks, evidence, neutral findings | 9–10, 13–14 |
| 34–37, 69, 77 | History, freshness, completeness; anomalies deferred | 10–12 |
| 42–48, 70 | Operational dashboard, provider intelligence | 13–14 |
| 51–54 | Structure, configuration, logs, safe failures | 1, 4–6, 12, 16 |
| 56–61 | Independent labels and honest metrics | 15, 17 |
| 62–71, 73 | Staged implementation | 1–17 |
| 9, 48, 71, 78 | Competitor and persona extensions | Explicit future scope; excluded from release 1 |
| 79–80 | Privacy and respectful collection | 5–8, 16–17 |
| 81–85, 87 | Dataset, history, report, repository, demo, measured claims | 12, 15–17 |

