# ClickPe Product Intelligence Monitor

ClickPe publishes loan-product information across a public catalogue and disclosure pages. The same product may also appear on a lender or intermediary website with different scope, timing, units, or wording. This project turns those public statements into traceable observations and neutral review items. A difference is not proof of an error or a regulatory violation.

The repository delivers the offline-tested software release plus a bounded public baseline captured on 2026-09-20. That run found 36 in-scope public feed records and froze a 25-product cohort; all 12 seed titles were reconciled against the rendered Personal Loans, Business Loans, and Loan Against Property catalogue pages. It does **not** include approved human programme mappings, a gold-label accuracy result, 24-hour history, a PDF report, or a demo video. Those acceptance items require independent review or elapsed time; their status is recorded in `reports/release-1/acceptance.md`.

## Architecture

The synchronous pipeline performs:

1. policy-aware public GET collection or hash-validated offline replay;
2. immutable capture storage with SHA-256 evidence;
3. strict catalogue discovery and a fixed cohort;
4. field extraction with raw quotes, locators, source context, and parse state;
5. reviewed entity/programme mapping;
6. semantic comparison after currency, rate-period, basis, condition, and mapping gates;
7. transactional SQLite persistence and atomic CSV/Parquet snapshot publication;
8. read-only Streamlit queries, review events, evaluation, reporting, and backup/restore.

Unknown, absent, unsupported, ambiguous, and failed are separate states. Failed collection never becomes a product removal or a freshly verified value. Synthetic fixtures are excluded from dashboard totals unless explicitly enabled.

## Windows setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src app tests scripts
```

With `uv`:

```powershell
uv sync --frozen --extra dev
uv run --frozen --extra dev pytest -q
```

Python 3.12 is required. Runtime output is ignored by Git.

## Deterministic offline replay

```powershell
.\.venv\Scripts\python.exe -m clickpe_pim run `
  --mode replay `
  --manifest tests/fixtures/catalogue/replay-manifest.json `
  --output-root .artifacts/replay `
  --run-id fixture_r1
```

The fixture contains two synthetic products, one matching amount, and one deliberate amount difference. Its approved mappings exist only inside the test manifest and must never be copied into live configuration. Replay validates every capture hash and performs no network request.

Outputs include an SQLite database, immutable raw evidence, a versioned snapshot, `products.parquet`, normalized observation datasets, comparisons, changes, source mappings, metrics, and an evidence index.

## Live collection

```powershell
.\.venv\Scripts\python.exe -m clickpe_pim run --mode live --config config.yaml --output-root .
```

Live mode checks ClickPe's current robots policy, uses bounded HTTPS collection, and discovers the catalogue feed. It does not approve candidate provider mappings. Before treating a live run as a release, complete the mapping, source-terms, visual catalogue, label, history, and evidence review in the validation protocol.

The frozen baseline run ID is `live_20260920_release`. Its local database, source bytes, and snapshots are ignored runtime artifacts. The committed cohort records the 25 selected native IDs and the catalogue capture hash; repeat runs must keep that cohort stable.

## Dashboard

```powershell
$env:CLICKPE_PIM_DB = "data/db/monitor.sqlite"
.\.venv\Scripts\python.exe -m streamlit run app/dashboard.py
```

For the synthetic fixture only, set `CLICKPE_PIM_INCLUDE_SYNTHETIC=1`. A permanent banner identifies synthetic data.

The five views are the overview, review queue, product explorer, change history, and provider intelligence. Review events append to an audit trail and do not overwrite evidence.

## Evaluation and report

```powershell
.\.venv\Scripts\python.exe -m clickpe_pim evaluate `
  --db data/db/monitor.sqlite --labels data/gold/labels.jsonl `
  --split test --output reports/release-1/evaluation.json

.\.venv\Scripts\python.exe -m clickpe_pim report `
  --db data/db/monitor.sqlite --evaluation reports/release-1/evaluation.json `
  --output-dir reports/release-1
```

Empty labels produce “not measured,” never a passing accuracy claim. Metrics include their denominators and Wilson intervals where applicable.

## Backup and restore

```powershell
.\.venv\Scripts\python.exe scripts/backup.py `
  --db data/db/monitor.sqlite --data-root data --archive data/backups/state.zip

.\.venv\Scripts\python.exe scripts/restore.py `
  --archive data/backups/state.zip --destination .artifacts/restored
```

The backup uses SQLite's backup API, includes evidence referenced by finalized runs, writes a checksummed manifest, and rejects unsafe restore paths. See `docs/runbook.md` for recovery and source-failure procedures.

## Source and scope limits

- Public product/company information only; no login, form submission, customer data, application flows, or CAPTCHA bypass.
- Loans only in release 1. Cards, savings/demat, competitors, personas, ML, and LLM extraction are excluded.
- Brand, LSP, lender, marketplace, and parent roles remain distinct.
- Nominal interest and APR, monthly and annual rates, flat and reducing bases, and conditional terms are not silently equated.
- A first run is a baseline. A real removal needs two healthy observations at least 24 hours apart.

See `docs/data-dictionary.md`, `docs/validation-protocol.md`, and `docs/runbook.md` for the detailed contracts.
