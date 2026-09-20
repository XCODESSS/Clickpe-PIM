# ClickPe PIM web interface

This directory contains a read-only static interface for one explicitly selected finalized monitor run. It never exposes a database, an API, or a review mutation. Review writes remain in the local Streamlit workflow.

The implementation uses Node 22.19.x with TypeScript 6.0.3, ESLint 9.39.5, and jsdom 29.0.1. These three versions intentionally correct incompatible pins in the original UI plan: the Next 16.3.5 lint stack rejects TypeScript 7, its bundled plugins do not support ESLint 10, and jsdom 30.1 requires a newer Node 22 patch release.

## Local synthetic preview

`PIM_UI_DEMO=1` uses the synthetic fixture under `test/fixtures/`. Every route then displays “Synthetic interface preview.” Synthetic output is for interface development and protected previews only.

```powershell
$env:PIM_UI_DEMO = "1"
npm run build
npm run audit:out
npm run preview
```

## Real snapshot build

A real build requires both `PIM_SNAPSHOT_PATH` and `PIM_EXPECTED_RUN_ID`. The selected SQLite database is opened read-only with query-only mode, the run must be finalized and non-synthetic, and only the public view model is written to `.cache/`.

```powershell
$env:PIM_SNAPSHOT_PATH = (Resolve-Path '..\data\db\monitor.sqlite').Path
$env:PIM_EXPECTED_RUN_ID = 'live_20260920_release'
npm run build
npm run audit:out
```

The raw database, review events, reviewer identities, notes, local evidence paths, and unselected run records must never appear in `out/` or `.vercel/output/`. Vercel linking, preview deployment, and production deployment each require explicit approval immediately before the action.

## Deployment output audit

Run `npm run audit:out` after every static build. The audit rejects database and environment filenames plus private reviewer fields, local Windows paths, snapshot environment names, and the fixture-only secret sentinel. It scans generated UTF-8 text without printing a matched secret value. Run `npm run audit:vercel` after `vercel build` and before any approved deployment.

The first Vercel link and synthetic preview require approval because they create external project and deployment state. A non-synthetic preview or production deployment requires a separate approval and an explicitly selected finalized real run.
