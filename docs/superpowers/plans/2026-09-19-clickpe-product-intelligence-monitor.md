# ClickPe Product Intelligence Monitor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a local financial-product monitor that discovers ClickPe loans, preserves source evidence, compares applicable official terms, tracks changes, and exposes actionable review items in Streamlit.

**Architecture:** A synchronous Python pipeline captures public source bytes, extracts immutable field observations, resolves reviewed entity/programme mappings, and writes comparisons/history into SQLite. Pure normalization, comparison and scoring functions run offline; a separate read-only query layer powers Streamlit and reports. Versioned raw captures, configuration, mapping manifests and Parquet exports make each result replayable.

**Tech Stack:** Python 3.12, requests, BeautifulSoup, Pydantic 2, Decimal/regex, SQLite, pandas/PyArrow, PyYAML, RapidFuzz, Streamlit/Plotly, pytest; optional Playwright and pypdf only for sources that need rendering or public PDF extraction.

**Spec:** `docs/specs/2026-09-19-clickpe-product-intelligence-monitor.md`, distilled from the user's 90-section brief; inspected source/environment evidence: `docs/research/2026-09-19-source-feasibility.md`.

## Global Constraints

Use public product/company information only; no customer data, logins, form submission or application workflows.
Use neutral review language; a source difference is not proof of an error or regulatory violation.
Start with loans; complete a 10–15-product checkpoint and a fixed 25-product first release, subject to actual availability.
Discover the whole public catalogue but report inventory separately from the monitored cohort.
Keep cards, savings/demat, competitors, personas, ML and LLM extraction outside this release.
Preserve brand, LSP, regulated lender and parent as different roles; mappings require evidence and programme review.
Retain unknowns as NULL and distinguish absence, ambiguity, unsupported extraction, blocked sources and parse failures.
Preserve nominal rate versus APR, rate period/basis, amount currency, bound qualifiers and conditional terms.
Keep raw tenure and discrete options; 365/12 days/month is explicitly approximate.
Every field and finding must be traceable to immutable source bytes, hash, locator, quote, retrieval time and extractor version.
Internal ClickPe disclosures are not independent authoritative-provider coverage.
Persist conflicting assertions; never silently select a convenient source value.
Failed/incomplete runs cannot overwrite good observations, refresh verification dates or create removals.
Store source captures, SQLite, processed Parquet and historical snapshots; replay must work without networking.
Use configurable delays, timeouts, bounded retries, caching, source terms/robots checks and structured logs.
Keep tests offline except an explicit live acceptance run; synthetic history is visibly synthetic.
Use weighted completeness and transparent policy scores, never a black-box financial recommendation score.
Evaluate against independent labels and report actual denominators, failures and uncertainty; targets are not results.
Deliver a working dashboard, reusable pipeline, dataset, history capability, report, reproducible local repository and short demo.
Support Windows/PowerShell with an isolated Python 3.12 environment. No original user dependency floor exists.
Only planning documents are created in the planning session. Git initialization, installation, implementation, scheduling and publication occur during subsequent execution.

---

## Starting state, decisions and execution route

The workspace was empty with no Git history, source files or tests. Python 3.12.6 and Git are available. Public catalogue discovery can use `https://clickpe.ai/api/proxy/products?channel=landing`; a direct requests inspection returned 67 records, of which 35 were in Personal Loan, Business Loan or Loan Against Property. This is reconnaissance, not a validated dataset.

Use one integrated plan because the brief already divides the pipeline into dependent stages. Each task below produces its own testable deliverable. Future product schemas and competitor collection should receive separate plans when requested.

The two `superpowers` execution skills named in the required header are not exposed in the current skill catalog and were not found at their standard local skill paths. Before using either named workflow, locate/read the actual skill or explicitly state it is unavailable and use a user-selected equivalent task/checkpoint workflow. Do not claim an unavailable skill was executed or install it silently. This does not block completing this planning artifact.

Milestones:

- Tasks 1–9: reproducible collection/extraction/comparison core.
- Tasks 10–14: operational monitor and four-view MVP; fifth view is provider intelligence.
- Tasks 15–17: measured validation, repeatable operation, live release report and demo.

Keep the cohort stable across runs. Seed 12 IDs observed during planning: `creditsea_pl`, `kreditbuddha_pl`, `brightloans_pl`, `muthoot_emi_bl`, `muthoot_daily_bl`, `incred_pl`, `moneydot_pl`, `prefr_pl`, `vivifi_pl`, `lendingplate_pl`, `flexiloans_bl`, `lap_google_form`. Validate they still exist at execution. Fill to 25 by ascending `(ranking, id)` among active in-scope records, preserving all available business/LAP/credit-line categories. Record selection once in `config/cohort.yaml`; do not replace hard-to-map products to inflate coverage.

## File map and responsibilities

All paths below are relative to `D:\Clickpe-PIM`. Every path is a planned **new** file unless a task explicitly modifies a file created by an earlier task. Line numbers are intentionally omitted because no implementation exists.

| Files | Responsibility |
|---|---|
| `pyproject.toml`, `uv.lock`, `requirements.txt`, `.gitignore` | Package, locked environment, compatibility install, ignored runtime artifacts |
| `config.yaml` | Collection, scoring, freshness and display policy |
| `config/cohort.yaml`, `config/entities.yaml`, `config/source_mapping.yaml` | Stable cohort; distinct legal entities and aliases; reviewed programme/source mappings |
| `src/clickpe_pim/__init__.py`, `__main__.py`, `cli.py` | Package version and CLI dispatch |
| `src/clickpe_pim/contracts.py`, `fields.py`, `settings.py` | Immutable typed records, field definitions, validated configuration |
| `src/clickpe_pim/normalize/{__init__,money,rates,tenure,text}.py` | Pure field normalization; text/threshold exceptions |
| `src/clickpe_pim/storage/schema.sql`, `src/clickpe_pim/storage/{__init__,repository,captures,exports}.py` | Schema, transactional persistence, immutable raw files, atomic exports |
| `src/clickpe_pim/collect/{__init__,http,policy}.py` | GET transport, robots/terms/host policy and retries |
| `src/clickpe_pim/catalogue/{__init__,discover,extract,disclosures}.py` | Public feed inventory, product assertions, ClickPe internal disclosures |
| `src/clickpe_pim/providers/{__init__,mapping,extract,entities}.py` | Reviewed scope, recipe-based official-source extraction, alias suggestions |
| `src/clickpe_pim/compare/{__init__,engine,checks,scoring}.py` | Comparability, internal checks, review priorities |
| `src/clickpe_pim/monitor/{__init__,history,freshness,metrics}.py` | Temporal changes, verification ages, transparent aggregates |
| `src/clickpe_pim/pipeline.py`, `queries.py` | Orchestration and dashboard/report query boundary |
| `src/clickpe_pim/evaluate.py`, `report.py` | Gold evaluation and analytical report generation |
| `app/dashboard.py`, `app/pages/{1_Review_Queue,2_Product_Explorer,3_Change_History,4_Providers}.py`, `app/components.py` | Overview, queue, explorer, history, provider views and shared evidence UI |
| `tests/conftest.py`, `tests/test_{contracts,money,rates,tenure,text,repository,captures,http,discovery,clickpe_extraction,disclosures,mapping,providers,comparison,scoring,history,pipeline,queries,dashboard,evaluation,report,backup}.py` | Offline tests owned by corresponding tasks |
| `tests/fixtures/{catalogue,partners,support,provider,blocked,history}/` | Small synthetic fixtures plus minimal attributed captured excerpts; each real fixture has URL/date/hash metadata |
| `data/gold/{labels,flag_reviews}.jsonl`, `data/gold/split.yaml` | Independent field labels, reviewed flag outcomes, fixed product split |
| `scripts/{backup,restore}.py`, `.github/workflows/ci.yml`, `.github/workflows/monitor.yml` | Consistent backups, verified restore, offline CI, opt-in monitoring |
| `README.md`, `docs/{data-dictionary,runbook,validation-protocol,demo-script}.md` | Operation, definitions, evaluation and demo instructions |
| `reports/release-1/{report.md,report.pdf,metrics.json,evidence-index.json,acceptance.md,demo.mp4}` | Generated measured release artifacts, never hand-invented results |

Runtime paths (ignored by Git except approved small fixtures/gold): `data/raw/{clickpe,providers}/{UTC-date}/{run_id}/`, `data/db/monitor.sqlite`, `data/processed/`, `data/snapshots/{run_id}/`, `data/manifests/{run_id}.json`, `logs/{run_id}.jsonl`, `data/backups/`. No data artifact may contain secrets, cookies or customer submissions.

## Shared contracts used throughout the tasks

All models live in `contracts.py`, use Pydantic `ConfigDict(extra="forbid", frozen=True)`, UTC-aware datetimes, and JSON-safe serialization with Decimal stored as strings. Stable IDs use native product IDs and SHA-256 over deterministic serialized identifiers, never Python `hash()`.

```python
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

class Value(Record):
    kind: Literal["money", "rate", "tenure", "number", "text", "boolean", "set"]
    lower: Decimal | None = None
    upper: Decimal | None = None
    text: str | None = None
    boolean: bool | None = None
    options: tuple[str, ...] = ()
    unit: str | None = None
    period: Literal["annual", "monthly", "daily", "unknown"] = "unknown"
    basis: Literal["flat", "reducing", "unknown"] = "unknown"
    qualifier: Literal["exact", "range", "from", "up_to", "policy", "conditional"] = "exact"
    approximate: bool = False

class Product(Record):
    product_id: str
    name: str
    category: str
    provider_name_raw: str | None = None
    provider_id: str | None = None
    clickpe_url: str
    active_status: Literal["active", "inactive", "unknown"]

class Capture(Record):
    capture_id: str
    run_id: str
    source_id: str
    source_type: str
    url: str
    final_url: str
    retrieved_at: datetime
    status: Literal["ok", "not_modified", "blocked", "failed", "not_found"]
    http_status: int | None = None
    sha256: str | None = None
    raw_path: str | None = None
    media_type: str | None = None
    error_code: str | None = None

class Observation(Record):
    observation_id: str
    run_id: str
    product_id: str
    source_id: str
    capture_id: str
    field: str
    state: Literal["present", "absent", "ambiguous", "unsupported", "failed"]
    value: Value | None = None
    raw_text: str
    locator: str
    context: Literal["offer", "marketing", "calculator", "example", "form_config", "unknown"]
    extracted_at: datetime
    extractor_version: str
    confidence: float = Field(ge=0, le=1)
    conditions: tuple[str, ...] = ()

class Mapping(Record):
    mapping_id: str
    product_id: str
    source_id: str
    entity_id: str | None = None
    role: Literal["brand", "lsp", "lender", "marketplace", "parent", "unknown"]
    programme: str | None = None
    segment: str | None = None
    geography: str | None = None
    scope: Literal["same_programme", "related_programme", "unknown", "different_programme"]
    review_state: Literal["candidate", "approved", "rejected"]
    confidence: float = Field(ge=0, le=1)
    evidence_capture_id: str | None = None
    evidence_locator: str | None = None
    rationale: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None

class Comparison(Record):
    comparison_id: str
    run_id: str
    product_id: str
    field: str
    left_id: str | None
    right_id: str | None
    mapping_id: str | None
    kind: Literal["internal", "external", "single_source"]
    status: Literal["MATCH", "DIFFERENT", "MISSING_CLICKPE", "MISSING_PROVIDER", "UNCOMPARABLE", "AMBIGUOUS"]
    reason: str
    reason_code: str
    confidence: float = Field(ge=0, le=1)

class Change(Record):
    change_id: str
    product_id: str
    source_id: str | None
    field: str | None
    type: Literal["VALUE_CHANGED", "PRODUCT_ADDED", "PRODUCT_REMOVED", "SOURCE_DISAPPEARED", "FIELD_ADDED", "FIELD_REMOVED"]
    previous_id: str | None
    current_id: str | None
    detected_at: datetime
    synthetic: bool = False
```

Add validators in Task 1: lower ≤ upper; every datetime aware; `present` needs a non-null value and nonempty quote/locator; `absent` has no value but has an inspected-scope locator; approved mapping requires reviewer/date/evidence/rationale; observation field belongs to registry; exact/range values cannot contain nonfinite or negative finance quantities. `policy` may have text and no numeric bounds. An absent observation links to a successfully parsed capture and is never synthesized from a network failure.

### Task 1: Executable package, schema and policy contract

**Files:** Create `pyproject.toml`, `.gitignore`, `config.yaml`, `src/clickpe_pim/{__init__,contracts,fields,settings}.py`, `tests/test_contracts.py`, `tests/conftest.py`, `docs/data-dictionary.md`.

**Interfaces:** Produces models above, `load_settings(path: Path) -> Settings`, `FIELD_SPECS: dict[str, FieldSpec]`. `FieldSpec` is a frozen dataclass `(kind: str, group: str, importance: float, unit: str | None, numeric: bool)`. `Settings` is a Pydantic model matching the YAML below; callers consume its nested dictionaries through validated typed nested models.

- [ ] **Step 1: Create the isolated execution environment and packaging metadata.** During execution run `git init`, then `python -m venv .venv`. Create `src/clickpe_pim/__init__.py` with `__version__ = "0.1.0"` before installing the package. Create package metadata with setuptools discovery under `src`, `requires-python = ">=3.12,<3.13"`, dependencies `requests>=2.32.5,<3`, `beautifulsoup4>=4.12.3,<5`, `pydantic>=2.12.5,<3`, `PyYAML>=6.0.2,<7`, `pandas>=2.3.3,<3`, `pyarrow>=20,<24`, `streamlit>=1.52.1,<2`, `plotly>=6,<7`, `rapidfuzz>=3.14,<4`. Add dev extras `pytest>=8.4,<9`, `ruff>=0.12,<1`, and optional `browser = ["playwright>=1.55,<2"]`, `pdf = ["pypdf>=6,<7", "reportlab>=4,<5"]`. These are selected compatibility ranges, not claims that the installed set has passed. Configure pytest `testpaths=["tests"]`, `pythonpath=["src"]`; add setuptools package data `clickpe_pim = ["storage/*.sql"]` so the schema ships in a wheel. Ignore `.venv/`, `.artifacts/`, caches, runtime data and generated reports, while keeping `data/gold/` tracked. Run `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`. Expected: imports/dependencies install; no global packages change.

- [ ] **Step 2: Write contract tests and run them red.**

```python
import pytest
from pydantic import ValidationError
from clickpe_pim.contracts import Value
from clickpe_pim.settings import load_settings

def test_unknown_is_not_zero():
    assert Value(kind="money", unit="INR").lower is None

def test_inverted_range_is_rejected():
    with pytest.raises(ValidationError):
        Value(kind="money", lower="500000", upper="300000", unit="INR")

def test_completeness_weights_sum_to_one():
    from pathlib import Path
    cfg = load_settings(Path("config.yaml"))
    assert sum(cfg.completeness.weights.values()) == pytest.approx(1)
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_contracts.py -q`; expected collection failure until the modules exist.

- [ ] **Step 3: Implement the shared models and exact field registry.** Register `loan_amount`, `interest_rate`, `apr`, `tenure`, `regulated_lender`, `repayment_frequency`, `emi_type`, `auto_pay_available`, `enach_available`, `processing_fee`, `foreclosure_fee`, `prepayment_fee`, `late_payment_fee`, `stamp_duty`, `other_charges`, `minimum_age`, `maximum_age`, `minimum_income`, `minimum_turnover`, `minimum_business_vintage`, `minimum_credit_score`, `employment_type`, `business_type`, `citizenship`, `residency`, `location_restrictions`, `pan_required`, `aadhaar_required`, `bank_statement_months`, `gst_required`, `income_proof_required`, `salary_slip_required`, `business_proof_required`, `address_proof_required`, `documents_raw`, `fees_raw_text`, `approval_time`, `disbursal_time`, `application_mode`, `paperless`, `instant_disbursal`, `marketing_claim`. Range fields expose min/max columns at export; there are no independent contradictory min/max objects. Register review-only `category_content` and `provider_identity` fields for checks. Document source units and valid enum values for every field.

- [ ] **Step 4: Implement configuration and shared test factories.**

```yaml
scraping:
  request_delay: 2.0
  max_retries: 3
  connect_timeout: 5
  read_timeout: 30
  max_bytes: 10485760
  max_pages_per_host: 10
monitoring:
  stale_days: 30
  confirm_absence_hours: 24
  required_absence_observations: 2
  maximum_comparison_age_days: 30
  maximum_pair_skew_days: 7
completeness:
  weights: {lender: 0.20, interest: 0.20, amount: 0.15, fees: 0.15, tenure: 0.10, eligibility: 0.10, repayment: 0.05, documents: 0.05}
comparison:
  amount_tolerance_inr: 1
  rate_tolerance_percentage_points: 0.01
  approximate_tenure_tolerance_days: 1
  minimum_mapping_confidence: 0.8
  high_priority_threshold: 70
paths:
  database: data/db/monitor.sqlite
  raw: data/raw
  snapshots: data/snapshots
```

`tests/conftest.py` supplies `make_observation` and `make_capture` factory fixtures accepting keyword overrides. Exact defaults are `run_id="r1"`, `product_id="p1"`, `source_id="s1"`, `capture_id="c1"`, `observation_id="o1"`, aware `2026-09-19T00:00:00Z`, field `loan_amount`, an offer-context present `Value(kind="money", upper="500000", unit="INR", qualifier="up_to")`, raw text `up to INR 500000`, locator `/response/0/content/headline`, extractor version `"1"`, confidence 1. Capture defaults are type `clickpe_catalogue`, URL/final URL `https://example.org/products`, status `ok`, HTTP 200, and a synthetic raw path/hash. Each factory constructs its model from a default dictionary merged with keyword overrides. Tests use `tmp_path` for all writes.

- [ ] **Step 5: Verify validation and commit.** Add parametrized invalid cases for naive timestamps, nonfinite/negative values, missing evidence on present observations and approved mappings without reviewer. Run `.\.venv\Scripts\python.exe -m pytest tests/test_contracts.py -q`; expected all pass. Run `git add pyproject.toml .gitignore config.yaml src tests docs` and `git commit -m "feat: define evidence and policy contracts"` after checking `git diff --cached --stat`.

### Task 2: Money and interest normalization with explicit bounds

**Files:** Create `src/clickpe_pim/normalize/{__init__,money,rates}.py`, `tests/test_money.py`, `tests/test_rates.py`.

**Interfaces:** Consumes `Value`; produces `normalize_currency(raw: str) -> Value | None`, `normalize_rate(raw: str, *, apr: bool = False) -> Value | None`. `None` means no supported parse; policy text produces `Value(kind="rate", text=raw, qualifier="policy")`.

- [ ] **Step 1: Write independent oracle tests.**

```python
from decimal import Decimal
import pytest
from clickpe_pim.normalize.money import normalize_currency
from clickpe_pim.normalize.rates import normalize_rate

@pytest.mark.parametrize("raw,expected", [("₹5 lakh", "500000"), ("Rs 500000", "500000"), ("INR 5,00,000", "500000"), ("5L", "500000"), ("25K", "25000"), ("₹1 crore", "10000000")])
def test_money(raw, expected):
    v = normalize_currency(raw)
    assert v.lower == v.upper == Decimal(expected)

def test_qualifiers_and_shared_units():
    assert normalize_currency("up to ₹5 lakh").lower is None
    assert normalize_currency("₹20,000–3 lakh").upper == Decimal("300000")
    assert normalize_currency("1–5 lakh").lower == Decimal("100000")
    assert normalize_currency("₹5–3 lakh") is None

def test_rate_period_and_policy():
    assert normalize_rate("1% monthly").period == "monthly"
    assert normalize_rate("12% p.a.").period == "annual"
    assert normalize_rate("Starting from 11%").period == "unknown"
    assert normalize_rate("As per partner policy").lower is None
    assert normalize_rate("11%-24% p.a.").upper == Decimal("24")
```

Put money cases in `test_money.py`, rate cases in `test_rates.py`. Run `.\.venv\Scripts\python.exe -m pytest tests/test_money.py tests/test_rates.py -q`; expect missing imports initially.

- [ ] **Step 2: Implement token parsing without float conversion.** Use `Decimal(token.replace(",", ""))` and multiplier map `{"k":1000,"l":100000,"lac":100000,"lacs":100000,"lakh":100000,"lakhs":100000,"cr":10000000,"crore":10000000,"crores":10000000}`. Anchor the accepted money expression after stripping `₹|Rs\.?|INR` and supported bound words; reject other currencies and unrelated trailing prose. Normalize dash variants. A trailing scale propagates to an unscaled range endpoint when it has no comma and is below 1000; a rupee marker does not block shared scaling. Thus `₹1–5 lakh` shares lakh, `₹20,000–3 lakh` retains 20,000, and `₹5–3 lakh` is an invalid inverted range. If scale inheritance is not unambiguous under these rules, return None. Preserve `from` with upper NULL and `up_to` with lower NULL. Reject reversed ranges before constructing `Value`.

```python
def bounds(numbers, qualifier):
    if len(numbers) == 2:
        return numbers[0], numbers[1], "range"
    if qualifier == "from":
        return numbers[0], None, "from"
    if qualifier == "up_to":
        return None, numbers[0], "up_to"
    return numbers[0], numbers[0], "exact"
```

Keep `bounds` in `money.py` and import it explicitly in `rates.py`. Callers pass only a selected field span, never the entire page.

- [ ] **Step 3: Implement rate period and basis preservation.** Recognize `p.a.|per annum|annual|yearly`, `p.m.|per month|monthly`, `per day|daily`; conflicting periods return None. Set `flat` or `reducing` only when stated. Strip `%` only after confirming a rate pattern; 100% digital/approval claims return None. `apr=True` supplies annual semantics because the field is APR, but rejects an explicitly monthly/daily APR label for manual review. Never convert periods. Never parse policy text as zero. Preserve a fee percentage in the fee field, not as interest.

- [ ] **Step 4: Extend boundary tests and verify.** Add `0% p.a.`, `4% monthly`, spaces/commas/Unicode dashes, ranges with one percent sign, policy text, negative amounts, unrelated numeric prose, mixed currencies and multiple periods. Expected: exact supported values or explicit None, never a plausible guessed number. Run the two test files and `tests/test_contracts.py` together; all pass.

- [ ] **Step 5: Commit.** `git add src/clickpe_pim/normalize tests/test_money.py tests/test_rates.py` then `git commit -m "feat: normalize amounts and rate semantics"`.

### Task 3: Tenure and qualified text requirements

**Files:** Create `src/clickpe_pim/normalize/{tenure,text}.py`, `tests/test_tenure.py`, `tests/test_text.py`.

**Interfaces:** `normalize_tenure(raw: str) -> Value | None`; `normalize_requirement(field: str, raw: str) -> Value | None`. Original representation remains in `Observation.raw_text`; normalized tenure unit is days, and `options` stores original discrete values plus unit as strings.

- [ ] **Step 1: Write the semantic regression tests.**

```python
from decimal import Decimal
from clickpe_pim.normalize.tenure import normalize_tenure
from clickpe_pim.normalize.text import normalize_requirement

def test_tenure_preserves_approximation_and_options():
    assert normalize_tenure("24 months").upper == Decimal("730")
    assert normalize_tenure("24 months").approximate
    assert normalize_tenure("104–300 days").lower == Decimal("104")
    assert not normalize_tenure("104–300 days").approximate
    assert normalize_tenure("104, 156, 234 and 313 days").options == ("104 days", "156 days", "234 days", "313 days")

def test_conditional_credit_requirement_survives():
    v = normalize_requirement("minimum_credit_score", "Minimum CIBIL 650; NTC applicants accepted subject to banking surrogate")
    assert v.lower == Decimal("650")
    assert v.qualifier == "conditional"
    assert "NTC" in v.text
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_tenure.py tests/test_text.py -q`; expect missing modules.

- [ ] **Step 2: Implement exact rational conversion and discrete-option extraction.** Parse tokens with a single shared unit. Convert day/week/month/year using `Decimal(1)`, `Decimal(7)`, `Decimal(365)/12`, `Decimal(365)`; perform `months * 365 / 12` in that order to avoid a 24-month rounding remainder. Mark months/years approximate. A comma/`and` list keeps options and its min/max envelope, with comparisons checking the options too. Reject mixed contradictory units and unsupported business-day/calendar-day substitutions. `up to` has no minimum.

- [ ] **Step 3: Implement explicit text dictionaries and exceptions.** Normalize employment to sorted sets of `salaried`, `self_employed`, `business_owner`, `professional`; explicit daily/weekly/monthly/flexible repayment to text; `EMI` alone means installment type, not monthly frequency. Require evidence before expanding `EDI` to daily. Credit-score rules capture `700+`/`minimum 700`/`at least 700`; `above 700` remains a strict condition in text. Mark any `subject to`, `NTC`, `except`, segment or geography condition as conditional. For documents, explicit requirement → true, explicit exemption → false, silence → None. Do not interpret “no hidden charges” as zero fees or “minimal paperwork” as no documents.

- [ ] **Step 4: Verify and commit.** Add tests for years, fractional months, 104–300 days, no unit, contradictory units, EMI without frequency, optional GST and unknown documents. Run `.\.venv\Scripts\python.exe -m pytest tests/test_tenure.py tests/test_text.py -q`; all pass. `git add src/clickpe_pim/normalize tests/test_tenure.py tests/test_text.py` then `git commit -m "feat: preserve tenure options and eligibility conditions"`.

### Task 4: Immutable evidence and transactional SQLite storage

**Files:** Create `src/clickpe_pim/storage/__init__.py`, `schema.sql`, `repository.py`, `captures.py` in that directory; create `tests/test_repository.py`, `tests/test_captures.py`.

**Interfaces:** `Repository(path: Path)` exposes `initialize() -> None`, `begin_run(run_id: str, started_at: datetime, manifest: dict) -> None`, `save_capture(capture: Capture) -> None`, `save_observations(items: list[Observation]) -> None`, `finish_run(run_id: str, status: str, catalogue_complete: bool) -> None`, `latest_good(product_id: str, source_id: str, field: str) -> Observation | None`. `save_bytes(root: Path, run_id: str, source_id: str, payload: bytes, suffix: str) -> tuple[Path,str]` returns relative path/hash; same path with different bytes is rejected.

- [ ] **Step 1: Write persistence and evidence tests.**

```python
import pytest
from clickpe_pim.storage.captures import save_bytes
from clickpe_pim.storage.repository import Repository

def test_raw_capture_is_immutable(tmp_path):
    path, digest = save_bytes(tmp_path, "r1", "s1", b"first", ".html")
    assert len(digest) == 64
    assert (tmp_path / path).read_bytes() == b"first"
    with pytest.raises(FileExistsError):
        save_bytes(tmp_path, "r1", "s1", b"changed", ".html")

def test_failed_run_does_not_replace_good_value(tmp_path, make_capture, make_observation):
    from clickpe_pim.contracts import Product
    repo = Repository(tmp_path / "monitor.sqlite")
    repo.initialize()
    stamp = make_capture().retrieved_at
    repo.upsert_product(Product(product_id="p1", name="Synthetic loan", category="personal_loan", clickpe_url="https://example.org/products", active_status="active"), stamp)
    repo.upsert_source("s1", "https://example.org/products", "clickpe_catalogue", {})
    for run_id, state in [("r1", "complete"), ("r2", "failed")]:
        repo.begin_run(run_id, stamp, {"synthetic": True})
        cap = make_capture(run_id=run_id, capture_id=run_id)
        repo.save_capture(cap)
        repo.save_observations([make_observation(run_id=run_id, capture_id=run_id, observation_id=run_id)])
        repo.finish_run(run_id, state, catalogue_complete=state == "complete")
    assert repo.latest_good("p1", "s1", "loan_amount").run_id == "r1"
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_repository.py tests/test_captures.py -q`; expected missing imports.

- [ ] **Step 2: Create the schema and migrations baseline.** Use `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000`, parameterized statements and explicit transaction scopes. Set `PRAGMA user_version=1`. Tables and critical keys:

```sql
CREATE TABLE scrape_runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
  status TEXT NOT NULL, catalogue_complete INTEGER NOT NULL DEFAULT 0,
  synthetic INTEGER NOT NULL DEFAULT 0, manifest_json TEXT NOT NULL
);
CREATE TABLE providers (provider_id TEXT PRIMARY KEY, record_json TEXT NOT NULL);
CREATE TABLE products (
  product_id TEXT PRIMARY KEY, record_json TEXT NOT NULL,
  first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, active_status TEXT NOT NULL
);
CREATE TABLE sources (source_id TEXT PRIMARY KEY, url TEXT NOT NULL, source_type TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE TABLE captures (
  capture_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs,
  source_id TEXT NOT NULL REFERENCES sources, retrieved_at TEXT NOT NULL,
  status TEXT NOT NULL, sha256 TEXT, raw_path TEXT, record_json TEXT NOT NULL
);
CREATE TABLE product_snapshots (
  run_id TEXT NOT NULL REFERENCES scrape_runs, product_id TEXT NOT NULL REFERENCES products,
  record_json TEXT NOT NULL, PRIMARY KEY(run_id, product_id)
);
CREATE TABLE product_attributes (
  observation_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs,
  product_id TEXT NOT NULL REFERENCES products, source_id TEXT NOT NULL REFERENCES sources,
  capture_id TEXT NOT NULL REFERENCES captures, field TEXT NOT NULL,
  state TEXT NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE mappings (mapping_id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products, source_id TEXT NOT NULL REFERENCES sources, record_json TEXT NOT NULL);
CREATE TABLE product_entities (product_id TEXT NOT NULL REFERENCES products, provider_id TEXT NOT NULL REFERENCES providers, role TEXT NOT NULL, evidence_json TEXT NOT NULL, PRIMARY KEY(product_id,provider_id,role));
CREATE TABLE comparisons (comparison_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs, product_id TEXT NOT NULL REFERENCES products, record_json TEXT NOT NULL);
CREATE TABLE conflicts (fingerprint TEXT PRIMARY KEY, comparison_id TEXT NOT NULL REFERENCES comparisons, priority INTEGER NOT NULL, severity TEXT NOT NULL, state TEXT NOT NULL, last_seen TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE TABLE review_events (event_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL REFERENCES conflicts, reviewed_at TEXT NOT NULL, reviewer TEXT NOT NULL, disposition TEXT NOT NULL, note TEXT NOT NULL);
CREATE TABLE changes (change_id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products, detected_at TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE INDEX attributes_lookup ON product_attributes(product_id,source_id,field,run_id);
```

`record_json` uses the Pydantic model JSON and checked schema version in the run manifest. Add `upsert_product(product: Product, at: datetime) -> None`, `upsert_source(source_id: str, url: str, source_type: str, record: dict) -> None`, `save_mapping(mapping: Mapping) -> None`, `save_comparisons(items: list[Comparison]) -> None`, and `save_changes(items: list[Change]) -> None` to Repository. Test setup explicitly inserts product/source parents before capture writes. Do not weaken foreign keys to make tests pass.

- [ ] **Step 3: Implement append-only raw storage and successful-state selection.** Restrict `run_id/source_id` to `[A-Za-z0-9_-]+` before constructing paths. Write bytes using exclusive creation `open("xb")`; compute SHA-256 first and verify after write. A byte-identical retry returns the existing path/hash; different bytes under the same ID raises. Use a temporary sibling and `os.replace` only for mutable latest exports. `latest_good` joins completed/partial runs to captures with valid bytes and present/absent observations; only healthy source results in a partial run qualify. It must not silently skip a genuine later supported absence. For history, source-level parse success is tracked in the manifest separately from overall run status.

- [ ] **Step 4: Verify rollback, identity and idempotence.** Add tests for missing foreign keys, two claims for one field, repeating an identical observation ID, mismatched bytes on an existing ID, interrupted transaction, genuine absence versus failed extraction, and replay IDs. A conflict on an existing ID with different serialized content raises rather than overwrites. Run both test files; all pass.

- [ ] **Step 5: Commit.** `git add src/clickpe_pim/storage tests/test_repository.py tests/test_captures.py` then `git commit -m "feat: persist immutable observations and source evidence"`.

### Task 5: Bounded public collection with source health

**Files:** Create `src/clickpe_pim/collect/{__init__,http,policy}.py`, `tests/test_http.py`, `tests/fixtures/blocked/captcha.html`.

**Interfaces:** `FetchResult` is a frozen dataclass `(url: str, final_url: str, status: str, http_status: int | None, body: bytes | None, media_type: str | None, error_code: str | None, retrieved_at: datetime)`. `HttpCollector(settings: Settings, session: requests.Session | None = None, sleep: Callable[[float],None] = time.sleep)` exposes `fetch(url: str, *, allowed_hosts: set[str], validators: dict[str,str] | None = None) -> FetchResult`. `check_policy(url: str, user_agent: str, robots_body: str, robots_status: int) -> bool` is pure.

- [ ] **Step 1: Write transport tests using injected sessions, never live sites.**

```python
from clickpe_pim.collect.policy import check_policy

def test_robots_disallow_is_honoured():
    assert not check_policy("https://example.org/private/x", "ClickPePIM", "User-agent: *\nDisallow: /private/", 200)

def test_unknown_robots_health_is_not_permission():
    assert not check_policy("https://example.org/", "ClickPePIM", "", 503)
```

In `test_http.py` implement `FakeResponse(status_code, body, headers)` with `iter_content()` and `close()`, and `FakeSession(responses)` with `get(*args, **kwargs)` popping configured responses and logging calls. Test 503→200 retries; 403/429/404 outcomes; 200 CAPTCHA body; timeout; oversized body; denied redirect; 304 with and without a prior capture. Run `.\.venv\Scripts\python.exe -m pytest tests/test_http.py -q`; expect imports missing.

- [ ] **Step 2: Implement policy without bypasses.** Use `urllib.robotparser.RobotFileParser.parse(robots_body.splitlines())` and `can_fetch`; 404 robots means no file, while 401/403 denies and 5xx/timeouts postpone that host. Validate HTTPS hostname against a reviewed allowlist before GET and at every redirect, with `allow_redirects=False`; at most five redirects. Exclude credentials in URLs and private/loopback addresses from external-source mappings. Cache robots per host/run; retain the actual robots capture. Source mapping records include `terms_checked_at` and `collection_notes`.

- [ ] **Step 3: Implement bounded retries and capture classification.** Pace all host requests by configured delay; use `timeout=(5,30)`, stream bytes capped at 10 MiB and close responses. Retry timeout/connection error/502/503/504 at 2, 4, 8 seconds with at most three retries after the initial attempt. Respect `Retry-After` for 429 only up to a 60-second cap, then return `blocked/rate_limited` and let the next run retry. Never retry authentication/CAPTCHA by changing identity. A 404/410 returns `not_found`, not a product removal. A 200 challenge page returns `blocked`. Record real retrieval time only on a network response; offline replay keeps original times. A 304 can confirm unchanged bytes only when linked to a known hash and previous validated capture; otherwise refetch once without validators.

- [ ] **Step 4: Verify source health and commit.** Assert failed bodies cannot be handed to successful extraction and cache replays cannot advance verification. Run `.\.venv\Scripts\python.exe -m pytest tests/test_http.py tests/test_captures.py -q`; all pass. `git add src/clickpe_pim/collect tests/test_http.py tests/fixtures/blocked` then `git commit -m "feat: collect public sources with explicit failure states"`.

### Task 6: Public catalogue inventory and stable cohort

**Files:** Create `src/clickpe_pim/catalogue/{__init__,discover}.py`, `config/cohort.yaml`, `tests/test_discovery.py`, `tests/fixtures/catalogue/feed.json`.

**Interfaces:** `DiscoveryResult` frozen dataclass `(products: list[Product], complete: bool, excluded: list[dict], reasons: tuple[str,...])`; `discover(payload: dict, catalogue_url: str) -> DiscoveryResult`; `select_cohort(products: list[Product], native_records: list[dict], target: int, seed_ids: list[str]) -> list[str]`.

- [ ] **Step 1: Write feed-contract and duplicate tests.**

```python
from clickpe_pim.catalogue.discover import discover

def test_native_ids_distinguish_muthoot_variants():
    rows = [{"id": x, "name": x, "category": "Business Loan", "lender": "Muthoot Finance", "status": "ACTIVE"} for x in ["muthoot_emi_bl", "muthoot_daily_bl"]]
    result = discover({"status": "Success", "response": rows}, "https://clickpe.ai/product")
    assert len(result.products) == 2
    assert result.complete

def test_shell_empty_and_duplicate_ids_are_not_complete():
    assert not discover({"status": "Success", "response": []}, "https://clickpe.ai/product").complete
    row = {"id": "p", "name": "Loan", "category": "Personal Loan", "status": "ACTIVE"}
    assert not discover({"status": "Success", "response": [row,row]}, "https://clickpe.ai/product").complete
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_discovery.py -q`; expect missing module.

- [ ] **Step 2: Implement a strict discovery adapter.** Require `status == "Success"`, a nonempty `response` list and required strings per row. Validate unique native IDs across all records, record out-of-scope entries, and retain inactive records for inventory accounting. Unknown categories are quarantined rather than classified by brand. Map exactly `Personal Loan`→`personal_loan`, `Business Loan`→`business_loan`, `Loan Against Property`→`loan_against_property`; support explicit `Creditline`/`Credit Line` as `credit_line` if observed. Do not map `Loan Against Credit Card` automatically. If any malformed row/duplicate/pagination cursor remains, mark discovery incomplete and disallow removals.

```python
CATEGORY_MAP = {"Personal Loan": "personal_loan", "Business Loan": "business_loan", "Loan Against Property": "loan_against_property", "Creditline": "credit_line", "Credit Line": "credit_line"}
# Stable product identity; name/provider edits must not create new products.
product = Product(product_id=row["id"], name=row["name"], category=CATEGORY_MAP[row["category"]], provider_name_raw=row.get("lender"), clickpe_url=catalogue_url, active_status={"ACTIVE":"active", "INACTIVE":"inactive"}.get(row.get("status"), "unknown"))
```

- [ ] **Step 3: Freeze selection and discover actual public presentation.** Write `config/cohort.yaml` as `{version: 1, target: 25, seed_ids: [...], product_ids: []}` before the first live run. At cohort creation validate seed membership, include all in-scope minority categories, fill by ranking/ID, then persist product IDs and the capture hash; subsequent runs load that list unchanged. Save the full feed first. Produce the discovered inventory CSV through Task 12. Verify at least the 12 seed entries' visible title/headline against the rendered catalogue/modals using the collaborative browser; document any hidden or inactive feed entries. Until verified, call the inventory “public feed records,” not visible cards. No detail URLs are fabricated.

- [ ] **Step 4: Verify degraded discovery and commit.** Test malformed envelope, renamed product with stable ID, inactive record, missing seed, smaller live catalogue, unknown category, appended future category and stable cohort after ranking changes. Expected: honest count and incomplete status where appropriate; no padded IDs. Run discovery tests; all pass. `git add src/clickpe_pim/catalogue config/cohort.yaml tests/test_discovery.py tests/fixtures/catalogue` then `git commit -m "feat: discover catalogue and freeze monitoring cohort"`.

### Task 7: ClickPe field extraction and internal disclosures

**Files:** Create `src/clickpe_pim/catalogue/{extract,disclosures}.py`, `tests/test_clickpe_extraction.py`, `tests/test_disclosures.py`, fixtures in `tests/fixtures/{partners,support}/`.

**Interfaces:** `extract_product(record: dict, capture: Capture) -> list[Observation]`; `extract_disclosures(html: str, capture: Capture) -> dict[str,list[Observation]]`. Disclosure keys are section labels; Task 8 maps those labels to products. `field_spans(text: str) -> list[tuple[str,str]]` returns field name plus exact matched source substring. Supported absence is emitted only for registered supported fields within recognized content blocks.

- [ ] **Step 1: Write evidence and category-contamination tests.**

```python
from clickpe_pim.catalogue.extract import extract_product

def test_headline_upper_bound_is_not_exact_amount(make_capture):
    row = {"id":"prefr_pl", "name":"Prefr Personal Loan", "category":"Personal Loan", "content":{"headline":"Instant Personal Loan up to ₹5 Lakhs", "keyBenefits":[]}}
    facts = extract_product(row, make_capture())
    amount = next(f for f in facts if f.field == "loan_amount" and f.state == "present")
    assert str(amount.value.upper) == "500000"
    assert amount.value.lower is None
    assert amount.locator.endswith("/content/headline")

def test_deposit_copy_does_not_become_loan_interest(make_capture):
    row = {"id":"vivifi_pl", "name":"Vivifi Personal Loan", "category":"Personal Loan", "content":{"headline":"Zero Balance Digital Savings Account", "keyBenefits":["Earn up to 4% interest p.a."]}}
    facts = extract_product(row, make_capture())
    assert not any(f.field == "interest_rate" and f.state == "present" for f in facts)
    assert any(f.field == "category_content" and f.state == "ambiguous" for f in facts)
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_clickpe_extraction.py tests/test_disclosures.py -q`; expect missing modules.

- [ ] **Step 2: Implement bounded content walking and evidence IDs.** Traverse display `content.headline`, `keyBenefits`, `requiredDocuments` and reviewed display sections. Extract each block separately with JSON pointers using the native ID to find its current array index. SHA-256 observation identity includes run/product/source/field/locator/raw text/extractor version. Reject form/config and calculator contexts from offer extraction. Save marketing claims in their own field/context. Retain competing amount/rate spans as separate observations; selector logic does not overwrite earlier matches. No generic recursive search through application configuration.

```python
FIELD_PATTERNS = {
    "loan_amount": r"(?:loan(?: amount)?|borrow|loans)\s*(?:from|of|up to|upto|starting from)?\s*(?:₹|Rs\.?|INR)?\s*[\d,.]+(?:\s*(?:to|[-–])\s*(?:₹|Rs\.?|INR)?\s*[\d,.]+)?\s*(?:lakhs?|lacs?|crores?|[KL])?",
    "interest_rate": r"(?:interest(?: rate)?|rate of interest)[^.;\n]{0,60}%[^;\n]{0,20}",
    "minimum_credit_score": r"(?:minimum\s+)?(?:CIBIL|credit score)[^;\n]{0,35}",
}
```

Use these as bounded initial patterns with tests; strip the field label to pass a value span into the pure normalizer. Add separate patterns for rate periods containing dots so sentence punctuation does not truncate `p.a.`. Test the actual discovered field strings, not just the snippet. `context=offer` requires absence of category contamination and representative-example/calculator markers.

- [ ] **Step 3: Implement disclosure blocks with scoped selectors.** BeautifulSoup selects each h2/h3 lender heading and its containing section, bounded before the next peer heading. Identify `Loan Amount`, `Tenure`, `Interest Rate`, `LSP`, `Lending NBFC`, and registration labels inside that block. Store heading plus CSS/text-node locator and exact quote. Link the entire section for absence evidence. An unexpected empty block is `unsupported`, not absent. Dates/registration numbers remain entity claims. Never infer all Prefr products share the lender listed in one disclosure.

- [ ] **Step 4: Cover the extended schema with explicit supported rules.** Extract labeled processing/late/prepayment/foreclosure fees as money or rate with fee basis and tax/conditions retained in `conditions`; complexity beyond the rule stays `fees_raw_text` and `unsupported` numerically. Add age, monthly income/turnover, business-vintage, document and bank-statement rules using Task 3 normalizers. Keep minimum and maximum age as distinct number fields. Extract explicit autopay/eNACH/paperless/application mode booleans only when stated. Approval/disbursal promises are marketing-context values. Add tests that “no hidden charges” does not become zero processing fees and new-to-credit exceptions survive alongside a minimum score.

- [ ] **Step 5: Verify parser health and commit.** Tests cover all four partner blocks, malformed HTML, duplicate claims, missing content, savings copy, one unknown-period rate, EMI versus daily variants and quotes resolving back to captured bytes. Run the two test files plus normalization tests; all pass. `git add src/clickpe_pim/catalogue tests/test_clickpe_extraction.py tests/test_disclosures.py tests/fixtures/partners tests/fixtures/support` then `git commit -m "feat: extract ClickPe terms with field evidence"`.

### Task 8: Reviewed entity/programme mapping and official extraction recipes

**Files:** Create `src/clickpe_pim/providers/{__init__,mapping,entities,extract}.py`, `config/entities.yaml`, `config/source_mapping.yaml`, `tests/test_mapping.py`, `tests/test_providers.py`, `tests/fixtures/provider/incred.html`.

**Interfaces:** `load_mappings(path: Path) -> list[Mapping]`; `suggest_alias(name: str, aliases: dict[str,str]) -> list[tuple[str,float]]`; `extract_provider(html: str, capture: Capture, product_id: str, recipe: dict) -> list[Observation]`. A recipe contains `scope_heading`, `exclude_headings`, `fields` mapping field→`{label_pattern, value_pattern, normalizer}`, `version`, and `expected_heading`. A source record contains source ID/URL/type, exact host allowlist, legal entity role, content format, recipe and terms-review metadata.

- [ ] **Step 1: Write identity/recipe tests.**

```python
from clickpe_pim.providers.entities import suggest_alias
from clickpe_pim.providers.extract import extract_provider

def test_fuzzy_match_is_only_a_suggestion():
    matches = suggest_alias("Muthoot Finance", {"Muthoot FinCorp":"muthoot_fincorp"})
    assert isinstance(matches, list)
    # No returned suggestion mutates a Mapping or approves legal equivalence.

def test_calculator_interest_is_excluded(make_capture):
    html = '<main><h2>Personal Loan</h2><p>APR 14–48% p.a.</p><h2>EMI calculator</h2><p>Interest 10–36%</p></main>'
    recipe = {"version":"1", "scope_heading":"Personal Loan", "expected_heading":"Personal Loan", "exclude_headings":["EMI calculator"], "fields":{"apr":{"label_pattern":"APR", "value_pattern":r"14–48% p\.a\.", "normalizer":"apr"}}}
    facts = extract_provider(html, make_capture(), "incred_pl", recipe)
    assert any(f.field == "apr" and f.state == "present" for f in facts)
    assert not any(f.field == "interest_rate" and f.state == "present" for f in facts)
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_mapping.py tests/test_providers.py -q`; expect missing imports.

- [ ] **Step 2: Create candidate mappings, never fabricated approvals.** Seed only observed URLs from the research note as `candidate`, `scope=unknown`, confidence 0 until inspected. An approved record must cite a captured paragraph supporting product/programme applicability, with reviewer/date. Map Prefr brand, Infocredit LSP and Hero lender separately. Distinguish Muthoot Finance/FinCorp until evidence resolves the relationship. Keep LAP unresolved if it has no named provider. Source URL discovery is manual and domain-reviewed; no automated search engine crawler.

```yaml
version: 1
sources:
  - source_id: incred_personal
    url: https://incred.com/personal-loan/
    source_type: official_product
    allowed_hosts: [incred.com, www.incred.com, assets.incred.com]
    format: html
    terms_checked_at: null
    collection_notes: candidate public product page; review terms before collection
mappings:
  - mapping_id: incred_pl_official
    product_id: incred_pl
    source_id: incred_personal
    role: lender
    scope: unknown
    review_state: candidate
    confidence: 0
    rationale: Official product candidate; ClickPe channel applicability requires review
```

- [ ] **Step 3: Implement exact aliases and scoped recipes.** Unicode-normalize/casefold/punctuation-normalize entity names; exact reviewed aliases can resolve the same role. RapidFuzz `fuzz.token_set_ratio` produces review suggestions only, even at 100. Recipe extraction removes `script/style/nav/footer`, calculator/example blocks and operates in the reviewed heading scope. Zero matches with a recognized section is supported absence only for a field that recipe covers; missing section is unsupported. Multiple non-equivalent matches become ambiguous and preserve all raw evidence. A changed expected heading causes an extraction-health failure.

- [ ] **Step 4: Research the fixed cohort in batches of five and add tested recipes.** For each product, search official product pages/terms/KFS/FAQ and capture at most a few relevant pages. Create one golden HTML excerpt plus expected values for each distinct recipe, preserving URL/hash provenance. Catalogue-wide regulatory claims are insufficient programme evidence. Brand homepages count as official-source discovery but not comparable-source coverage. For public PDFs use optional pypdf page text, page numbers and capture hashes; encrypted/image-only PDFs are unsupported pending manual transcription. If ordinary HTML lacks needed rendered content, use optional Playwright with the same host/pacing/access rules, save rendered DOM and network source metadata, and add a replay fixture; do not require browser rendering for the working JSON feed. An inaccessible/unmatched source stays unresolved in the denominator.

- [ ] **Step 5: Verify and commit mapping batches.** Add tests for role mismatch, expired/unreviewed mapping, ambiguous aliases, exact same-role alias, duplicate field matches and unsupported PDF. Run mapping/provider tests; all pass. `git add src/clickpe_pim/providers config/entities.yaml config/source_mapping.yaml tests/test_mapping.py tests/test_providers.py tests/fixtures/provider` then `git commit -m "feat: map official sources with reviewed programme scope"`. Repeat this bounded recipe/review/test/commit cycle for each batch; the deliverable is a complete mapping-status ledger for all 25 products, including unresolved cases.

### Task 9: Comparability gates, internal checks and structured findings

**Files:** Create `src/clickpe_pim/compare/{__init__,engine,checks}.py`, `tests/test_comparison.py`.

**Interfaces:** `compare_pair(left: Observation, right: Observation, mapping: Mapping, *, kind: str, settings: Settings) -> Comparison`; `check_product(product: Product, observations: list[Observation]) -> list[Comparison]`. `compare_pair` consumes healthy captures/age eligibility established by the pipeline; `Observation.state` still gates comparison. The `kind` argument is restricted to internal/external, with single-source checks produced by `check_product`.

- [ ] **Step 1: Write the decision-table tests.**

```python
from clickpe_pim.compare.engine import compare_pair
from clickpe_pim.contracts import Mapping, Value

def test_unconfirmed_programme_is_ambiguous(make_observation, settings):
    a = make_observation()
    b = make_observation(observation_id="other", value=Value(kind="money", upper="300000", unit="INR", qualifier="up_to"))
    m = Mapping(mapping_id="m", product_id="p1", source_id="s1", role="lender", scope="unknown", review_state="candidate", confidence=0.5, rationale="programme not established")
    result = compare_pair(a,b,m,kind="internal",settings=settings)
    assert result.status == "AMBIGUOUS"
    assert result.reason_code == "programme_unconfirmed"
```

Add `settings` fixture in `tests/conftest.py` by loading root `config.yaml`. Parametrize the additional cases below with `Value` and validated approved mappings; expected statuses are independent test data. Run `.\.venv\Scripts\python.exe -m pytest tests/test_comparison.py -q`; expect missing module.

| Left / right condition | Expected |
|---|---|
| Same reviewed programme, same upper amount, currency/bound semantics | MATCH |
| Same reviewed programme, 500000 versus 300000 maximum | DIFFERENT |
| Monthly 1% versus annual 12% | UNCOMPARABLE |
| Unknown rate period on either side | UNCOMPARABLE |
| Nominal interest versus APR | UNCOMPARABLE |
| Explicit flat versus reducing, or unknown versus known basis | UNCOMPARABLE |
| Same explicit rate period, both basis unknown | Compare advertised nominal rates; disclose basis unknown |
| One field supported absent, other healthy/present | MISSING_CLICKPE or MISSING_PROVIDER |
| Both absent, failed/unsupported parser, different field IDs | UNCOMPARABLE |
| Candidate/related programme or differing conditions | AMBIGUOUS |
| 24 months versus 2 years under the same approximation | MATCH |
| Continuous tenure range versus discrete allowed options | UNCOMPARABLE |
| Minimum 700 versus minimum 700 with NTC exception | AMBIGUOUS |

- [ ] **Step 2: Implement the gate order and comparison core.**

```python
def comparison_status(left, right, mapping):
    if left.field != right.field:
        return "UNCOMPARABLE", "different_field"
    if any(o.state in {"failed", "unsupported"} for o in (left,right)):
        return "UNCOMPARABLE", "extraction_unavailable"
    if mapping.review_state != "approved" or mapping.scope != "same_programme":
        return "AMBIGUOUS", "programme_unconfirmed"
    if any(o.state == "ambiguous" for o in (left,right)) or left.conditions != right.conditions:
        return "AMBIGUOUS", "conditional_or_multiple_claims"
    if left.state == right.state == "absent":
        return "UNCOMPARABLE", "both_absent"
    if left.state == "absent":
        return "MISSING_CLICKPE", "supported_absence_left"
    if right.state == "absent":
        return "MISSING_PROVIDER", "supported_absence_right"
    return None
```

The wrapper first validates matching product IDs, mapping product/source IDs and confidence ≥ configured minimum. The pipeline checks mapping effective dates against the captured source times before invoking this pure comparison function; an expired mapping produces an AMBIGUOUS comparison with reason `mapping_expired` directly from the orchestrator. Before numeric comparison check offer context, same kind/unit/currency/period/basis and bound/options semantics. A range and an `up_to` value can compare their shared upper endpoint without asserting that missing minima agree. Add `compared_endpoints: tuple[str,...] = ()` to `Comparison`; no overlapping endpoint → UNCOMPARABLE. A min-only and max-only observation cannot match. Decimal tolerance is per unit; rates use percentage points, not percentage error. Approximate versus exact tenure comparison emits approximation reason and tolerance, never a silent exact equality. Policy text on either side is UNCOMPARABLE numerically. Use exact normalized text/sets; no embedding guesses. Set comparison confidence to `min(left.confidence, right.confidence, mapping.confidence)`; it is a rule confidence, not a calibrated error probability.

- [ ] **Step 3: Preserve multi-source disagreements and neutral reasons.** Produce source-pair comparisons within approved scopes; deduplicate dashboard flags by product/field/source pair/reason/evidence fingerprint, not by discarding observations. Internal comparisons get `kind=internal`, so right-side label is “Comparison source,” not “Official.” `check_product` produces category-copy/identity/inverted-range/contradictory-claim review items with evidence IDs. Quarantined invalid normalized numbers remain raw assertions; they do not disappear. Copy template: `Possible {field} difference; review programme applicability and the cited source terms.` Unknown/conditional cases explain why the values cannot be directly compared.

- [ ] **Step 4: Verify evidence linkage and commit.** Ensure every non-MATCH comparison carries at least one observation ID; pair differences carry both and a mapping ID. Test numeric tolerances, duplicate sources, same-source conflicting bounds, multiple lenders, and marketing exclusion. Run comparison tests and contracts; all pass. `git add src/clickpe_pim/compare tests/test_comparison.py tests/conftest.py` then `git commit -m "feat: compare applicable terms and preserve ambiguity"`.

### Task 10: Completeness, freshness and transparent review priority

**Files:** Create `src/clickpe_pim/compare/scoring.py`, `src/clickpe_pim/monitor/{__init__,freshness,metrics}.py`, `tests/test_scoring.py`.

**Interfaces:** `age_days(last_verified: datetime | None, now: datetime) -> int | None`; `freshness_band(days: int | None) -> str`; `weighted_completeness(group_fractions: dict[str,float], weights: dict[str,float]) -> float`; `priority(severity: str, importance: float, confidence: float, days: int | None) -> int`; `ratio(numerator: int, denominator: int) -> float | None`.

- [ ] **Step 1: Write policy boundary tests.**

```python
import pytest
from clickpe_pim.monitor.freshness import freshness_band
from clickpe_pim.monitor.metrics import weighted_completeness, ratio
from clickpe_pim.compare.scoring import priority

def test_unknown_denominator_and_freshness():
    assert ratio(0,0) is None
    assert freshness_band(None) == "Unknown"
    assert [freshness_band(x) for x in [7,8,30,31,90,91]] == ["Fresh","Monitor","Monitor","Stale","Stale","High priority"]

def test_weighted_score_and_priority():
    assert weighted_completeness({"lender":1,"interest":0}, {"lender":0.5,"interest":0.5}) == 50
    assert priority("high",1,1,8) == 80
    assert priority("critical",1,1,100) == 100
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_scoring.py -q`; expect missing modules.

- [ ] **Step 2: Implement scoring with visible factors.**

```python
SEVERITY = {"low": .2, "medium": .5, "high": .8, "critical": 1.0}
def priority(severity, importance, confidence, days):
    factor = 1.0 if days is None or days <= 30 else 1.15 if days <= 90 else 1.25
    return min(100, round(100 * SEVERITY[severity] * importance * confidence * factor))

def weighted_completeness(group_fractions, weights):
    return 100 * sum(weights[g] * group_fractions.get(g,0) for g in weights) / sum(weights.values())

def ratio(numerator, denominator):
    return numerator / denominator if denominator else None
```

Validate fractions, confidence and importance in [0,1]. Severity defaults: wording low, eligibility/documents medium, amount/tenure/rate/major fee high; suspected identity/disclosure mismatch critical but explicitly unverified. Field importance is 1.0 lender/rates, .8 amount/tenure/fees, .6 eligibility, .4 repayment/documents, .2 wording. Mapping/source-health queue receives an independent urgency label; low numeric confidence cannot hide an unresolved lender.

- [ ] **Step 3: Implement group fractions and honest denominators.** Lender earns 1 only for an unambiguous resolved role/applicability. Amount = known min/max endpoints divided by two. Interest = maximum of the min/max endpoint fraction for eligible nominal interest or APR, not their sum; nominal requires stated period, policy-only earns zero numeric completeness but counts raw disclosure separately. Tenure = known min/max fraction, preserving discrete options. Fees has two equal slots: processing fee disclosure and at least one explicit other-charge disclosure (prepayment/foreclosure/late/stamp/other); a supported numeric/zero statement earns 1 in its slot, a scoped complex raw disclosure earns 0.5, marketing earns 0. Eligibility is the mean of three equal slots: age range, employment, income for personal loans/credit lines; business vintage, business type, turnover for business loans; age range, income, location restrictions for LAP. An age slot is its known-bound fraction; other supported explicit slots earn 1 and missing/unsupported/ambiguous slots earn 0. Documents earn 1 for a scoped explicit list and 0 for marketing-only language; repayment earns 1 for explicit frequency/flexibility. Every group is capped at 1. Do not redistribute missing-group weights; not-applicable removal requires documented product-policy justification. Show coverage (approved applicable official mapping with successful extraction / cohort size), source-discovery coverage separately, and compared endpoint count separately from observation count.

- [ ] **Step 4: Verify and commit.** Test future timestamps rejected, aware UTC day rounding, expired source/unknown mapping, raw policy-only rates, unsupported extraction distinct from non-disclosure, and cohort denominator including unresolved LAP. Run scoring tests; all pass. `git add src/clickpe_pim/compare/scoring.py src/clickpe_pim/monitor tests/test_scoring.py` then `git commit -m "feat: score review priority and publish metric denominators"`.

### Task 11: Historical changes without failure-induced removals

**Files:** Create `src/clickpe_pim/monitor/history.py`, `tests/test_history.py`, `tests/fixtures/history/two_runs.json`.

**Interfaces:** `Snapshot` frozen dataclass `(run_id: str, at: datetime, products: dict[str,Product], observations: list[Observation], healthy_sources: set[str], catalogue_complete: bool, synthetic: bool, extractor_version: str, mapping_hash: str, config_hash: str = "", source_statuses: dict[str,str] = field(default_factory=dict), cohort_ids: frozenset[str] = frozenset())`; import `field` from dataclasses. `source_statuses` values use Capture.status, retaining HTTP status as strings `"404"`/`"410"` for confirmed not-found responses. `products` contains the complete inventory, not only the cohort. `detect_changes(previous: Snapshot | None, current: Snapshot, prior_absences: dict[tuple[str,str], list[datetime]]) -> list[Change]`. Product-absence keys are `("product", product_id)`; field/source keys encode the source/field, and only healthy complete observations are counted.

- [ ] **Step 1: Write temporal and negative tests.**

```python
from dataclasses import replace
from clickpe_pim.monitor.history import Snapshot, detect_changes

def test_first_run_is_baseline(make_observation):
    o = make_observation()
    snap = Snapshot("r1",o.extracted_at,{},[o],{"s1"},True,True,"1","mapping1")
    assert detect_changes(None,snap,{}) == []

def test_failed_source_does_not_remove_field(make_observation):
    o = make_observation()
    old = Snapshot("r1",o.extracted_at,{},[o],{"s1"},True,True,"1","mapping1")
    new = replace(old,run_id="r2",observations=[],healthy_sources=set(),catalogue_complete=False)
    assert detect_changes(old,new,{}) == []
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_history.py -q`; expect missing module.

- [ ] **Step 2: Compare semantic values at stable grain.** Key observations by `(product_id, source_id, field, conditions)` within unchanged reviewed mappings; compare all normalized values in that scope as a sorted semantic set. Ignore whitespace/quote/locator drift when normalized semantics agree; log source hash change separately in source health. `VALUE_CHANGED` references old/new observation IDs. Supported present→absent creates pending field absence; two healthy observations ≥24h apart confirm FIELD_REMOVED. New supported fields create FIELD_ADDED after baseline, but newly added cohort IDs or source mappings first establish their own baseline. Changed extractor/config/mapping versions require replay of previous bytes under the new version before comparison; otherwise mark run non-comparable and log `method_changed`, not a product change.

- [ ] **Step 3: Implement product/source disappearance confirmation.** Only full inventory success can increment product absence; cohort expansion is labeled baseline for newly monitored existing products, not PRODUCT_ADDED. A genuinely new ID in two comparable inventories produces PRODUCT_ADDED. Explicit inactive status is retained as a lifecycle observation; removal still records the evidence and policy. A source 404/410 on two distinct collection attempts ≥24h apart yields SOURCE_DISAPPEARED; 403/429/5xx/CAPTCHA and parser failure yield source-health events only. Product removal never follows provider-page disappearance alone. Persist absence counters with run/source IDs in run manifests so replay cannot increment them twice.

- [ ] **Step 4: Verify deterministic replay and commit.** Test amount increase, lexical-only edit, added/removed field, duplicate run ID, two same-day absences, recovery before confirmation, source 404 versus 503, product rename, true new product, cohort addition and extraction-version change. Expected: exact event types, no duplicate/replayed events. Run history and repository tests; all pass. `git add src/clickpe_pim/monitor/history.py tests/test_history.py tests/fixtures/history` then `git commit -m "feat: detect verified changes across healthy snapshots"`.

### Task 12: Rerunnable pipeline, CLI and atomic dataset exports

**Files:** Create `src/clickpe_pim/{pipeline,cli,__main__}.py`, `src/clickpe_pim/storage/exports.py`, `tests/test_pipeline.py`; modify `storage/repository.py` for finalization and source-health metadata; create `tests/fixtures/catalogue/replay-manifest.json` and `README.md`.

**Interfaces:** `RunResult` frozen dataclass `(run_id: str, status: str, products_discovered: int, products_monitored: int, observations: int, comparisons: int, changes: int, errors: tuple[str,...])`; `run_monitor(config_path: Path, *, mode: Literal["live","replay"], replay_manifest: Path | None, output_root: Path, run_id: str | None = None) -> RunResult`; `export_run(repo: Repository, run_id: str, output_root: Path) -> dict[str,str]` returns file→SHA-256. `main(argv: list[str] | None = None) -> int` dispatches commands. `__main__.py` executes `raise SystemExit(main())`.

- [ ] **Step 1: Write an offline end-to-end test.**

```python
from pathlib import Path
from clickpe_pim.pipeline import run_monitor

def test_replay_is_deterministic_and_network_free(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("replay attempted network")
    monkeypatch.setattr("requests.sessions.Session.request", forbidden)
    manifest = Path("tests/fixtures/catalogue/replay-manifest.json")
    a = run_monitor(Path("config.yaml"),mode="replay",replay_manifest=manifest,output_root=tmp_path,run_id="fixture_r1")
    b = run_monitor(Path("config.yaml"),mode="replay",replay_manifest=manifest,output_root=tmp_path,run_id="fixture_r1")
    assert a == b
    assert a.status == "complete"
    assert (tmp_path / "data/processed/products.parquet").exists()
```

The replay fixture contains two synthetic products, two official fixture sources, one approved synthetic same-programme mapping per product, a known match and known amount difference, and exact capture hashes. Use fixed times/IDs. These identities and mappings are test-only; do not copy synthetic approvals into live config. Run `.\.venv\Scripts\python.exe -m pytest tests/test_pipeline.py -q`; expect missing modules.

- [ ] **Step 2: Implement orchestration and manifest contract.** Order: validate settings/mappings → start run → load robots/collect or validate replay hashes → persist captures → discover inventory → select/load cohort → extract healthy source assertions → save mapped relationships → compare recent applicable observations → score/check → detect changes → export → mark finalized. A source failure permits a partial run with last-good values visibly stale, but old values must not be labeled as verified this run. Block comparisons if either capture is older than 30 days or the pair differs by more than seven days; publish that reason in coverage. Record `run_id`, mode/synthetic flag, UTC start/end, config hash, mappings hash, cohort hash, git revision/dirty flag, Python/dependency versions, extractor version, capture list, per-source parse status, absence counters, comparison exclusions and artifact hashes. Every replay reads archived configs/mappings from its manifest, not today's config silently.

- [ ] **Step 3: Implement failure-safe publication and counters.** Persist raw captures even on downstream failure. Use a staging directory `data/snapshots/{run_id}.pending`; write typed Parquet, evidence index and metrics; verify hashes; atomically rename to `{run_id}`; then finalize the DB run in one transaction and atomically update `data/processed/latest.json`. Queries only use finalized runs. On restart recover a renamed-but-unfinalized snapshot by manifest/hash verification, or leave it unexposed and report failure. Never overwrite a finalized run with different input/config hashes. Log JSON lines with `run_id`, timestamp, event, source ID, URLs, pages requested/successful/failed, product count, fields extracted, error code; request counts exclude cache hits and report those separately. Never log cookies, full application links or forms.

- [ ] **Step 4: Add CLI commands and typed exports.**

```python
# cli.py: exact argparse subcommand surface
parser = argparse.ArgumentParser(prog="clickpe_pim")
sub = parser.add_subparsers(dest="command", required=True)
run = sub.add_parser("run")
run.add_argument("--config", type=Path, default=Path("config.yaml"))
run.add_argument("--mode", choices=["live", "replay"], required=True)
run.add_argument("--manifest", type=Path)
run.add_argument("--output-root", type=Path, default=Path("."))
run.add_argument("--run-id")
```

Reject replay without manifest and live with replay manifest. Exit codes: complete 0, partial 2, invalid config/fatal 1; print one JSON summary. `export_run` writes `clickpe_products.csv` (inventory), `clickpe_normalized.parquet`, `provider_normalized.parquet`, `products.parquet` (cohort presentation), `observations.parquet`, `comparisons.parquet`, `changes.parquet`, `source_mapping.csv`, and `metrics.json` into each immutable run directory. Update convenience exports under `data/processed/` only after finalization. Wide products expose `min_loan_amount`, `max_loan_amount`, `min_interest_rate`, `max_interest_rate`, `APR_min`, `APR_max`, `min_tenure_days`, `max_tenure_days`, currency/period/basis and evidence IDs; ambiguous multiple values stay NULL with state and linked observations. Set explicit Arrow decimal/bool/UTC timestamp columns; empty datasets keep their schemas. Use UTF-8 CSV with quoting for multiline evidence.

- [ ] **Step 5: Verify replay, crash recovery and commit.** Run `.\.venv\Scripts\python.exe -m clickpe_pim run --mode replay --manifest tests/fixtures/catalogue/replay-manifest.json --output-root .artifacts/replay`, then pipeline tests. Expected: two synthetic products, one known synthetic difference, no network, stable file hashes excluding the run receipt. Add tests for hash tampering, disk-write failure, one failed provider, missing catalogue, empty tables, duplicate replay and interrupted finalization. `git add src/clickpe_pim tests/test_pipeline.py tests/fixtures/catalogue/replay-manifest.json README.md` then `git commit -m "feat: orchestrate replayable monitoring and dataset exports"`.

### Task 13: Overview and evidence-first review queue

**Files:** Create `src/clickpe_pim/queries.py`, `app/dashboard.py`, `app/components.py`, `app/pages/1_Review_Queue.py`, `tests/test_queries.py`, `tests/test_dashboard.py`; modify `storage/repository.py` for append-only review events.

**Interfaces:** `load_overview(db_path: Path, *, include_synthetic: bool = False) -> dict`; `load_queue(db_path: Path, filters: dict[str,list[str]], *, include_synthetic: bool = False) -> pandas.DataFrame`; `load_evidence(db_path: Path, comparison_id: str) -> dict`; `record_review(db_path: Path, fingerprint: str, reviewer: str, disposition: str, note: str, at: datetime) -> None`. UI uses `CLICKPE_PIM_DB` environment variable, default `data/db/monitor.sqlite`; test-only synthetic visibility uses `CLICKPE_PIM_INCLUDE_SYNTHETIC=1` and displays a permanent synthetic banner.

- [ ] **Step 1: Test the empty dashboard and filtered evidence query.**

```python
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_dashboard_handles_missing_database(tmp_path, monkeypatch):
    monkeypatch.setenv("CLICKPE_PIM_DB", str(tmp_path / "missing.sqlite"))
    app = AppTest.from_file(str(Path("app/dashboard.py").resolve())).run()
    assert not app.exception
    assert any("No monitoring run" in x.value for x in app.info)
```

Query tests use the replay DB from Task 12 and assert one known flagged item, its two evidence IDs, expected filter result and exclusion of synthetic data by default. Run `.\.venv\Scripts\python.exe -m pytest tests/test_queries.py tests/test_dashboard.py -q`; expect missing files/functions.

- [ ] **Step 2: Implement read-only query views and overview.** Open SQLite read-only with `sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)`; missing DB returns an empty state without silently creating a new DB. Latest finalized run ID governs coherent aggregates. Overview shows numerator/denominator for coverage, cohort versus inventory, provider role counts, internal versus external review counts, current high-priority queue, last successful source check, seven-day changes and weighted completeness. Failed sources and incomplete run banner stay visible. Plotly charts: category/provider product counts, status/severity counts, completeness distribution. Display Unknown for missing metrics rather than zero. Do not chart mixed-rate periods together.

- [ ] **Step 3: Implement the review queue and source evidence panel.**

```python
st.title("Review Queue")
st.caption("Potential differences and missing information requiring review.")
selected = st.dataframe(queue, hide_index=True, on_select="rerun", selection_mode="single-row", key="review_table")
if selected.selection.rows:
    row = queue.iloc[selected.selection.rows[0]]
    evidence = load_evidence(db_path, row["comparison_id"])
    render_evidence(evidence)
```

`render_evidence(evidence: dict) -> None` lives in `app/components.py`: two columns with source labels/URLs, raw excerpts via `st.code` or `st.text`, normalized values, capture timestamps/hashes, programme rationale, comparison reason and confidence factors. Whitelist displayed links to http/https, escape raw text, never use `unsafe_allow_html` with source content. Queue filters: category, provider, severity, field, status plus internal/external/mapping/health lane. Show priority/product/provider/field/left/right/severity/confidence/last checked. Keep a `selectbox` fallback for row selection so AppTest and keyboard users can select an item reliably.

- [ ] **Step 4: Add explicit review dispositions with an audit trail.** Use a Streamlit form requiring reviewer, chosen outcome and note before `record_review`. Events append; current disposition is a view, never overwriting evidence. New value/source hash/reason changes generate a new fingerprint and reopen the item; identical subsequent findings retain review disposition. Missing-source runs cannot mark old flags resolved. Resolution requires a successful comparable match or an explicit reviewer decision. Tests assert resubmission deduplication and that a changed finding reopens.

- [ ] **Step 5: Verify the user journey and commit.** Start `.\.venv\Scripts\python.exe -m streamlit run app/dashboard.py --server.address 127.0.0.1 --server.port 8501`. Use the collaborative browser to inspect overview → filter → selected review → source evidence at desktop and narrow viewport. Check empty, partial, all-match and ambiguous cases. Run query/dashboard tests; expected no exceptions and correct metrics/evidence. `git add app src/clickpe_pim/queries.py src/clickpe_pim/storage/repository.py tests/test_queries.py tests/test_dashboard.py` then `git commit -m "feat: add overview and evidence review workflow"`.

### Task 14: Product, history and provider views

**Files:** Create `app/pages/2_Product_Explorer.py`, `3_Change_History.py`, `4_Providers.py`; modify `app/components.py`, `src/clickpe_pim/queries.py`, `tests/test_dashboard.py`, `tests/test_queries.py`.

**Interfaces:** Add `load_product(db_path: Path, product_id: str) -> dict`, `load_changes(db_path: Path, filters: dict[str,list[str]]) -> pandas.DataFrame`, `load_providers(db_path: Path) -> pandas.DataFrame`. Each query returns only finalized run data and exposes synthetic flags explicitly.

- [ ] **Step 1: Add page-navigation tests using the main entrypoint.**

```python
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_all_pages_handle_empty_state(tmp_path, monkeypatch):
    monkeypatch.setenv("CLICKPE_PIM_DB", str(tmp_path / "missing.sqlite"))
    at = AppTest.from_file(str(Path("app/dashboard.py").resolve())).run()
    for page in ["pages/1_Review_Queue.py", "pages/2_Product_Explorer.py", "pages/3_Change_History.py", "pages/4_Providers.py"]:
        at.switch_page(page).run()
        assert not at.exception
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_dashboard.py -q`; expected missing-page failure.

- [ ] **Step 2: Implement product comparison with original evidence.** Product selectbox uses ID as key and name/provider as label; side-by-side field table includes all expected fields and states. Each row can expand to all conflicting assertions, not just one chosen value. Legal entity roles display separately. A product with unknown lender shows “Unresolved lender” and mapping rationale; do not borrow a provider from a similarly named product. Source details reuse `render_evidence` where a comparison exists and show individual observation evidence otherwise.

- [ ] **Step 3: Implement history and provider metrics.** History filters product/provider/date range/change type and exposes old/new value and both timestamps/URLs. One baseline run shows “No historical comparison yet.” A synthetic-history toggle is off by default and visibly labeled. Weekly change counts use detection date in UTC, with display timezone Asia/Kolkata. Provider page counts unique products by verified role, and shows source coverage, completeness, open review counts, last verified and comparable loan amount/tenure ranges; rate summaries are split by APR/nominal and period. Avoid cross-programme average rates or arbitrary best-provider scores.

- [ ] **Step 4: Verify populated states and commit.** Query tests assert same-provider different programmes stay distinct, duplicate joins do not multiply products, and synthetic changes never enter real totals. Use AppTest plus the browser to verify selection/filters/source links and no horizontal clipping of critical values. Run query/dashboard tests; all pass. `git add app src/clickpe_pim/queries.py tests/test_queries.py tests/test_dashboard.py` then `git commit -m "feat: add product history and provider intelligence views"`.

### Task 15: Independent gold labels, evaluation and analytical report

**Files:** Create `src/clickpe_pim/{evaluate,report}.py`, `data/gold/{labels,flag_reviews}.jsonl`, `data/gold/split.yaml`, `docs/validation-protocol.md`, `tests/test_evaluation.py`, `tests/test_report.py`; modify CLI to expose `evaluate` and `report`.

**Interfaces:** `evaluate_labels(observations: list[Observation], labels: list[dict], *, split: str) -> dict`; `evaluate_flags(comparisons: list[Comparison], reviews: list[dict]) -> dict`; `build_report(db_path: Path, evaluation: dict, output_dir: Path) -> Path` writes Markdown, metrics JSON and evidence index and returns the Markdown path. Optional reportlab export adds PDF without changing figures.

- [ ] **Step 1: Write evaluation tests with an independent three-label oracle.**

```python
from clickpe_pim.evaluate import evaluate_labels, evaluate_flags

def test_abstention_is_not_ignored(make_observation):
    obs = make_observation()
    labels = [
      {"label_id":"a","product_id":"p1","source_id":"s1","capture_id":"c1","field":"loan_amount","state":"present","expected":{"kind":"money","upper":"500000","lower":None,"unit":"INR","qualifier":"up_to"},"split":"test"},
      {"label_id":"b","product_id":"p2","source_id":"s1","capture_id":"c1","field":"loan_amount","state":"present","expected":{"kind":"money","upper":"300000","lower":None,"unit":"INR","qualifier":"up_to"},"split":"test"},
      {"label_id":"c","product_id":"p3","source_id":"s1","capture_id":"c1","field":"loan_amount","state":"absent","expected":None,"split":"test"},
    ]
    out = evaluate_labels([obs],labels,split="test")
    assert out["present_numeric_correct"] == 1
    assert out["present_numeric_total"] == 2
    assert out["present_numeric_accuracy"] == 0.5
    assert out["labels_total"] == 3
    assert evaluate_flags([],[])["precision"] is None
```

Run `.\.venv\Scripts\python.exe -m pytest tests/test_evaluation.py tests/test_report.py -q`; expect missing modules.

- [ ] **Step 2: Define the gold-label contract and sampling procedure.** Freeze 20 cohort products selected deterministically across categories, amount formats, monthly/annual/unknown rates, internal ambiguities and source-health states. Label ten fields per product: loan_amount, interest_rate, apr, tenure, regulated_lender, repayment_frequency, processing_fee, minimum_credit_score, minimum_income (or business vintage for business loans), documents_raw. Use a captured ClickPe or official source chosen before reading extractor output. Each label also requires locator, quote, labeler, labeled_at, source hash, conditions and rationale; test fixtures above use the minimal evaluator shape. Save explicit 10 development/10 held-out product IDs in split.yaml, keeping all source records for a product together; report provider overlap as a limitation. A second review checks all held-out labels and every high-priority flag, recording disagreements. Unknown/ambiguous labels remain labeled states, never forced numeric values.

- [ ] **Step 3: Implement metrics that penalize missing predictions.** Join labels by product/source/capture/field; duplicate contradictory predictions score incorrect unless expected state is ambiguous and the expected assertion set is reproduced. Match numeric bounds/unit/period/basis/qualifier/conditions and tenure approximation; a correct number with wrong rate period is incorrect. Report numeric accuracy over gold-present numeric fields, state classification accuracy over all labels, missing-field recall, unsupported/abstention rate, and results per field/source/category/split. Report exact counts and Wilson 95% interval for binomial accuracy. Conflict precision = confirmed useful flags / reviewed flags; extraction issues/dismissed/legitimate differences are not automatically useful. Unreviewed flags remain outside that denominator but their count is always shown. A legitimate programme difference can be useful only when the reviewer explicitly marks it useful for the stated monitoring decision.

- [ ] **Step 4: Generate the report from the finalized database.** Implement deterministic sections: business question; catalogue/cohort; data/schema/sources; normalization/entity/programme methods; coverage/completeness; internal and external findings with evidence; change history; evaluation; limitations and actions. Every quantitative sentence references a metric key and every finding an evidence ID. Omit percentage when denominator is zero; write “not measured” for unreviewed precision and “one baseline only” for missing longitudinal evidence. No competitor observations without competitor data. Tables include denominators and capture dates. Report tests scan for known fixture values, broken evidence references and any unsupported `95%` success claim.

- [ ] **Step 5: Expose evaluation/report commands, verify and commit.** Add `evaluate --db PATH --labels PATH --split {dev,test} --output PATH` and `report --db PATH --evaluation PATH --output-dir PATH` to `main`. Example commands:

```powershell
.\.venv\Scripts\python.exe -m clickpe_pim evaluate --db data/db/monitor.sqlite --labels data/gold/labels.jsonl --split test --output reports/release-1/evaluation.json
.\.venv\Scripts\python.exe -m clickpe_pim report --db data/db/monitor.sqlite --evaluation reports/release-1/evaluation.json --output-dir reports/release-1
```

Run evaluation/report tests; expected oracle counts, no inferred live success. `git add src/clickpe_pim/evaluate.py src/clickpe_pim/report.py src/clickpe_pim/cli.py data/gold docs/validation-protocol.md tests/test_evaluation.py tests/test_report.py` then `git commit -m "feat: evaluate frozen labels and generate evidence report"`. Actual human-reviewed labels are completed in Task 17; empty label files yield explicit unmeasured results, never passing targets.

### Task 16: Reproducible installation, offline CI and durable monitoring state

**Files:** Create `uv.lock`, `requirements.txt`, `scripts/backup.py`, `scripts/restore.py`, `.github/workflows/ci.yml`, `.github/workflows/monitor.yml`, `docs/runbook.md`, `tests/test_backup.py`; modify `README.md`, `.gitignore`.

**Interfaces:** `create_backup(db_path: Path, data_root: Path, archive: Path) -> Path`; `restore_backup(archive: Path, destination: Path) -> Path`. These functions live in their corresponding scripts and include `argparse` entrypoints. Backup contains SQLite via its backup API, referenced raw evidence, immutable manifests/config versions, cohort and review history, plus a checksummed manifest. Enumerate only files referenced by finalized run manifests; exclude `data/backups/`, the destination archive, WAL/SHM sidecars and pending snapshots so an archive cannot recursively include itself. Restore targets a new directory and verifies paths/hashes/schema version before exposing data.

- [ ] **Step 1: Test backup/restore from a live WAL-mode database.** Add a test creating the replay database, leaving its connection open, taking `sqlite3.Connection.backup()` into a temporary standalone DB, building the archive and restoring it under `tmp_path / "restored"`. Assert product/evidence/review counts and every hash match. Add a malicious `../escape` archive member and reject it; reject missing evidence and modified hashes. Run `.\.venv\Scripts\python.exe -m pytest tests/test_backup.py -q`; expect missing modules.

- [ ] **Step 2: Lock and verify the dependency environment.** Run `uv lock`, `uv export --frozen --no-dev --format requirements-txt --output-file requirements.txt`, and `uv sync --frozen --extra dev`. Add optional browser/PDF extras only where exercised by source recipes/report output. Run `uv run --frozen --extra dev pytest -q` and `uv run --frozen --extra dev ruff check src app tests scripts`; fix real issues, record Python/package versions. Test installation once in a second temporary clean environment rather than relying on global packages. Do not pin to the reconnaissance environment without resolution/tests.

- [ ] **Step 3: Add offline CI with an OS matrix.** Use official `actions/checkout` and `actions/setup-python` releases verified at implementation time and pin immutable commit SHAs with version comments. Matrix `windows-latest`, `ubuntu-latest`, Python `3.12`; install `uv` at a pinned version selected by the lock verification, `uv sync --frozen --extra dev`, run pytest and Ruff, execute fixture replay, then upload test/replay artifacts. No live scraping on pull requests. Expected: both platforms pass without network except dependency installation. Document actual chosen action SHAs and uv version in the runbook; verifying these current external releases is an execution step, not a guessed constant in this plan.

- [ ] **Step 4: Prepare an opt-in monitor workflow with persistent-state restore.** Initially expose `workflow_dispatch` only, with boolean `initialize_baseline` default false and `concurrency: {group: clickpe-monitor, cancel-in-progress: false}`. Use read-only repository permissions plus artifact upload/download permission as required by the verified actions. Download the latest successful monitor state artifact through GitHub's artifact API; if missing/expired, fail unless `initialize_baseline=true`. Restore into a new path, validate checksums, then run `python -m clickpe_pim run --mode live`, accepting code 2 only as a marked partial run. In an `always()` step create and upload a consistent complete state archive; never upload a DB without its evidence and manifest. Document retention and require local durable archive copies; caches alone are not historical storage. No schedule trigger is added until Task 17 passes and the user elects recurring execution. When activated, one weekly UTC cron is sufficient; no need for daily lender requests initially.

- [ ] **Step 5: Verify recovery instructions and commit.** Run `.\.venv\Scripts\python.exe scripts/backup.py --db data/db/monitor.sqlite --data-root data --archive data/backups/state.zip` then `.\.venv\Scripts\python.exe scripts/restore.py --archive data/backups/state.zip --destination .artifacts/restored`. Expected: a verified new copy; original state unchanged. Run backup tests and update README/runbook with setup, replay, live, dashboard, label/evaluation, backup, recovery, source-blocked and parser-drift instructions. `git add uv.lock requirements.txt scripts .github docs/runbook.md README.md .gitignore tests/test_backup.py` then `git commit -m "build: lock dependencies and preserve monitoring state"`.

### Task 17: Live cohort validation, report and demo acceptance

**Files:** Populate `config/cohort.yaml`, `config/entities.yaml`, `config/source_mapping.yaml`, `data/gold/{labels,flag_reviews}.jsonl`, `data/gold/split.yaml`; generate runtime artifacts and `reports/release-1/{report.md,report.pdf,metrics.json,evidence-index.json,acceptance.md,demo.mp4}`; create `docs/demo-script.md`; update `README.md` with measured results.

**Interfaces:** Uses the tested CLI `run`, `evaluate`, `report`, backup/restore and Streamlit entrypoint. Produces a reviewed release acceptance ledger with one row per criterion below, evidence artifact path and outcome (`pass`, `fail`, `not_observable_yet`).

- [ ] **Step 1: Run the 12-product checkpoint and reconcile visible inventory.** Freeze raw captures using the collector, confirm permitted source access, verify seed products in the actual catalogue presentation, and save their mapping ledger. Use a separate checkpoint output root/cohort, then freeze the final 25-product cohort in release config. Command: `.\.venv\Scripts\python.exe -m clickpe_pim run --config config.yaml --mode live --output-root .`. Expected: actual discovery counts, transparent unresolved mappings/source failures and an evidence-backed queue; no guaranteed count of differences. If runtime access differs from planning, preserve failures and adjust recipes from observed bytes without inventing data.

- [ ] **Step 2: Expand/review the 25-product cohort and label the gold set.** Complete source research and reviewed mapping status for every fixed-cohort product. Independently label 200 source/field items where feasible following the product split. Evaluate development data, repair rules with regression fixtures, freeze code/config/labels, then evaluate held-out data once. If fixes follow held-out inspection, report it as development feedback and obtain a fresh held-out subset for a new claimed test result. Review every high/critical finding and a documented sample of other flags. Record actual total and reviewed denominators.

- [ ] **Step 3: Run the complete offline suite and evidence replay.** Run `uv run --frozen --extra dev pytest -q` and replay the finalized live manifest into `.artifacts/live-replay` with networking disabled by the test harness. Expected: identical normalized/comparison metrics for identical versions, valid evidence hashes, no missing foreign keys, all fields/flags traceable. Save test environment and results in acceptance.md. Verify `source_mapping.csv`, CSV/Parquet types, empty/unknown handling and every reported citation/source URL.

- [ ] **Step 4: Establish real history without manufacturing a change.** Run collection a second time after at least 24 hours, preserving both manifests/captures. Record elapsed observation window, changes or “no changes observed.” In the meantime demonstrate change detection only in the explicitly synthetic fixture mode. If the second real run is not yet possible, mark historical observation incomplete and say so; do not fabricate timestamps or keep an agent blocked waiting for a day. Publication can present a single baseline honestly, but the full definition of done remains open until the required history evidence exists.

- [ ] **Step 5: Generate and visually inspect the analytical report.** Execute the evaluation/report commands from Task 15 using actual held-out labels. Export 5–10 PDF pages using optional ReportLab, render them to images through the available PDF workflow, inspect every page for clipped tables/links and verify linked evidence. Include catalogue/provider counts, missing-field patterns, high-priority review examples, internal/external split, intermediary LSP relationships, measured coverage/accuracy/precision and temporal limitations. No marketplace-gap or competitor claim without data. README numbers must be sourced from the same `metrics.json`.

- [ ] **Step 6: Validate and record the working UI.** Follow `docs/demo-script.md`: 0–20s overview and observation date; 20–45s filter/select one real review item; 45–75s product comparison and both source excerpts; 75–100s mapping rationale and review action; 100–120s real history or an explicitly synthetic demonstration. Use a supported screen recorder, review the exported MP4 for legible values/no private tabs, and save `reports/release-1/demo.mp4`. If recording tools are unavailable, deliver the script and mark video outstanding; do not claim a recording exists. Confirm every dashboard view in the browser and label network/visual validation limits.

- [ ] **Step 7: Commit the measured release and hand off.** Commit reviewed mapping/config, approved minimal fixtures/labels, docs and a shareable report subset; keep bulk raw captures/database out of Git. Include artifact size/content checks before staging. Run `git status --short`, then `git add README.md config data/gold docs/demo-script.md` and `git commit -m "docs: record validated monitoring release results"`. Local Git completion does not imply a GitHub repository was published. Publishing a remote repository, enabling schedules and contacting ClickPe are separate handoff actions.

## Release acceptance ledger

| Criterion | Evidence and required outcome |
|---|---|
| Discovery | Full feed captured; visible presentation reconciled; inventory/cohort counts distinct |
| Cohort | 25 actual stable IDs or documented availability shortfall; no coverage-driven replacement |
| Official coverage | Approved applicable healthy sources / fixed cohort; target ≥90%, actual shown |
| Mapping | Brands/LSPs/lenders/programmes separate; all unresolved cases visible |
| Extraction | Held-out numeric-field target >95%; correct unit/period/basis/qualifier required; actual sample/interval disclosed |
| Gold | Approximately 200 independently reviewed labels, fixed split and frozen source hashes |
| Review precision | Explicit reviewed-flag numerator/denominator; no guessed precision |
| Evidence | 100% of reported flags resolve to captured bytes and exact observations |
| Comparison | Monthly/annual, APR/nominal, different programmes, conditional eligibility and calculator examples cannot become false matches/differences |
| Failure safety | 403/429/5xx/CAPTCHA/schema drift never remove products/fields or replace good values |
| Replay | Frozen live run reproduces results offline with original versions/timestamps |
| History | Baseline plus real later snapshot; synthetic transitions separately tested/labeled; no requirement that a real change must occur |
| Dashboard | Five pages usable, filters/evidence work, empty/partial states tested and visually inspected |
| Report/demo | Source-backed 5–10-page report and reviewed 60–120s demo, or explicit outstanding artifact |
| Operations | Windows clean install, offline CI, consistent backup/restore; recurring job remains opt-in |
| Claims | No regulatory accusation, fabricated metric, implied live validation from fixtures, or asserted competitor coverage |

Targets are performance goals, not permission to distort the sample. A below-target result still has analytical value, but acceptance must state the shortfall and the next specific correction. No fixed number of discrepancies is required.

## Task dependency and implementation rhythm

`1 → (2,3,4) → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17`.

Tasks 2/3 and storage are logically independent after the contracts, but use inline execution unless the user chooses delegation. If subagents are chosen, assign one bounded task, review spec adherence then implementation quality before the next task, and keep shared contract edits serialized. Human mapping and label review are explicit work, not automatic success assumptions.

Each task follows the shown red/green tests and commit gate. The 2–5 minute checkboxes are intended to be split into individual fixture/rule/view edits when a repeated source batch is involved; a cohort-wide research/labeling acceptance item takes longer and is a release checklist, not a single coding action. Do not compress source review, labels or visual validation to meet an aspirational 2–3 or 5–8 day estimate.

## Planning self-review record

- Every original brief section is mapped in the specification's coverage index; future categories/competitors/ML are explicitly outside this first release.
- Live feasibility changed the discovery design to a public JSON feed and added category-contamination/form-config tests; source counts are reconnaissance only.
- File ownership, data grains, public interfaces, test commands, failure cases, evaluation denominators and handoff artifacts are stated above.
- The saved draft had 17 tasks, 80 tracked steps and 23 Python snippets; the placeholder scan found no prohibited markers, and all 23 snippets parsed with Python's AST parser. This checks plan syntax, not runtime correctness of an unbuilt application. Self-review corrected shared money-unit inheritance, storage-test parent rows, factory IDs, mapping-date ownership, history health inputs and backup self-inclusion.
- No implementation, environment installation, Git initialization, deployment or scheduler activation was performed while writing this plan.
