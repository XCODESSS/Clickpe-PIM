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
$env:PIM_UI_DEMO = "0"
$env:PIM_EXPECTED_RUN_ID = Read-Host 'Exact finalized non-synthetic run ID in this database'
npm run build
npm run audit:out
```

The raw database, review events, reviewer identities, notes, local evidence paths, and unselected run records must never appear in `out/` or `.vercel/output/`. Vercel linking, preview deployment, and production deployment each require explicit approval immediately before the action.

## Deployment output audit

Run `npm run audit:out` from `web` after every static build. The audit rejects database and environment filenames plus private reviewer fields, local Windows paths, snapshot environment names, and the fixture-only secret sentinel. It scans generated UTF-8 text without printing a matched secret value.

## Manual real-data preview

The canonical target is the existing `clickpe-pim-xotw` project, with root directory `web`, Next.js, and Node 22.x. Root and `web` Vercel configuration disable automatic Git deployments: a source checkout alone does not contain the monitor database. The other existing projects are retained; their remote configuration still needs verification.

Run all pinned Vercel CLI commands (`vercel@59.23.2 pull`, `build`, and `deploy --prebuilt`) from the **repository root**, and npm commands from **web**. With the configured project root, the CLI writes the deployment artifact to root `.vercel/output`. Audit that exact directory from the repository root:

```powershell
node web/scripts/assert-deploy-output.mjs .vercel/output
```

The existing `npm run audit:vercel` script checks `web/.vercel/output` relative to `web`; it is not the audit command for this workflow's root output.

The `Deploy ClickPe preview` workflow accepts three manual inputs:

| Input | Meaning |
|---|---|
| `monitor_run_id` | Numeric Actions ID of a successful monitor workflow with an available state artifact |
| `expected_run_id` | Exact finalized non-synthetic SQLite `scrape_runs.run_id` in that artifact |
| `publish_preview` | Defaults to `false`; enable only for an authorized preview publication |

Validation restores the checksum-verified artifact, checks the exact run and project settings, builds once through Vercel, verifies the projected run, and audits both static and deployment output. A failed check prevents publication. Even validation-only execution needs the Vercel credentials and project settings; it is not the secret-free frontend CI job.

See [the preview runbook](../docs/runbooks/vercel-preview.md) for external setup and verification. Pushing the implementation, changing project settings, and first preview publication are separate authorization milestones. Production publication and promotion are outside this procedure.
