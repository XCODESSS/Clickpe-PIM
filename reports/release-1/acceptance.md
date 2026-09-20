# Release 1 acceptance ledger

This ledger separates implemented/offline-verified software from live research and human review. Synthetic fixtures never count as live evidence. The baseline and replay below were executed on 2026-09-20; two same-day runs do not satisfy the 24-hour history gate.

| Criterion | Outcome | Evidence or remaining work |
|---|---|---|
| Offline architecture and contracts | pass | Full pytest and Ruff gates pass; deterministic replay fixture |
| Discovery adapter | pass (offline) | Duplicate, malformed, inactive, scope, and stable-ID tests |
| Evidence and failure safety | pass (offline) | Immutable-byte, foreign-key, collection-state, and history tests |
| Replay/export | pass | Hash-validated fixture replay plus offline replay of `data/snapshots/live_20260920_release/manifest.json` reproduce 36 products, 25 monitored products, 46 observations, and one comparison |
| Dashboard | pass (synthetic fixture) | Empty states automated; populated overview, queue, evidence, and product views inspected at desktop and 390 px width on 2026-09-19 |
| Backup/restore | pass | Checksummed live-state archive restored to a new directory; SQLite integrity, foreign keys, and run/observation/comparison counts match |
| Reproducible install | pass (local Windows) | Frozen uv sync plus a separate clean Python 3.12 environment imported version 0.1.0 |
| Live discovery and visible catalogue reconciliation | pass | `live_20260920_release` captured 36 in-scope public feed records; rendered catalogue screenshots confirmed all 12 seed titles across Personal Loans, Business Loans, and Loan Against Property |
| Fixed 25-product cohort | pass | `config/cohort.yaml` freezes 25 native IDs against catalogue SHA-256 `4d2d8d294659088d23939cc0eba35cfc0e0fa03cba037d6f9f066575da9397dd` |
| Official coverage and mapping review | not_observable_yet | 0/25 products have an approved same-programme official-source mapping; the existing InCred entry remains a candidate, not an approval |
| Independent gold labels and held-out accuracy | not_observable_yet | Label files are intentionally empty; no metric claimed |
| Reviewed-flag precision | not_observable_yet | One stored review item is unreviewed; no precision is claimed |
| Real history | not_observable_yet | Two healthy same-day captures exist, but the plan requires a later observation after at least 24 hours |
| Analytical report | pass with limitations | Markdown, metrics, and evidence index are generated from the live database; extraction accuracy and review precision are explicitly not measured |
| PDF report and video | not_observable_yet | PDF generation requires measured reviewed results; recording remains outstanding |
| Recurring schedule/publication | not_observable_yet | Remains opt-in and separately authorized |
