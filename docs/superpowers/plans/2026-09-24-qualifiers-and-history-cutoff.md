# Qualifiers and Historical Snapshot Cutoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve stored numeric qualifiers and prevent events or run counts after the selected run from appearing in historical frontend snapshots.

**Architecture:** Keep formatting in the existing display helper and constrain SQLite projection queries using the selected finalized run's `finished_at`. Preserve the stored values and database; exercise projection through its existing subprocess test harness.

**Tech Stack:** Node 22.19, TypeScript, Vitest, better-sqlite3, Next.js static export, Playwright.

**Spec:** `docs/specs/2026-09-20-clickpe-pim-vercel-ui.md`; the user's September 24 report supplies the two bug reproductions. No separate bug specification exists.

## Global Constraints

Only frontend files under `web/**` and this new plan may change.
Keep Python, Streamlit, database schema, collection, normalization, mapping, comparison, scoring, monitoring, evaluation and reporting unchanged.
Open the database read-only with query-only enabled; preserve its file hash.
Format stored values without recalculating financial or monitoring decisions.
Do not publish private fields, database files, local paths or unselected records.
Preserve distinct missing-evidence states and synthetic-data labeling; reject synthetic runs for real builds.
Preserve existing visual, accessibility and responsive design requirements from the linked spec; no styling changes are needed.
Node must satisfy `>=22.19 <23`; add no dependencies.
Keep unrelated `.restored-preview/` and `state.zip` untouched.
The user explicitly requests immediate inline implementation without confirmation. The execution helper skill is not installed; execute this plan inline with red/green test checkpoints.
Deployment settings and email sending are outside these two code fixes.

---

## File map

- `web/src/lib/format.ts`: render stored numeric qualifiers and approximation.
- `web/src/lib/format.test.ts`: verify qualified bounds and unchanged text, boolean, zero and range behavior.
- `web/scripts/prepare-snapshot.mjs`: filter historical changes and finalized-run counts at the selected completion time.
- `web/test/prepare-snapshot.test.ts`: seed later history and verify cutoff, ordering, counts and read-only projection.
- This plan: record tasks and actual validation outcomes.

### Task 1: Preserve numeric qualifiers

**Files:** Modify `web/src/lib/format.ts:30`; test `web/src/lib/format.test.ts`.

**Interfaces:** Consumes `EvidenceView.value`, including string `qualifier` and boolean `approximate`; preserves `formatValue(evidence: EvidenceView): string`.

- [x] **Step 1: Add table-driven regression cases**

```ts
it.each([
  ["up_to", null, "120000.0", false, "Up to 120000.0 INR"],
  ["from", "0", null, false, "From 0 INR"],
  ["range", "100", "200", false, "100–200 INR"],
  ["exact", "100", null, true, "Approximately 100 INR"],
  ["up_to", null, "100", true, "Approximately Up to 100 INR"],
  ["conditional", "100", null, false, "Conditional 100 INR"],
  ["policy", "100", null, false, "Policy 100 INR"],
])("preserves %s numeric semantics", (qualifier, lower, upper, approximate, expected) => {
  expect(formatValue(evidence({ value: { ...evidence().value!, qualifier, lower, upper, approximate } }))).toBe(expected);
});
```

Add text-precedence assertions for stored policy and conditional text; retain existing zero, boolean and missing-state assertions.

- [x] **Step 2: Verify failure**

From `web/`: `npm test -- src/lib/format.test.ts`. Expected: qualifier and approximation assertions fail.

- [x] **Step 3: Prefix numeric display without changing bounds**

Before the existing return, derive:

```ts
const qualifier = value.qualifier === "exact" || value.qualifier === "range"
  ? null
  : value.qualifier === "up_to" ? "Up to" : formatField(value.qualifier);
```

Prepend `value.approximate ? "Approximately" : null, qualifier` to the existing joined/unit/period array. Keep text, boolean and options early returns unchanged.

- [x] **Step 4: Verify focused and broader tests**

From `web/`: `npm test -- src/lib/format.test.ts`, then `npm run lint` and `npm run typecheck`. Expected: all pass.

- [x] **Step 5: Review and commit this unit**

From repository root: `git diff --check`, then `git add web/src/lib/format.ts web/src/lib/format.test.ts` and `git commit -m "fix: preserve qualifiers in evidence values"`.

### Task 2: Bound history to the selected run

**Files:** Modify `web/scripts/prepare-snapshot.mjs:138`; test `web/test/prepare-snapshot.test.ts`.

**Interfaces:** Existing `prepare(dbPath, outPath, runId)` subprocess projects `changes`, `overview.recentChanges`, `overview.finalizedRuns` and `buildId`. `createFixtureDb(path)` supplies a real fixture run ending `2026-09-20T08:00:00Z`.

- [x] **Step 1: Add historical regression fixture in the test**

Create a temporary fixture DB using existing helpers. Insert changes using:

```ts
const insert = db.prepare("INSERT INTO changes VALUES (?,?,?,?)");
for (const [id, at] of [
  ["earlier", "2026-09-19T08:00:00Z"],
  ["offset_before", "2026-09-20T13:29:59+05:30"],
  ["offset_after", "2026-09-20T07:30:00-01:00"],
  ["later", "2026-09-24T08:00:00Z"],
]) {
  const row = { change_id: id, product_id: "fixture_difference", source_id: null, field: "loan_amount", type: "VALUE_CHANGED", detected_at: at };
  insert.run(id, row.product_id, at, JSON.stringify(row));
}
```

Insert a later finalized non-synthetic run into `scrape_runs` and copy the selected run's `product_snapshots` into it. Close DB; hash it. Project the September 20 run and assert change IDs equal `["change_difference", "offset_before", "earlier"]`, recentChanges is 3 and finalizedRuns is 1. Project the later run and assert all 5 changes and finalizedRuns 2. Assert unchanged DB hash. Existing fixture event exactly at cutoff must remain included.

- [x] **Step 2: Verify failure**

From `web/`: `npm test -- test/prepare-snapshot.test.ts`. Expected: September 20 includes future events and wrong run count.

- [x] **Step 3: Apply timestamp cutoff and chronological ordering**

In change query append `AND julianday(detected_at) <= julianday(?)`; order by `julianday(detected_at) DESC,change_id`; bind `.all(expectedRunId, run.finished_at)`.

In finalized-run count append `AND julianday(finished_at) <= julianday(?)`; bind `.get(run.finished_at)`. This compares instants across stored UTC offsets, includes the completion boundary and excludes future records.

- [x] **Step 4: Validate projection and full frontend**

From `web/`: `npm test`, `npm run lint`, `npm run typecheck`. Expected: all pass.

PowerShell from `web/`: `$env:PIM_UI_DEMO='1'; npm run build`. Expected: synthetic static export succeeds. Then `npm run audit:out` and `npm run test:e2e`; expected: output audit and browser suite pass.

- [x] **Step 5: Review and commit this unit**

From repository root: `git diff --check`, then `git add web/scripts/prepare-snapshot.mjs web/test/prepare-snapshot.test.ts` and `git commit -m "fix: bound snapshot history to selected run"`.

Record real validation results below and commit the plan with `git add docs/superpowers/plans/2026-09-24-qualifiers-and-history-cutoff.md` and `git commit -m "docs: record qualifier and history fix plan"`.

## Execution evidence

- Regression tests first failed in seven cases, reproducing lost qualifiers and future history leakage.
- After implementation: 48 frontend tests pass, including numeric qualifiers, preserved policy text, cutoff boundary, UTC-offset ordering, later-run selection and database hash preservation.
- Frontend lint and TypeScript pass.
- Synthetic static build, output audit and all 18 Playwright browser tests pass.
- Real static build for local finalized run `20260921T135606Z` and output audit pass; 36 product pages are generated. Generated `brightloans_pl` HTML contains `Up to 120000.0 INR`.
- Code commits: `9b44f85` (qualifiers), `a08cd87` (history cutoff).
- No Python or database-schema source changes; no deployment settings changed and nothing pushed or emailed.
- Public deployment access remains unresolved. Official-source comparison accuracy remains unvalidated.
- The optional execution helper skill was unavailable after searching installed skill locations; implementation ran inline as requested.
