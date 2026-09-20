# ClickPe PIM Vercel UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a distinctive, accessible, read-only ClickPe Product Intelligence Monitor interface that is statically built from one finalized snapshot and deployed on Vercel without changing the existing backend or monitoring logic.

**Architecture:** Keep the Python/SQLite pipeline and Streamlit review workflow unchanged. A separate Next.js app under `web/` opens an explicitly selected SQLite snapshot in read-only/query-only mode during the local build, projects only public stored records into a temporary view model, statically generates the interface, and deploys the prebuilt static output to Vercel; no database, write endpoint, or domain calculation reaches the deployment.

**Tech Stack:** Node.js 22.19.x, npm 10.9.x, Next.js 16.3.5 App Router, React 19.3.0, TypeScript 7.0.2, Zod 4.6.5, better-sqlite3 13.0.3, vanilla CSS, Archivo Variable 5.3.0, Source Serif 4 Variable 5.3.0, Vitest 5.0.1, Testing Library 16.3.3, Playwright 1.63.0, axe-core 4.13.0, Vercel CLI 59.23.2.

**Spec:** `docs/specs/2026-09-20-clickpe-pim-vercel-ui.md`; product semantics remain defined by `docs/specs/2026-09-19-clickpe-product-intelligence-monitor.md`.

## Global Constraints

This is a UI-only change. Create implementation files only under `web/**`; outside `web/**`, only this plan and its design specification may be added.

Do not modify `src/clickpe_pim/**`, `app/**`, `tests/**`, `config/**`, `config.yaml`, `pyproject.toml`, `requirements.txt`, `uv.lock`, database schema, pipeline, queries, collectors, extractors, normalizers, mappings, comparison, scoring, monitoring, evaluation, reports, or existing Streamlit behavior.

Open SQLite with `readonly: true`, `fileMustExist: true`, and `PRAGMA query_only=ON`; never issue INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, VACUUM, or write-oriented PRAGMA statements.

The TypeScript layer may select, filter, sort, count, group, and format stored records for presentation. It must not normalize finance values, infer mappings, compare terms, calculate priority/completeness/freshness, or create change events.

Do not expose a server action, mutation route, public API, or review form. The unchanged Streamlit app remains the review-write surface.

Do not publish the SQLite file, review events, reviewer identities, notes, local paths, environment values, or unselected records. Build output must be scanned before deployment.

Use a fixed `PIM_EXPECTED_RUN_ID` for any non-demo build. Reject missing, unfinished, failed, or synthetic production runs.

Synthetic content is allowed only when `PIM_UI_DEMO=1`; every route then shows a persistent “Synthetic interface preview” banner.

Preserve exact stored comparison language and the statement “Review items are not findings of error or wrongdoing.” Never convert a review item into an accusation or regulatory conclusion.

Keep brand, LSP, lender, marketplace, parent, programme, and segment roles distinct. Do not rank providers.

Use sentence case, active voice, plain verbs, and specific empty/error copy from the design specification. Do not use uppercase eyebrows, decorative numbering, appended arrow glyphs, or generic promotional copy.

Meet WCAG 2.2 AA, support keyboard-only use, reduced motion, Windows high contrast, 200% zoom, and widths from 390 px upward.

Use TDD, path-scoped Git staging, and one focused commit per task. Never run `git add .`; existing user changes in `src/clickpe_pim/monitor/metrics.py` and `tests/test_scoring.py` must remain untouched and unstaged.

Vercel project linking, preview deployment, and production deployment are external changes. Obtain explicit approval immediately before each action; approval for a preview does not authorize production.

---

## Verified starting state and architectural decision

- The repository already contains a committed Python pipeline, SQLite storage, read-only query layer, and five-view Streamlit dashboard.
- Current commits end at `d69ec47 docs: record offline release acceptance`.
- The working tree already has user changes in `src/clickpe_pim/monitor/metrics.py` and `tests/test_scoring.py`; this plan neither stages nor edits them.
- `data/db/` is ignored and no production database is committed. A Vercel Git build therefore cannot safely discover the local database.
- The frontend will use a local prebuilt Vercel deployment: select a local finalized run, statically build only its public projection, scan the output, and deploy `.vercel/output`. The raw database never goes to Vercel.
- Next.js static export supports pre-rendered App Router pages and `generateStaticParams`; request-dependent features, cookies, Server Actions, and dynamic route generation are intentionally excluded.
- The repository has no Git remote. Linking or deploying to Vercel is deferred to the approval-gated final task.

## Protected-path preflight

Before Task 1, capture the current protected diff without altering it:

```powershell
New-Item -ItemType Directory -Force web\.artifacts | Out-Null
git diff -- src app tests config config.yaml pyproject.toml requirements.txt uv.lock | Set-Content -Encoding utf8 web\.artifacts\protected-before.patch
git status --short
```

Expected: the recorded patch contains the pre-existing metrics/scoring work; no implementation task stages those paths. `web/.artifacts/` will be ignored before the first commit.

## File map and responsibilities

| File | Responsibility |
|---|---|
| `web/package.json`, `web/package-lock.json` | Pinned UI dependencies and build/test/deploy scripts |
| `web/tsconfig.json`, `web/next.config.ts`, `web/eslint.config.mjs` | Strict TypeScript, static export, image and lint configuration |
| `web/vitest.config.ts`, `web/playwright.config.ts`, `web/test/setup.ts` | Unit, DOM, browser, and accessibility test configuration |
| `web/.gitignore`, `web/README.md` | UI-local ignored output, setup, snapshot selection, and Vercel runbook |
| `web/scripts/prepare-snapshot.mjs` | Read one explicit finalized SQLite run without writes and emit a public view model |
| `web/scripts/assert-deploy-output.mjs` | Reject raw databases, environment values, local paths, reviewer data, and fixture secrets in deploy output |
| `web/src/lib/snapshot/types.ts` | Zod schema and TypeScript types for the only data contract consumed by pages |
| `web/src/lib/snapshot/get-snapshot.ts` | Server-only loader for `.cache/public-snapshot.json` |
| `web/src/lib/format.ts` | Display-only date, decimal-string, normalized-value, label, and hash formatting |
| `web/src/app/layout.tsx`, `web/src/app/globals.css` | Fonts, metadata, design tokens, reset, focus, grid, reduced-motion, and high-contrast rules |
| `web/src/components/app-shell.tsx` | Skip link, desktop rail, mobile navigation, run state, and synthetic banner |
| `web/src/components/status-mark.tsx` | Text-plus-shape rendering for stored comparison and source states |
| `web/src/components/evidence-seam.tsx` | ClickPe evidence, stored decision, and comparison evidence workbench |
| `web/src/components/run-register.tsx` | Continuous overview register for stored run and count values |
| `web/src/components/empty-state.tsx` | Directional route-specific empty and unavailable messages |
| `web/src/app/page.tsx` | Comparison-first overview and run health |
| `web/src/components/review-ledger.tsx` | Client-side queue filters, URL state, keyboard-friendly rows, and result count |
| `web/src/app/reviews/page.tsx` | Review queue route |
| `web/src/app/reviews/[comparisonId]/page.tsx` | Statically generated evidence detail route |
| `web/src/components/product-ledger.tsx` | Client-side product search and stable product links |
| `web/src/app/products/page.tsx` | Product index route |
| `web/src/app/products/[productId]/page.tsx` | Statically generated observations and mapping detail route |
| `web/src/app/changes/page.tsx` | Stored change history route |
| `web/src/app/providers/page.tsx` | Role/programme relationship summary route |
| `web/src/app/not-found.tsx` | Clear invalid snapshot-route recovery |
| `web/test/fixtures/public-snapshot.json` | Explicitly synthetic public view model for tests and protected previews |
| `web/test/create-fixture-db.ts` | UI-owned minimal SQLite fixture used only to test read-only projection |
| `web/test/config.test.ts` | Static/UI boundary and configuration checks |
| `web/test/prepare-snapshot.test.ts` | Read-only database projection, redaction, and run-gate tests |
| `web/src/**/*.test.tsx`, `web/src/**/*.test.ts` | Focused route/component/format tests co-located with their owner |
| `web/e2e/navigation.spec.ts`, `web/e2e/accessibility.spec.ts`, `web/e2e/responsive.spec.ts` | User journey, axe, keyboard, zoom, and viewport checks |
| `web/e2e/visual.spec.ts` | Review screenshots at desktop, tablet, and mobile sizes |
| `web/test/assert-deploy-output.test.ts` | Leakage scanner pass/fail fixtures |

## Shared public view-model contract

All routes consume this contract from `web/src/lib/snapshot/types.ts`; no component imports SQLite or backend Python:

```ts
export type ComparisonStatus =
  | "MATCH"
  | "DIFFERENT"
  | "MISSING_CLICKPE"
  | "MISSING_PROVIDER"
  | "UNCOMPARABLE"
  | "AMBIGUOUS";

export type EvidenceView = {
  observationId: string;
  sourceId: string;
  sourceType: string;
  sourceUrl: string | null;
  retrievedAt: string;
  sha256: string | null;
  field: string;
  state: "present" | "absent" | "ambiguous" | "unsupported" | "failed";
  rawText: string;
  locator: string;
  context: string;
  confidence: number;
  value: {
    kind: string;
    lower: string | null;
    upper: string | null;
    text: string | null;
    boolean: boolean | null;
    options: string[];
    unit: string | null;
    period: string;
    basis: string;
    qualifier: string;
    approximate: boolean;
  } | null;
};

export type ReviewView = {
  comparisonId: string;
  fingerprint: string | null;
  productId: string;
  productName: string;
  field: string;
  kind: string;
  status: ComparisonStatus;
  reason: string;
  reasonCode: string;
  confidence: number;
  priority: number | null;
  severity: string | null;
  state: string | null;
  mapping: {
    role: string;
    programme: string | null;
    segment: string | null;
    geography: string | null;
    scope: string;
    reviewState: string;
    confidence: number;
    rationale: string;
  } | null;
  left: EvidenceView | null;
  right: EvidenceView | null;
};

export type ProductView = {
  productId: string;
  name: string;
  category: string;
  providerName: string | null;
  activeStatus: string;
  clickpeUrl: string | null;
  cohortMember: boolean;
  observations: EvidenceView[];
  mappings: Array<NonNullable<ReviewView["mapping"]>>;
  reviewCount: number;
};

export type PublicSnapshot = {
  schemaVersion: 1;
  buildId: string;
  run: {
    runId: string;
    finishedAt: string;
    status: "complete" | "partial";
    synthetic: boolean;
    catalogueComplete: boolean;
  };
  overview: {
    inventoryProducts: number;
    cohortProducts: number;
    reviewItems: number;
    highPriorityItems: number;
    failedSources: number;
    coverageNumerator: number;
    coverageDenominator: number;
    recentChanges: number;
    finalizedRuns: number;
  };
  products: ProductView[];
  reviews: ReviewView[];
  changes: Array<{
    changeId: string;
    productId: string;
    productName: string;
    sourceId: string | null;
    field: string | null;
    type: string;
    detectedAt: string;
  }>;
  providers: Array<{
    entityId: string;
    role: string;
    programmes: number;
    products: number;
    approvedSources: number;
    openReviews: number;
  }>;
};

export function getSnapshot(): PublicSnapshot;
export function formatValue(evidence: EvidenceView): string;
export function formatTimestamp(value: string): string;
export function formatField(value: string): string;
```

### Task 1: Create the isolated static frontend workspace

**Files:**
- Create: `web/package.json`, `web/package-lock.json`, `web/tsconfig.json`, `web/next.config.ts`, `web/eslint.config.mjs`
- Create: `web/vitest.config.ts`, `web/playwright.config.ts`, `web/test/setup.ts`, `web/.gitignore`, `web/README.md`
- Test: `web/test/config.test.ts`

**Interfaces:**
- Consumes: Node.js `>=22.19 <23`; no Python or backend module import.
- Produces: `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`, `npm run preview`, and a static `out/` site.

- [ ] **Step 1: Create the package manifest and install the exact dependency set.**

Use this `web/package.json` shape, then run `npm install` from `D:\Clickpe-PIM\web` to generate the lockfile:

```json
{
  "name": "clickpe-pim-web",
  "version": "0.1.0",
  "private": true,
  "engines": { "node": ">=22.19 <23" },
  "scripts": {
    "dev": "next dev",
    "prepare:data": "node scripts/prepare-snapshot.mjs",
    "prebuild": "npm run prepare:data",
    "build": "next build",
    "preview": "serve out -l 3000",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:e2e": "playwright test",
    "test:visual": "playwright test e2e/visual.spec.ts"
  },
  "dependencies": {
    "@fontsource-variable/archivo": "5.3.0",
    "@fontsource-variable/source-serif-4": "5.3.0",
    "next": "16.3.5",
    "react": "19.3.0",
    "react-dom": "19.3.0",
    "server-only": "0.0.1",
    "zod": "4.6.5"
  },
  "devDependencies": {
    "@axe-core/playwright": "4.13.0",
    "@playwright/test": "1.63.0",
    "@testing-library/dom": "10.4.2",
    "@testing-library/react": "16.3.3",
    "@testing-library/user-event": "14.6.7",
    "@types/better-sqlite3": "9.6.0",
    "@types/node": "26.6.2",
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "@vitejs/plugin-react": "6.1.1",
    "better-sqlite3": "13.0.3",
    "eslint": "10.11.0",
    "eslint-config-next": "16.3.5",
    "jsdom": "30.1.0",
    "serve": "14.2.6",
    "typescript": "7.0.2",
    "vitest": "5.0.1"
  }
}
```

Expected: `npm install` finishes without peer-dependency errors and creates `package-lock.json` with lockfile version 3.

- [ ] **Step 2: Write a failing configuration/boundary test.**

`web/test/config.test.ts` must read `next.config.ts` and `package.json`, then assert `output: "export"`, `images.unoptimized: true`, no API/start script, Node 22, and no dependency on Streamlit/Python packages:

```ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("static UI boundary", () => {
  it("cannot acquire a backend runtime", () => {
    const pkg = JSON.parse(readFileSync("package.json", "utf8"));
    const config = readFileSync("next.config.ts", "utf8");
    expect(pkg.engines.node).toBe(">=22.19 <23");
    expect(pkg.scripts).not.toHaveProperty("start:api");
    expect(config).toContain('output: "export"');
    expect(config).toContain("unoptimized: true");
    expect(JSON.stringify(pkg)).not.toMatch(/streamlit|clickpe_pim|fastapi/i);
  });
});
```

- [ ] **Step 3: Run the test and confirm the expected failure.**

Run: `npm test -- test/config.test.ts`

Expected: FAIL because `next.config.ts` does not exist.

- [ ] **Step 4: Add strict configuration and local ignore rules.**

`next.config.ts` must export:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
};

export default nextConfig;
```

Use `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`, and alias `@/*` to `./src/*` in `tsconfig.json`. Configure Vitest for `jsdom`, `test/setup.ts`, and tests under `src/**/*.test.*` plus `test/**/*.test.*`. Configure Playwright's `webServer.command` as `npm run preview` at `http://127.0.0.1:3000`; the browser tasks build the synthetic site before starting Playwright.

`web/.gitignore` must include:

```text
node_modules/
.next/
out/
.vercel/
.cache/
.artifacts/
playwright-report/
test-results/
```

- [ ] **Step 5: Document the boundary and verify the scaffold.**

`web/README.md` must state that the site is read-only, that review writes remain in Streamlit, that `PIM_UI_DEMO=1` is synthetic, and that real builds require `PIM_SNAPSHOT_PATH` plus `PIM_EXPECTED_RUN_ID`. Run:

```powershell
npm test -- test/config.test.ts
npm run typecheck
npm run lint
```

Expected: all commands pass; the build command is deferred until the snapshot preparation script exists.

- [ ] **Step 6: Commit only the isolated scaffold.**

```powershell
git add -- web/package.json web/package-lock.json web/tsconfig.json web/next.config.ts web/eslint.config.mjs web/vitest.config.ts web/playwright.config.ts web/test/setup.ts web/test/config.test.ts web/.gitignore web/README.md
git diff --cached --name-only
git commit -m "build: scaffold isolated Vercel UI"
```

Expected staged paths: only the listed `web/**` files.

### Task 2: Project a finalized SQLite run into a public read-only snapshot

**Files:**
- Create: `web/scripts/prepare-snapshot.mjs`
- Create: `web/src/lib/snapshot/types.ts`, `web/src/lib/snapshot/get-snapshot.ts`, `web/src/lib/format.ts`
- Create: `web/test/fixtures/public-snapshot.json`, `web/test/create-fixture-db.ts`
- Test: `web/test/prepare-snapshot.test.ts`, `web/src/lib/format.test.ts`

**Interfaces:**
- Consumes: `PIM_SNAPSHOT_PATH`, `PIM_EXPECTED_RUN_ID`, or `PIM_UI_DEMO=1`; SQLite `user_version=1`; the stored record JSON from the existing schema.
- Produces: `web/.cache/public-snapshot.json` validated as `PublicSnapshot`; `getSnapshot(): PublicSnapshot`; the display-only formatters defined above.

- [ ] **Step 1: Create a failing read-only projection test with a UI-owned database fixture.**

`createFixtureDb(path)` creates only the tables/columns selected by the UI script, inserts one finalized non-synthetic run, two products, one `DIFFERENT` comparison, its stored priority, two observations/captures/sources, one approved mapping, and one change. Insert a second synthetic run for the rejection test. Insert sentinel private strings `Private Reviewer Token` and `C:\private\capture.html` in unselected review/path fields.

The test runs the script in a child process and asserts source bytes are unchanged:

```ts
const before = createHash("sha256").update(readFileSync(dbPath)).digest("hex");
const result = spawnSync(process.execPath, ["scripts/prepare-snapshot.mjs"], {
  cwd: process.cwd(),
  env: {
    ...process.env,
    PIM_SNAPSHOT_PATH: dbPath,
    PIM_EXPECTED_RUN_ID: "ui_fixture_run",
    PIM_PUBLIC_SNAPSHOT_OUT: outPath,
  },
  encoding: "utf8",
});
expect(result.status).toBe(0);
expect(createHash("sha256").update(readFileSync(dbPath)).digest("hex")).toBe(before);
const raw = readFileSync(outPath, "utf8");
expect(raw).not.toContain("Private Reviewer Token");
expect(raw).not.toContain("C:\\private\\capture.html");
```

Also assert the script fails for a missing run ID, unfinished run, failed run, `user_version != 1`, and synthetic run when `PIM_UI_DEMO` is absent.

- [ ] **Step 2: Run the projection test and confirm the expected failure.**

Run: `npm test -- test/prepare-snapshot.test.ts`

Expected: FAIL because `scripts/prepare-snapshot.mjs` and snapshot types do not exist.

- [ ] **Step 3: Define the Zod contract and safe display formatters.**

Implement the shared types above as Zod schemas, export `PublicSnapshot = z.infer<typeof publicSnapshotSchema>`, and have `getSnapshot()` read and parse `.cache/public-snapshot.json` with `server-only` semantics. It must throw `The public UI snapshot was not prepared.` if the file is absent and must never fall back to querying SQLite from a route.

`formatValue` must use stored strings only:

```ts
export function formatValue(evidence: EvidenceView): string {
  const value = evidence.value;
  if (!value) return formatField(evidence.state);
  if (value.text) return value.text;
  if (value.boolean !== null) return value.boolean ? "Yes" : "No";
  if (value.options.length) return value.options.join(", ");
  const bounds = [value.lower, value.upper].filter((part): part is string => part !== null);
  const joined = bounds.length === 2 ? `${bounds[0]}–${bounds[1]}` : bounds[0] ?? "Unknown";
  return [joined, value.unit, value.period !== "unknown" ? value.period : null]
    .filter(Boolean)
    .join(" ");
}
```

Tests cover zero as a real stored value, `null` as unknown, boolean false as “No,” annual/unknown period, long SHA wrapping, and invalid timestamps returning “Unknown time” rather than inventing a date.

- [ ] **Step 4: Implement a strictly read-only projection script.**

Open the selected path only as follows:

```js
const db = new Database(resolve(snapshotPath), {
  readonly: true,
  fileMustExist: true,
});
db.pragma("query_only = ON");
if (db.pragma("user_version", { simple: true }) !== 1) {
  throw new Error("Unsupported SQLite schema version.");
}
```

For real builds, require `PIM_EXPECTED_RUN_ID` and select exactly:

```sql
SELECT run_id, finished_at, status, catalogue_complete, synthetic, manifest_json
FROM scrape_runs
WHERE run_id = ? AND finished_at IS NOT NULL AND status IN ('complete', 'partial')
```

Then select records with these bounded statements:

```sql
SELECT record_json FROM product_snapshots WHERE run_id=? ORDER BY product_id;
SELECT c.record_json AS comparison_json, f.fingerprint, f.priority, f.severity, f.state
FROM comparisons c LEFT JOIN conflicts f ON f.comparison_id=c.comparison_id
WHERE c.run_id=? ORDER BY COALESCE(f.priority,-1) DESC,c.product_id,c.comparison_id;
SELECT a.record_json AS observation_json, cap.record_json AS capture_json,
       s.url, s.source_type
FROM product_attributes a
JOIN captures cap ON cap.capture_id=a.capture_id
JOIN sources s ON s.source_id=a.source_id
WHERE a.run_id=? ORDER BY a.observation_id;
SELECT record_json FROM mappings
WHERE product_id IN (SELECT product_id FROM product_snapshots WHERE run_id=?)
ORDER BY product_id,mapping_id;
SELECT record_json FROM changes
WHERE product_id IN (SELECT product_id FROM product_snapshots WHERE run_id=?)
ORDER BY detected_at DESC,change_id;
SELECT COUNT(*) AS finalized_runs
FROM scrape_runs
WHERE finished_at IS NOT NULL AND status IN ('complete','partial') AND synthetic=0;
```

Project fields by explicit property selection. Never spread `record_json`. Omit `reviewed_by`, `reviewed_at`, `effective_*`, evidence local paths, `review_events`, registration claims, and every field not present in `PublicSnapshot`. Count only stored rows and stored conflict priorities; do not recalculate them. Parse `manifest_json.cohort_ids` and `manifest_json.source_parse_status` for cohort/source-health display. Use the final count query only for `overview.finalizedRuns`; it does not select or expose records from another run.

Serialize keys in stable order, calculate `buildId = sha256(serialized snapshot without buildId)`, validate with `publicSnapshotSchema`, and atomically replace the output JSON. When `PIM_UI_DEMO=1`, validate and copy `test/fixtures/public-snapshot.json`; preserve `run.synthetic=true`.

- [ ] **Step 5: Prove run gates, redaction, determinism, and no writes.**

Run:

```powershell
npm test -- test/prepare-snapshot.test.ts src/lib/format.test.ts
$env:PIM_UI_DEMO="1"
npm run prepare:data
Get-FileHash .cache\public-snapshot.json -Algorithm SHA256
npm run prepare:data
Get-FileHash .cache\public-snapshot.json -Algorithm SHA256
Remove-Item Env:PIM_UI_DEMO
```

Expected: tests pass; repeated demo hashes match; generated JSON says `synthetic: true`; the fixture database hash remains unchanged.

- [ ] **Step 6: Commit the data adapter without backend edits.**

```powershell
git add -- web/scripts/prepare-snapshot.mjs web/src/lib/snapshot web/src/lib/format.ts web/src/lib/format.test.ts web/test/fixtures/public-snapshot.json web/test/create-fixture-db.ts web/test/prepare-snapshot.test.ts
git diff --cached --name-only
git commit -m "feat: add read-only UI snapshot adapter"
```

### Task 3: Build the evidence-register design system and app shell

**Files:**
- Create: `web/src/app/layout.tsx`, `web/src/app/globals.css`, `web/src/app/not-found.tsx`
- Create: `web/src/components/app-shell.tsx`, `web/src/components/status-mark.tsx`, `web/src/components/evidence-seam.tsx`, `web/src/components/empty-state.tsx`
- Test: `web/src/components/app-shell.test.tsx`, `web/src/components/evidence-seam.test.tsx`

**Interfaces:**
- Consumes: `PublicSnapshot.run`, `ReviewView`, `formatValue`, and the design tokens in the UI specification.
- Produces: `AppShell`, `StatusMark`, `EvidenceSeam`, and `EmptyState` used by every route.

- [ ] **Step 1: Write failing semantic and copy tests.**

Render `AppShell` with the synthetic fixture and assert a skip link, `navigation` landmark, all five route links, active-page `aria-current`, and the visible text “Synthetic interface preview.” Render `EvidenceSeam` and assert source headings, exact quotes, stored reason, source URLs, locator, SHA-256, and the neutral limitation sentence. Assert no `button` or form labelled “Record review.”

- [ ] **Step 2: Run the focused tests and confirm the expected failure.**

Run: `npm test -- src/components/app-shell.test.tsx src/components/evidence-seam.test.tsx`

Expected: FAIL because the components do not exist.

- [ ] **Step 3: Implement the token sheet and typographic rules.**

Import Archivo Variable in `layout.tsx` and Source Serif 4 only in `EvidenceSeam`. Define exact tokens in `globals.css`:

```css
:root {
  --archive-ink: #142831;
  --cold-stock: #eef3f5;
  --source-white: #ffffff;
  --register-blue: #2f5bea;
  --review-amber: #a65f00;
  --verified-green: #176b55;
  --rule: color-mix(in srgb, var(--archive-ink) 24%, transparent);
  --focus: 2px solid var(--register-blue);
  --step--2: 0.75rem;
  --step--1: 0.875rem;
  --step-0: 1rem;
  --step-1: 1.25rem;
  --step-2: 1.563rem;
  --step-3: 1.953rem;
  --step-4: 2.441rem;
}
```

Set `font-variation-settings: "wdth" 100` for body and `"wdth" 90` for route titles. Add visible focus, skip-link, `overflow-wrap:anywhere` for hashes, reduced-motion, `forced-colors`, and 390 px rules. Do not add gradients, shadows, rounded card grids, or automatic entrance animation.

- [ ] **Step 4: Implement the application shell and source-safe primitives.**

`AppShell` renders desktop rail, compact mobile header/navigation, run state, a synthetic banner when required, and `<main id="main-content">`. `StatusMark` maps stored values to readable text plus `data-status`; CSS supplies distinct solid/dashed/double markers so color is not the only signal.

`EvidenceSeam` uses the exact `5 / 2 / 5` grid at desktop and source → decision → source order below 760 px. It renders external links only when `new URL(url).protocol` is `http:` or `https:`; otherwise it displays “Source URL unavailable.” Raw evidence is rendered as text in `<blockquote>`, never as HTML.

- [ ] **Step 5: Verify semantics, types, lint, and mobile CSS.**

Run:

```powershell
npm test -- src/components/app-shell.test.tsx src/components/evidence-seam.test.tsx
npm run typecheck
npm run lint
```

Expected: all pass; tests find one main landmark, source-safe links, synthetic disclosure, and no review mutation.

- [ ] **Step 6: Commit the design foundation.**

```powershell
git add -- web/src/app/layout.tsx web/src/app/globals.css web/src/app/not-found.tsx web/src/components/app-shell.tsx web/src/components/status-mark.tsx web/src/components/evidence-seam.tsx web/src/components/empty-state.tsx web/src/components/*.test.tsx
git commit -m "feat: add evidence-register UI foundation"
```

### Task 4: Implement the comparison-first overview

**Files:**
- Create: `web/src/app/page.tsx`, `web/src/components/run-register.tsx`
- Test: `web/src/app/page.test.tsx`, `web/src/components/run-register.test.tsx`

**Interfaces:**
- Consumes: `getSnapshot()`, `EvidenceSeam`, stored `reviews`, and stored/row-count overview fields.
- Produces: the `/` route with the highest stored-priority two-sided review and a continuous run register.

- [ ] **Step 1: Write failing overview tests for populated, all-match, and partial states.**

Assert the demo overview begins with the highest stored-priority two-sided review, keeps its exact stored reason, renders the nine register values, and states “Review items are not findings of error or wrongdoing.” With an all-match snapshot, assert “No two-source review item is available in this snapshot.” With a partial run or failed source, assert the visible direction “Some sources did not complete. Stored values may be older than this run.”

- [ ] **Step 2: Run tests and confirm the expected failure.**

Run: `npm test -- src/app/page.test.tsx src/components/run-register.test.tsx`

Expected: FAIL because the route and register do not exist.

- [ ] **Step 3: Implement the overview selection and register without domain recomputation.**

Select only for presentation:

```ts
const featured = snapshot.reviews
  .filter((item) => item.status !== "MATCH" && item.left && item.right)
  .toSorted((a, b) => (b.priority ?? -1) - (a.priority ?? -1))[0] ?? null;
```

Do not change priority or status. `RunRegister` renders a single ruled strip with inventory products, monitored cohort, applicable official-source coverage as `numerator/denominator`, review items, high priority, source failures, recent changes, finalized runs, and run status. Use `<dl>` rather than nine card containers.

- [ ] **Step 4: Implement directional empty and partial states.**

If snapshot preparation succeeded but has zero products, render “This finalized snapshot contains no products. Select another run before publishing.” If coverage denominator is zero, display “Unknown” rather than `0%`. If `run.synthetic`, do not use “live,” “current,” or “verified” in route copy.

- [ ] **Step 5: Run focused and broader checks.**

```powershell
npm test -- src/app/page.test.tsx src/components/run-register.test.tsx
npm run typecheck
npm run lint
```

Expected: all pass; no metric-card class or gradient is present.

- [ ] **Step 6: Commit the overview.**

```powershell
git add -- web/src/app/page.tsx web/src/app/page.test.tsx web/src/components/run-register.tsx web/src/components/run-register.test.tsx
git commit -m "feat: add comparison-first overview"
```

### Task 5: Implement the read-only review queue and evidence routes

**Files:**
- Create: `web/src/components/review-ledger.tsx`
- Create: `web/src/app/reviews/page.tsx`, `web/src/app/reviews/[comparisonId]/page.tsx`
- Test: `web/src/components/review-ledger.test.tsx`, `web/src/app/reviews/review-detail.test.tsx`

**Interfaces:**
- Consumes: `ReviewView[]`, `EvidenceSeam`, stored priorities/statuses/reasons, and static comparison IDs.
- Produces: `/reviews/` filters and `/reviews/[comparisonId]/` static pages; no write control.

- [ ] **Step 1: Write failing queue interaction tests.**

Use Testing Library/user-event to assert filters named “Field,” “Status,” “Severity,” and “Product”; filtered result count; clear-filter behavior; keyboard activation of a row link; stable `/reviews/cmp-difference/` href; and the exact empty result “No review items match these filters. Clear filters to see the full queue.” Assert raw evidence is absent from the queue rows so dense data remains scannable.

- [ ] **Step 2: Write failing detail/static-route tests.**

Assert `generateStaticParams()` returns every comparison ID in the snapshot, unknown IDs call `notFound()`, one-sided comparisons use the specified missing-evidence sentence, and stored mapping scope/rationale appear without reviewer identity. Assert the page contains no form, text input, submit button, or POST behavior.

- [ ] **Step 3: Run focused tests and confirm expected failures.**

Run: `npm test -- src/components/review-ledger.test.tsx src/app/reviews/review-detail.test.tsx`

Expected: FAIL because the queue and routes do not exist.

- [ ] **Step 4: Implement URL-backed client filters and ledger rows.**

`ReviewLedger` initializes from `URLSearchParams`, applies exact set membership to already stored fields, and updates the query string with `history.replaceState` after user action. It must not calculate severity or priority. Each row uses a real `<a>` to the static detail route and displays priority, product, field, status, severity, and shortened reason. At 760 px, rows become labelled list items while preserving DOM order and full accessible names.

- [ ] **Step 5: Implement static evidence details and neutral limitations.**

Use:

```ts
export function generateStaticParams() {
  return getSnapshot().reviews.map(({ comparisonId }) => ({ comparisonId }));
}

export const dynamicParams = false;
```

The route title is `{productName}: {formatField(field)}`. Below `EvidenceSeam`, show stored kind, reason code, confidence, priority, severity, and mapping scope/rationale in a definition list. Copy: “This view presents stored public evidence and a comparison decision. It does not establish an error, violation, or suitable loan.”

- [ ] **Step 6: Verify queue/detail behavior and commit.**

```powershell
npm test -- src/components/review-ledger.test.tsx src/app/reviews/review-detail.test.tsx
npm run typecheck
npm run lint
git add -- web/src/components/review-ledger.tsx web/src/components/review-ledger.test.tsx web/src/app/reviews
git commit -m "feat: add read-only evidence review workflow"
```

### Task 6: Implement product discovery and evidence-preserving detail

**Files:**
- Create: `web/src/components/product-ledger.tsx`
- Create: `web/src/app/products/page.tsx`, `web/src/app/products/[productId]/page.tsx`
- Test: `web/src/components/product-ledger.test.tsx`, `web/src/app/products/product-detail.test.tsx`

**Interfaces:**
- Consumes: `ProductView[]`, stored observations/mappings, and static native product IDs.
- Produces: searchable `/products/` and static `/products/[productId]/` pages without collapsing claims.

- [ ] **Step 1: Write failing product search and state tests.**

Assert case-insensitive search across name, native product ID, category, and provider display name. Verify “Unknown,” “Absent,” “Ambiguous,” “Unsupported,” and “Failed” stay distinct. Verify zero and false are displayed as values, contradictory observations render as separate rows, and unresolved lender copy appears when no approved same-programme lender mapping is stored.

- [ ] **Step 2: Run tests and confirm the expected failure.**

Run: `npm test -- src/components/product-ledger.test.tsx src/app/products/product-detail.test.tsx`

Expected: FAIL because the product components/routes do not exist.

- [ ] **Step 3: Implement the searchable product ledger.**

Render name, product ID, category, provider, active status, observation count, and review count. Use a single search input labelled “Search products.” Search changes only visible rows; it never changes stored `activeStatus` or cohort membership. The zero-result message is “No products match this search. Clear the search to see the full product list.”

- [ ] **Step 4: Implement static product detail without deduplication.**

Generate all product params and set `dynamicParams=false`. Group only for visual headings with `Map<string, EvidenceView[]>`; preserve array order and render every observation. Each observation row shows source type, state, `formatValue`, unit/period/basis when stored, raw evidence, locator, evidence ID, retrieval time, and source link. Render mapping role, programme, segment, geography, scope, review state, confidence, and rationale; omit reviewer fields by contract.

- [ ] **Step 5: Verify product routes and commit.**

```powershell
npm test -- src/components/product-ledger.test.tsx src/app/products/product-detail.test.tsx
npm run typecheck
npm run lint
git add -- web/src/components/product-ledger.tsx web/src/components/product-ledger.test.tsx web/src/app/products
git commit -m "feat: add product evidence explorer"
```

### Task 7: Implement stored change history and provider relationships

**Files:**
- Create: `web/src/app/changes/page.tsx`, `web/src/app/providers/page.tsx`
- Test: `web/src/app/changes/page.test.tsx`, `web/src/app/providers/page.test.tsx`

**Interfaces:**
- Consumes: `PublicSnapshot.changes` and `PublicSnapshot.providers` exactly as projected.
- Produces: `/changes/` reverse-chronological history and `/providers/` relationship ledger.

- [ ] **Step 1: Write failing state and wording tests.**

For changes, assert stored event type, product, field, source, and timestamp appear; no event is inferred for a product without a change row; the empty copy is “No stored historical change is available for this run.” For providers, assert entity/role rows remain separate and the visible sentence says “Roles and programmes stay separate. This view does not rank providers.” Assert there is no score, star, position, or “best provider” copy.

- [ ] **Step 2: Run tests and confirm expected failures.**

Run: `npm test -- src/app/changes/page.test.tsx src/app/providers/page.test.tsx`

Expected: FAIL because the routes do not exist.

- [ ] **Step 3: Implement the history ledger.**

Render stored rows in the already projected reverse-chronological order. Use exact readable labels for `VALUE_CHANGED`, `PRODUCT_ADDED`, `PRODUCT_REMOVED`, `SOURCE_DISAPPEARED`, `FIELD_ADDED`, and `FIELD_REMOVED`; do not infer causality. Show “Baseline is not a historical change” beside the method note.

- [ ] **Step 4: Implement the provider relationship matrix.**

Rows contain entity ID, role, programme count, product count, approved applicable source count, and open review count. Use column headers that state counts, not quality. On mobile, render one relationship per bordered row with the same semantic labels.

- [ ] **Step 5: Verify both routes and commit.**

```powershell
npm test -- src/app/changes/page.test.tsx src/app/providers/page.test.tsx
npm run typecheck
npm run lint
git add -- web/src/app/changes web/src/app/providers
git commit -m "feat: add history and provider relationship views"
```

### Task 8: Add browser accessibility, responsive, and visual critique gates

**Files:**
- Create: `web/e2e/navigation.spec.ts`, `web/e2e/accessibility.spec.ts`, `web/e2e/responsive.spec.ts`, `web/e2e/visual.spec.ts`
- Modify: `web/src/app/globals.css` only for failures found by the checks

**Interfaces:**
- Consumes: the synthetic static build served from `out/`.
- Produces: a keyboard-complete user journey, zero serious/critical axe findings, responsive assertions, and review screenshots in `web/.artifacts/visual/`.

- [ ] **Step 1: Write the failing browser journey.**

Navigate overview → filtered review queue → review detail → source link visibility → product detail → changes → providers. Assert route titles, synthetic banner persistence, and no network request using POST/PUT/PATCH/DELETE. Tab from the browser chrome, activate the skip link, reach navigation and the first review link, then open it with Enter.

- [ ] **Step 2: Add axe and responsive assertions.**

Run `AxeBuilder` on all routes and fail on serious/critical findings. At 390×844, 768×1024, and 1440×1024 assert:

```ts
const overflow = await page.evaluate(() =>
  document.documentElement.scrollWidth > document.documentElement.clientWidth
);
expect(overflow).toBe(false);
```

At mobile width, assert evidence DOM order is ClickPe source → stored decision → comparison source. Emulate `reducedMotion: "reduce"` and assert computed transition durations are `0s`. Set browser zoom to 200% with `document.body.style.zoom="2"` and verify navigation plus evidence remain reachable.

- [ ] **Step 3: Run the browser suite and observe real failures.**

```powershell
npx playwright install chromium
$env:PIM_UI_DEMO="1"
npm run build
npm run test:e2e
Remove-Item Env:PIM_UI_DEMO
```

Expected before final CSS/accessibility repair: at least one assertion may fail; record the exact selector and viewport in the test output rather than weakening the assertion.

- [ ] **Step 4: Fix only demonstrated UI issues and rerun the full gate.**

Use semantic HTML or focused CSS changes in `web/**`; do not alter stored data or backend paths. Run:

```powershell
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
```

Expected: all pass; `out/` contains only static HTML/CSS/JS/font assets.

- [ ] **Step 5: Capture and critique the three required screenshots.**

`visual.spec.ts` saves:

```text
web/.artifacts/visual/overview-1440x1024.png
web/.artifacts/visual/review-768x1024.png
web/.artifacts/visual/review-390x844.png
```

Inspect them at full size. Review against the design brief: comparison-first opening, evidence seam legibility, source/decision hierarchy, typography, density, mobile order, no generic KPI cards, no clipped hashes, and no decorative rule without information. Remove one nonfunctional visual treatment if the page feels over-accessorized; document the removed treatment in the commit body.

- [ ] **Step 6: Commit the verified browser quality floor.**

```powershell
git add -- web/e2e web/src/app/globals.css
git commit -m "test: verify responsive accessible UI"
```

Do not add screenshot artifacts.

### Task 9: Scan the prebuilt output and deploy approval-gated Vercel previews

**Files:**
- Create: `web/scripts/assert-deploy-output.mjs`
- Test: `web/test/assert-deploy-output.test.ts`
- Modify: `web/package.json`, `web/README.md`

**Interfaces:**
- Consumes: `out/` and `.vercel/output/`; an explicit local run selected for real builds.
- Produces: a fail-closed static-output scan and, only after approval, a Vercel preview URL; production remains a separately approved action.

- [ ] **Step 1: Write failing leakage-scanner tests.**

Create temporary output trees and assert rejection of `*.sqlite`, `*.sqlite-wal`, `*.db`, `.env*`, `Private Reviewer Token`, `reviewed_by`, `review_events`, Windows drive paths, `PIM_SNAPSHOT_PATH`, and a seeded fixture secret. Assert ordinary HTML containing public evidence text, SHA-256, source URLs, locators, and the word “review” passes.

- [ ] **Step 2: Run the scanner tests and confirm the expected failure.**

Run: `npm test -- test/assert-deploy-output.test.ts`

Expected: FAIL because `assert-deploy-output.mjs` does not exist.

- [ ] **Step 3: Implement the fail-closed output scanner and wire it into scripts.**

Recursively inspect filenames and UTF-8 text files under the supplied directory. Skip binary font/image bytes but always reject database/environment filename extensions. Exit non-zero with every offending relative path and rule. Add:

```json
{
  "scripts": {
    "audit:out": "node scripts/assert-deploy-output.mjs out",
    "audit:vercel": "node scripts/assert-deploy-output.mjs .vercel/output"
  }
}
```

The scanner must not print the matched secret value; print only the rule name and file path.

- [ ] **Step 4: Prove a synthetic static build is safe before any external action.**

```powershell
$env:PIM_UI_DEMO="1"
npm run build
npm run audit:out
Remove-Item Env:PIM_UI_DEMO
Get-ChildItem out -Recurse -File | Where-Object { $_.Extension -in '.sqlite','.db' }
```

Expected: build and audit pass; the final command returns no files; every page visibly states it is synthetic.

- [ ] **Step 5: Verify the protected backend diff is byte-for-byte unchanged and commit the deploy gate.**

```powershell
git diff -- src app tests config config.yaml pyproject.toml requirements.txt uv.lock | Set-Content -Encoding utf8 web\.artifacts\protected-after.patch
$before = Get-Content -Raw web\.artifacts\protected-before.patch
$after = Get-Content -Raw web\.artifacts\protected-after.patch
if ($before -ne $after) { throw "Protected backend diff changed during UI implementation." }
git add -- web/scripts/assert-deploy-output.mjs web/test/assert-deploy-output.test.ts web/package.json web/package-lock.json web/README.md
git commit -m "build: add Vercel output safety gate"
```

Expected: protected patch comparison succeeds; commit contains only `web/**`.

- [ ] **Step 6: Stop and obtain explicit approval to link/create the Vercel project.**

Explain that this creates external Vercel state and that the first deployment will use the clearly labelled synthetic fixture. After approval, run from `D:\Clickpe-PIM\web`:

```powershell
npx vercel@59.23.2 link --yes --project clickpe-pim-ui
$env:PIM_UI_DEMO="1"
npx vercel@59.23.2 build
npm run audit:vercel
npx vercel@59.23.2 deploy --prebuilt
Remove-Item Env:PIM_UI_DEMO
```

Expected: Vercel returns a preview URL, the preview is protected according to the project setting, all routes load, and every route shows “Synthetic interface preview.” If the project is not protected, do not share the URL until the user decides the intended audience.

- [ ] **Step 7: Stop and obtain separate approval before a non-synthetic preview or production deployment.**

After approval and only when `data/db/monitor.sqlite` contains a finalized non-synthetic run, resolve its exact run ID without changing the database:

```powershell
$env:PIM_SNAPSHOT_PATH = (Resolve-Path '..\data\db\monitor.sqlite').Path
$env:PIM_EXPECTED_RUN_ID = (& '..\.venv\Scripts\python.exe' -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); r=c.execute(\"SELECT run_id FROM scrape_runs WHERE finished_at IS NOT NULL AND status IN ('complete','partial') AND synthetic=0 ORDER BY finished_at DESC LIMIT 1\").fetchone(); print(r[0] if r else '')" $env:PIM_SNAPSHOT_PATH).Trim()
if (-not $env:PIM_EXPECTED_RUN_ID) { throw 'No finalized non-synthetic run exists.' }
npx vercel@59.23.2 build --prod
npm run audit:vercel
npx vercel@59.23.2 deploy --prebuilt --prod
Remove-Item Env:PIM_SNAPSHOT_PATH
Remove-Item Env:PIM_EXPECTED_RUN_ID
```

Expected: preparation selects exactly the printed run ID; output scan passes; production shows no synthetic banner; the deployed build contains no raw database or private fields. Record the returned deployment URL in the handoff message, not in source code.

## Release validation matrix

| Requirement | Test/evidence |
|---|---|
| Backend and logic untouched | protected patch equality plus path-scoped commits |
| Read-only source access | database SHA before/after, SQLite read-only/query-only test, no mutation SQL |
| No private data in deployment | projection redaction tests plus `audit:out`/`audit:vercel` |
| Neutral evidence framing | component/route copy tests |
| Synthetic truthfulness | persistent banner E2E test and production run rejection |
| Overview and five views | navigation E2E journey |
| Stored values remain distinct | product/detail unit tests |
| No provider ranking | provider wording/absence tests |
| Keyboard and WCAG floor | keyboard journey plus axe serious/critical gate |
| Mobile and zoom usability | overflow, DOM-order, reduced-motion, 200% zoom tests |
| Distinctive design | required screenshot critique against the evidence-register spec |
| Vercel readiness | local `vercel build`, output audit, protected preview review |

## Planning self-review record

- **Spec coverage:** The UI-only boundary, attached frontend design process, Vercel use, all existing dashboard views, evidence semantics, accessibility, responsive behavior, screenshot critique, privacy, synthetic-state disclosure, and approval gates each map to a task and validation row.
- **Prohibited-pattern scan:** The saved plan contains no deferred implementation markers or vague test/error-handling instructions; each conditional state has exact behavior and copy.
- **Type consistency:** `PublicSnapshot`, `ReviewView`, `EvidenceView`, `ProductView`, `getSnapshot`, `formatValue`, `formatTimestamp`, `formatField`, environment variable names, route names, and commands are consistent across all tasks.
- **Boundary review:** No implementation task modifies or stages a backend, Streamlit, configuration, Python dependency, or existing backend-test path.
