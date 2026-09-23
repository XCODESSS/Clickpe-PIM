# Vercel preview procedure

This procedure implements the [preview recovery plan](../superpowers/plans/2026-09-22-vercel-preview-recovery.md). Local implementation does not establish that remote settings, Actions checks, or a deployment have succeeded.

## Target and external setup

After authorization for external settings changes, inventory the current settings and domain assignments for all three existing projects. Record their original values before changing them. Preserve deployments and domains.

| Setting | Required value |
|---|---|
| Canonical project | `clickpe-pim-xotw` |
| Team ID | `team_p0zbRpUBhRhAYkbD4sISIQVa` |
| Project ID | `prj_pDWOySkP10wr6iEyVY69CkNVeLok` |
| Root directory | `web` |
| Framework | Next.js (`nextjs`) |
| Node | `22.x` |
| Build command | `npm run build` |
| Install command | `npm ci` |
| Output directory | Framework default for static export |
| Preview protection | Enabled and verified before publishing |
| Git automatic deployments | Disabled |

The two other projects, `clickpe-pim` and `clickpe-pim-2bgo`, must also stop automatic Git builds. The repository's two `vercel.json` files disable Git builds for their respective roots on branches containing those files. Verify actual behavior; disconnect a duplicate's Git repository only with explicit authorization if branches without these files still trigger builds. Do not delete projects.

Verify Actions variables `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` match the table. Verify `VERCEL_TOKEN` exists as a suitably scoped Actions secret without exposing its value. If missing, enter it through GitHub's secret UI, never in chat or a tracked file.

## Code and artifact prerequisites

1. Review the implementation diff and obtain authorization to push the PR update. Require Windows and Ubuntu Python CI and frontend CI to pass for that revision. Historical failed Vercel checks are not successful repaired deployments.
2. Inspect required branch checks. If obsolete Vercel contexts block merging, propose a rules update to the validated CI checks and obtain authorization before changing branch protection.
3. Confirm the manual workflow is registered on the default branch. Obtain separate merge authorization if required to make it available; do not merge automatically.
4. Select a successful run of `.github/workflows/monitor.yml` from this repository with an unexpired `clickpe-monitor-state` artifact. Restore with the existing checksum-validating `scripts/restore.py` and enumerate finalized non-synthetic SQLite runs read-only. Record the numeric Actions run ID, exact SQLite run ID, and run health. These two IDs are different.
5. If there is no suitable artifact, stop. Do not trigger live collection or substitute synthetic evidence.

## Validate, then publish

All Vercel CLI commands run at the repository root with CLI `59.23.2`; npm commands run in `web`. Ignore old local `web/.vercel` metadata. Pull preview settings before building. The authoritative CLI output is root `.vercel/output`, and the static export is `web/out`.

Dispatch `Deploy ClickPe preview` on the approved revision with the selected `monitor_run_id`, `expected_run_id`, and `publish_preview=false`. This requires authorization for external workflow execution. Verify provenance, restore, exact read-only selection, project/root/Node checks, build, selected public snapshot, both output audits, and explicit database-file rejection all pass. No deployment should be created.

The audit commands are:

```powershell
# From web:
npm run audit:out
# From the repository root:
node web/scripts/assert-deploy-output.mjs .vercel/output
```

Missing or failed artifacts, another workflow/repository, missing/unfinished/synthetic/wrong SQLite runs, mismatched project settings, and either failed audit must prevent publication. After approval, exercise a wrong-run validation-only dispatch and confirm it stops at selection.

Present the successful validation and selected project/run before requesting first publication approval. Dispatch the same revision and both IDs with `publish_preview=true`. It rebuilds and audits before `deploy --prebuilt`; it must not advance the source revision or snapshot silently. Never add `--prod` or promote the deployment as part of this procedure.

## Verify the protected preview

Require Vercel status READY. Open it in the authorized signed-in session and verify overview, reviews, products, changes, providers, a product detail, and an available review detail. Empty review data is valid. Confirm the displayed run ID matches selection and partial-run warnings appear when applicable.

At desktop and 390 px widths, check navigation, readable evidence, and no horizontal page overflow. Inspect deployment resources for static assets only; no database or Python/serverless backend may be present. Keep preview protection enabled and do not create a public bypass URL.

Record the verified URL, source commit, Actions monitor run ID, SQLite run ID, validation/publish workflow IDs, date, run health, audit results, and browser results after execution. No verified preview URL or remote validation result has been recorded by this local implementation.

## Failure and rollback

On any build or audit failure, publish nothing and retain the logs. On rendering failure, record the failed preview and repair it before another authorized publication. Leave production untouched. Restore external settings from the recorded original values if rollback is needed, and revert scoped code commits rather than resetting the working tree. Preserve fixture hashes and existing deployments throughout.

## Local implementation evidence — 2026-09-22

Changes were validated locally on `automation/vercel-preview-local`, based on `840117584df2d6573852ec815fe3e8170a9c7edf`, without committing, pushing, changing remote settings, or publishing.

- A disposable Git checkout with `core.autocrlf=true` reproduced all three capture hash failures. Applying the fixture attributes to that checkout restored all three exact hashes; tracked fixture contents remained unchanged.
- All 63 Python tests passed from the corrected checkout using the existing Python 3.12.6 environment. A fresh frozen dependency setup was blocked by uv cache access, so independent dependency installation remains unverified.
- Node 22.19.0: lint, 38 unit tests, fresh synthetic build (11 static pages), typecheck, and static output audit passed.
- All 18 Chromium E2E tests passed, including accessibility and responsive checks. The local preview server needed explicit termination after tests finished for the runner to exit; final runner exit code was zero.
- Both Vercel JSON files and workflow YAML parsed successfully. Embedded workflow Python compiled, and 17 positive/negative provenance, SQLite run-selection, and built-snapshot guard cases passed offline. The Python CI job remained structurally unchanged.
- Independent workflow review found no actionable issues. Backend code, existing tests, fixture contents, dependency locks, and UI components were not changed.

Remote project configuration, fresh Windows/Ubuntu Actions results, real-data Vercel build/output placement, validation-only dispatch, and protected preview publication remain unverified and require the external execution milestones above.
