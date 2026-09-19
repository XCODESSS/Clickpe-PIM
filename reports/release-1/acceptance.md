# Release 1 acceptance ledger

This ledger separates implemented/offline-verified software from live research that has not been performed. Synthetic fixtures never count as live evidence.

| Criterion | Outcome | Evidence or remaining work |
|---|---|---|
| Offline architecture and contracts | pass | 60 pytest checks and Ruff pass; deterministic replay fixture |
| Discovery adapter | pass (offline) | Duplicate, malformed, inactive, scope, and stable-ID tests |
| Evidence and failure safety | pass (offline) | Immutable-byte, foreign-key, collection-state, and history tests |
| Replay/export | pass | Hash-validated network-free fixture produces SQLite, CSV, Parquet, metrics, and evidence index |
| Dashboard | pass (synthetic fixture) | Empty states automated; populated overview, queue, evidence, and product views inspected at desktop and 390 px width on 2026-09-19 |
| Backup/restore | pass (offline) | SQLite backup, checksummed archive, round trip, and traversal rejection |
| Reproducible install | pass (local Windows) | Frozen uv sync plus a separate clean Python 3.12 environment imported version 0.1.0 |
| Live discovery and visible catalogue reconciliation | not_observable_yet | Requires approved live run and collaborative browser review |
| Fixed 25-product cohort | not_observable_yet | `config/cohort.yaml` intentionally remains unfrozen |
| Official coverage and mapping review | not_observable_yet | Candidate mappings are not approvals |
| Independent gold labels and held-out accuracy | not_observable_yet | Label files are intentionally empty; no metric claimed |
| Reviewed-flag precision | not_observable_yet | Requires human review outcomes |
| Real history | not_observable_yet | Requires a second healthy live observation after at least 24 hours |
| PDF report and video | not_observable_yet | Requires measured live results and visual/recording QA |
| Recurring schedule/publication | not_observable_yet | Remains opt-in and separately authorized |
