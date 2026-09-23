# Vercel Preview Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make PR checks pass and provide an explicitly requested, audited real-data preview through one Vercel project.

**Architecture:** GitHub Actions restores a selected monitor artifact, projects one explicit finalized run into the existing public snapshot, and builds the static frontend. Vercel receives only audited prebuilt output. Automatic Vercel Git builds are disabled because a source checkout does not contain the monitor database.

**Tech Stack:** Python 3.12, SQLite, GitHub Actions, Node 22.19.0 in CI, Next.js 16.3.5, existing npm lockfile, Vercel CLI 59.23.2.

**Spec:** `docs/specs/2026-09-20-clickpe-pim-vercel-ui.md`; the user's 2026-09-22 request to plan repairs for PR #1. This repair extends the original file allowlist to deployment configuration and Git checkout attributes, without changing backend code or fixture contents.

## Global Constraints

- This document is planning only. Do not execute deployment, project changes, commits, pushes, or implementation while preparing it.
- Preserve `src/clickpe_pim/**`, `app/**`, `tests/**`, `config/**`, `config.yaml`, `pyproject.toml`, `requirements.txt`, `uv.lock`, and existing backend scripts byte-for-byte.
- Preserve collection, extraction, normalization, mappings, comparison, scoring, evaluation, reporting, and SQLite schema behavior.
- Keep Streamlit as the existing local review-writing interface.
- Keep static Next.js export, read-only/query-only SQLite access, and explicit finalized non-synthetic run selection for real previews.
- Never introduce a Python Vercel entrypoint, public database API, server action, review mutation, or TypeScript financial logic.
- Never upload databases, review events, reviewer identities, notes, local paths, environment files, or unselected private records.
- Retain existing UI design, copy, accessibility, responsive behavior, and persistent synthetic-data labeling. This repair does not redesign any route.
- Keep `engines.node` as `>=22.19 <23`, locked dependency versions, and existing immutable GitHub Action pins. Align the Vercel project to Node 22.x.
- Preview publication remains manual and defaults off. No production publication, promotion, live collection, project deletion, or new recurring schedule.
- Project changes, pushing changes that affect external CI, and first preview publication are separate execution milestones; obtain authorization for the concrete scope when executing, unless already explicitly granted.
- Do not weaken hash validation to compensate for checkout conversion. Do not replace expected hashes with CRLF hashes.
- The execution helper skills named in the template header were not available in the planning session's skill catalog. Check availability at execution time; do not claim to have used them or install them automatically. Inline execution can follow these steps if the user chooses that approach.

---

## Evidence and diagnosis

Inspected branch: `automation/vercel-preview-local`, commit `840117584df2d6573852ec815fe3e8170a9c7edf`.

- [PR #1](https://github.com/XCODESSS/Clickpe-PIM/pull/1) contains three failed Vercel checks on that commit.
- [clickpe-pim deployment](https://vercel.com/shreyarththakor17-gmailcoms-projects/clickpe-pim/Eo8SYi5s1G57M2ZdanhXBTaPAZvv) and [clickpe-pim-2bgo deployment](https://vercel.com/shreyarththakor17-gmailcoms-projects/clickpe-pim-2bgo/ErWCqC5W85T3xukscixmeqVz2cFk): `No python entrypoint found`. Both are rooted at the repository root in the PR metadata.
- [clickpe-pim-xotw deployment](https://vercel.com/shreyarththakor17-gmailcoms-projects/clickpe-pim-xotw/4L6rG8F31mAZ4DDJHzgejPGCpM4q): the Next.js prebuild stops with `PIM_EXPECTED_RUN_ID is required for a non-demo build.` Its project root is `web`.
- [Offline CI run](https://github.com/XCODESSS/Clickpe-PIM/actions/runs/35731966699): Ubuntu passed; Windows job `106759523365` had 59 passing and four failing tests. All four failed at `capture hash mismatch: clickpe_catalogue`.
- Local fixture bytes match all three manifest hashes. Converting LF to CRLF changes all three hashes. Git reports LF blobs with no fixture attributes. Checkout conversion is the leading Windows diagnosis; Task 1 proves it with Git checkout, not just a byte substitution.
- Local checks earlier in this task: 38 frontend tests pass, typecheck passes, source-only lint passes, and existing `out/` passes its audit. Full lint scans `.vercel/output` and fails. These are not evidence of a successful fresh real-data deployment.
- `.github/workflows/deploy-preview.yml` is manual, ends after its Vercel audit, and never deploys. Vercel's Git integration is a separate build path and does not run this workflow's restore steps.
- Vercel connector team enumeration returned empty and its project/log methods returned integration errors. Logged-in Chrome provided the deployment logs. Prefer the connector if repaired; otherwise use the authenticated dashboard for planned project configuration.

## Target configuration and boundaries

Use existing `clickpe-pim-xotw` as the canonical frontend project. This choice preserves the project already configured for `web`; it does not create or rename anything.

| Setting | Intended value |
|---|---|
| Team ID | `team_p0zbRpUBhRhAYkbD4sISIQVa` |
| Canonical project ID | `prj_pDWOySkP10wr6iEyVY69CkNVeLok` |
| Root directory | `web` |
| Framework | Next.js |
| Node | 22.x |
| Build command | `npm run build` |
| Install command | `npm ci` |
| Output directory | Framework default for the existing static export |
| Git auto-deployment | Disabled |
| Preview protection | Keep enabled; verify before first publish |

Retain `clickpe-pim` and `clickpe-pim-2bgo` without deleting deployments or domains. Disable their automatic Git deployments too. Do not turn them into Python services.

The Actions artifact run ID is a numeric GitHub Actions ID. `expected_run_id` is a string stored in SQLite `scrape_runs`. They are different inputs and must not be substituted for each other. Select both from a real successful monitor artifact during execution; do not hardcode the old local baseline as though it must exist in that artifact.

## File responsibility map

| File | Action and responsibility |
|---|---|
| `.gitattributes` | Create; preserve captured fixture bytes across OS checkouts |
| `vercel.json` | Create; disable Git deployments for projects rooted at repository root |
| `web/vercel.json` | Create; disable Git deployments for the frontend-root project |
| `web/eslint.config.mjs` | Modify; ignore generated `.vercel` output |
| `.github/workflows/ci.yml` | Modify; add offline frontend validation alongside the unchanged Python matrix |
| `.github/workflows/deploy-preview.yml` | Modify; explicit run selection, artifact provenance, consistent CLI working directory, validation-only default and optional prebuilt preview publish |
| `web/README.md` | Modify; document canonical project, inputs, commands, output location and approval boundaries |
| `docs/runbooks/vercel-preview.md` | Create; record external setup, failure handling and first-preview verification |

Existing adapter, audit script, Python scripts, and tests are reused unchanged. No dependencies are added. No UI components change.

## Task 1: Preserve replay capture bytes on Windows

**Files:** Create `.gitattributes`. Test existing `tests/test_backup.py`, `tests/test_pipeline.py`, `tests/test_queries.py`, `tests/test_report.py` without modifying them.

**Interfaces:** Consumes `tests/fixtures/catalogue/replay-manifest.json` capture paths and hashes. Produces identical fixture bytes on Windows and Ubuntu checkouts.

- [ ] Record clean status and HEAD before implementation. Retain unrelated changes. Work from the existing PR branch or an isolated checkout of its head, not an unrelated default branch.
- [ ] Reproduce checkout conversion using these PowerShell commands from `D:/Clickpe-PIM`. Never use an existing working folder or reset the user's checkout. Keep the temporary clone until validation is recorded.

```powershell
$probeRoot = & ./.venv/Scripts/python.exe -c "import tempfile; print(tempfile.mkdtemp(prefix='clickpe-checkout-'))"
$probeCheckout = Join-Path $probeRoot 'repo'
git -c core.autocrlf=true clone --no-local --no-checkout D:/Clickpe-PIM $probeCheckout
git -C $probeCheckout -c core.autocrlf=true checkout HEAD
```
- [ ] In that clone, use the following read-only hash check with the existing Python 3.12 interpreter. Before the fix, expect at least the catalogue payload assertion to fail under CRLF checkout.

```python
import hashlib
import json
from pathlib import Path

manifest = Path('tests/fixtures/catalogue/replay-manifest.json')
for capture in json.loads(manifest.read_text(encoding='utf-8'))['captures']:
    payload = (manifest.parent / capture['fixture']).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == capture['sha256'], capture['source_id']
```

- [ ] Add only this rule, preserving exact bytes rather than normalizing evidence:

```gitattributes
# Replay captures are byte-hashed evidence; never convert checkout line endings.
tests/fixtures/** -text
```

- [ ] Check `git check-attr text -- tests/fixtures/catalogue/feed.json tests/fixtures/provider/match.html tests/fixtures/provider/difference.html`; expect `text: unset`. Confirm no fixture changes with `git diff -- tests/fixtures`.
- [ ] Commit only `.gitattributes`: `git add .gitattributes` then `git commit -m "fix: preserve replay fixture bytes across checkouts"`.
- [ ] Repeat the temporary-clone checkout from this commit with `core.autocrlf=true`; the same hash check must pass. Run the existing full Python suite from that fresh checkout using its own frozen environment: `uv sync --frozen --extra dev`, then `uv run --frozen --extra dev pytest -q`. Expect all 63 currently collected tests to pass. If hash checks still fail, stop and inspect bytes instead of changing expected hashes.

## Task 2: Make the intended build path explicit and add frontend CI

**Files:** Create `vercel.json`, `web/vercel.json`; modify `web/eslint.config.mjs`, `.github/workflows/ci.yml`.

**Interfaces:** Consumes existing npm scripts and synthetic fixture; produces a secret-free frontend PR check and Git auto-deployment suppression for both project roots.

- [ ] Add the following exact content to both Vercel configuration files:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "git": { "deploymentEnabled": false }
}
```

- [ ] Add `".vercel/**",` to `globalIgnores` in `web/eslint.config.mjs`. Existing full lint fails when generated Vercel bundles are present; `npm run lint` from `web` must now pass without command-line exclusions. No bespoke test is needed for this ignore entry.
- [ ] Append the following independent job under `jobs` in `.github/workflows/ci.yml`; leave the Python matrix unchanged:

```yaml
  web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: web
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020
        with:
          node-version: "22.19.0"
          cache: npm
          cache-dependency-path: web/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
        env:
          PIM_UI_DEMO: "1"
      - run: npm run typecheck
      - run: npm run audit:out
      - run: npx --no-install playwright install --with-deps chromium
      - run: npm run test:e2e
```

- [ ] Validate locally from `web` using the existing installed dependencies: lint, tests, synthetic build (`$env:PIM_UI_DEMO='1'` in PowerShell), typecheck, output audit, then E2E. Ensure port 3000 is free; do not terminate unrelated processes. Restore the prior process environment after the synthetic build. Browser installation is required only if the matching Chromium is absent.
- [ ] Parse both JSON files and the YAML using existing Python/PyYAML; remember PyYAML's YAML 1.1 loader can treat `on` as a Boolean key, so use `yaml.BaseLoader` for a syntax-only parse. Inspect the actual GitHub Actions run later for authoritative workflow behavior.
- [ ] Commit only the four configuration files with `fix: route previews through audited builds`.

## Task 3: Repair the real-data workflow and add an opt-in publish step

**Files:** Modify `.github/workflows/deploy-preview.yml`.

**Interfaces:** Inputs `monitor_run_id` (successful Actions run), `expected_run_id` (SQLite finalized run), `publish_preview` (Boolean false by default). Existing restore writes `.restored/database/monitor.sqlite`; existing adapter consumes `PIM_SNAPSHOT_PATH`, `PIM_EXPECTED_RUN_ID`, `PIM_UI_DEMO=0`. Produces audited static build and, only when requested, one preview URL.

- [ ] Keep the existing `monitor_run_id` input. Add these dispatch inputs:

```yaml
      expected_run_id:
        description: Exact finalized non-synthetic scrape_runs.run_id in the artifact
        required: true
        type: string
      publish_preview:
        description: Publish the audited output to the canonical preview project
        required: true
        type: boolean
        default: false
```

- [ ] Before artifact download, add a bash provenance check using the runner's GitHub CLI and environment variables; never interpolate user-controlled inputs directly into shell code:

```yaml
      - name: Verify monitor artifact provenance
        env:
          GH_TOKEN: ${{ github.token }}
          MONITOR_RUN_ID: ${{ inputs.monitor_run_id }}
        shell: bash
        run: |
          set -euo pipefail
          [[ "$MONITOR_RUN_ID" =~ ^[0-9]+$ ]]
          gh api "repos/${GITHUB_REPOSITORY}/actions/runs/${MONITOR_RUN_ID}" > monitor-run.json
          python - <<'PY'
          import json, os
          with open('monitor-run.json', encoding='utf-8') as stream:
              run = json.load(stream)
          if (run['conclusion'] != 'success'
                  or run['status'] != 'completed'
                  or run['path'] != '.github/workflows/monitor.yml'
                  or run['head_repository']['full_name'] != os.environ['GITHUB_REPOSITORY']):
              raise SystemExit('Expected a successful monitor workflow run from this repository.')
          PY
```

- [ ] Preserve the checksum-validating restore step and existing download action. Missing/expired artifact is a hard failure with no publish; do not start live collection or fall back to a fixture.
- [ ] Replace automatic latest-run selection with the following body, passing `EXPECTED_RUN_ID: ${{ inputs.expected_run_id }}` through the step's `env`:

```python
import os
import sqlite3
from pathlib import Path

path = Path('data/db/monitor.sqlite').resolve()
run_id = os.environ['EXPECTED_RUN_ID']
if not run_id or '\n' in run_id or '\r' in run_id:
    raise SystemExit('Expected run ID must be nonempty and single-line.')
with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
    db.execute('PRAGMA query_only=ON')
    row = db.execute('''SELECT run_id FROM scrape_runs
        WHERE run_id=? AND finished_at IS NOT NULL
        AND status IN ('complete','partial') AND synthetic=0''', (run_id,)).fetchone()
if row is None:
    raise SystemExit('Selected finalized non-synthetic run was not found.')
with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as stream:
    stream.write(f'PIM_EXPECTED_RUN_ID={run_id}\n')
    stream.write(f'PIM_SNAPSHOT_PATH={path}\nPIM_UI_DEMO=0\n')
```

- [ ] Add workflow concurrency `group: clickpe-preview` and `cancel-in-progress: false` to serialize builds/publishes. Keep permissions at `contents: read`, `actions: read`.
- [ ] Add job-level Vercel credentials using the existing names: token from `secrets.VERCEL_TOKEN`, org/project IDs from `vars.VERCEL_ORG_ID` and `vars.VERCEL_PROJECT_ID`. Before pull, use bash `test -n "$VERCEL_TOKEN"` and exact ID equality checks against the target table. Do not print token values or enable shell tracing.
- [ ] Run all Vercel CLI commands at the repository root, with project `rootDirectory=web`. Keep npm commands in `web`. This avoids applying `web` twice and puts CLI metadata/output in a single known root `.vercel` directory. Pull with `npx --yes vercel@59.23.2 pull --yes --environment=preview --token="$VERCEL_TOKEN"`.
- [ ] Immediately inspect root `.vercel/project.json` without printing credentials: require `projectId`/`orgId` equal the configured IDs, `settings.rootDirectory == 'web'`, `settings.framework == 'nextjs'`, and `settings.nodeVersion == '22.x'`. Fail with a setting-name-only message on mismatch. Existing `web/.vercel/project.json` is local ignored state and must not be used in fresh CI.
- [ ] Keep `npm ci`, add `npm run lint` and `npm test` in `web`, and remove the redundant standalone prepare/build pair. Run the one authoritative build with `npx --yes vercel@59.23.2 build --token="$VERCEL_TOKEN"` from repository root. npm's existing prebuild must prepare the snapshot. Do not use `--prod`.
- [ ] After build, parse `web/.cache/public-snapshot.json`; require `snapshot.run.runId` equals the requested ID and `snapshot.run.synthetic === false`. This catches environment overrides from pulled settings. Retain adapter failure behavior for missing or invalid data.
- [ ] Audit `web/out` with `npm run audit:out` in `web`. Audit the actual deployment directory from repository root with `node web/scripts/assert-deploy-output.mjs .vercel/output`. Require `.vercel/output/config.json` and `.vercel/output/static/index.html` to exist. If pinned CLI behavior places output elsewhere, fail and resolve the working-directory mismatch; never audit one directory and upload another.
- [ ] Preserve the explicit forbidden-database-file check, pointed at both `web/out` and root `.vercel/output`. Do not weaken the existing audit or its tests to make a build pass.
- [ ] Append this step after every audit. It is the only publish action:

```yaml
      - name: Publish audited preview
        if: ${{ inputs.publish_preview }}
        shell: bash
        run: |
          set -euo pipefail
          url=$(npx --yes vercel@59.23.2 deploy --prebuilt --yes --token="$VERCEL_TOKEN")
          [[ "$url" == https://*.vercel.app ]]
          printf 'Preview: %s\nRun: %s\nCommit: %s\n' "$url" "$PIM_EXPECTED_RUN_ID" "$GITHUB_SHA" >> "$GITHUB_STEP_SUMMARY"
```

- [ ] Add a separate always-available summary step before publication recording source commit, monitor Actions run ID, selected SQLite run ID, and validation result, with no database content or environment dump. A validation-only run must clearly say publication was not requested.
- [ ] Validate existing adapter tests (`npm test -- test/prepare-snapshot.test.ts`) and audit tests (`npm test -- test/assert-deploy-output.test.ts`) from `web`. Syntax-check workflow YAML. Review negative paths: wrong workflow artifact, failed monitor run, expired artifact, wrong/missing/unfinished/synthetic SQLite run, wrong project IDs, leaked database, audit failure; each must prevent publication. Exercise wrong-run selection in a validation-only workflow dispatch after external execution is authorized.
- [ ] Commit only `.github/workflows/deploy-preview.yml` with `fix: validate selected monitor run before preview publication`.

## Task 4: Align external project settings and prove the first preview

**Files:** Modify `web/README.md`; create `docs/runbooks/vercel-preview.md`. External configuration: the three existing Vercel projects and repository Actions variables/secrets.

**Interfaces:** Consumes committed Tasks 1–3, successful monitor artifact, exact SQLite run ID, existing scoped Vercel token. Produces documented validation evidence and an authorized protected preview.

- [ ] Before changing external state, present the concrete project table and diff. Confirm authorization for these settings changes and PR update if not already granted. Do not delete projects or move domains. Inventory domain assignments before disabling duplicate automation.
- [ ] In Vercel, retain `clickpe-pim-xotw`, align its settings to the target table, and retain preview protection. Verify the two duplicates no longer auto-build Git commits. The root and `web` configuration files suppress future source-based builds once present on the relevant branch; if needed for branches without those files, disconnect the duplicates' Git repository only after explicit authorization. Preserve existing deployments.
- [ ] In GitHub Actions configuration, verify the two variables match the canonical IDs. Verify the existing `VERCEL_TOKEN` is present and scoped for the project without exposing its value. If absent, the user supplies it through the secret UI; do not request a token in chat.
- [ ] Update PR #1 with the authorized commits and a description explaining checkout byte preservation, disabled source builds, and manual real-data prebuilt previews. Do not merge automatically. Confirm the new commit's Windows, Ubuntu and frontend CI jobs pass.
- [ ] Check branch protection for required legacy Vercel status contexts. If they prevent merging after intentionally disabling duplicate builds, propose replacing those contexts with the passing offline/frontend checks; make only the authorized rules change. Do not misreport historical failed deployment checks as repaired deployments.
- [ ] Discover a successful `ClickPe monitor` Actions run with an unexpired `clickpe-monitor-state` artifact. Restore it locally with the existing restore script if necessary to enumerate finalized nonsynthetic run IDs read-only. Present selected IDs and run health. Stop if none exists; do not invent one or trigger live collection as a workaround.
- [ ] Ensure the workflow exists on the repository's default branch before expecting GitHub's manual dispatch UI to expose it. If it is not registered yet, obtain approval for the PR merge after checks pass; do not silently merge just to enable dispatch.
- [ ] Dispatch the workflow against the approved code with `publish_preview=false`, the selected monitor Actions ID, and exact SQLite run ID. Require restore, selection, build and both audits to pass. Check logs for correct root, Node, project ID and run ID. No deployment should appear from this validation-only action.
- [ ] Show the successful validation result and intended project/run to the user, then obtain preview-publication approval if not already granted. Dispatch with identical IDs and code revision and `publish_preview=true`; the job rebuilds and reaudits before upload. The selected run and code must not silently advance.
- [ ] Verify Vercel reports READY for this preview. Open the protected preview with the user's authenticated session; verify overview, reviews, products, changes, providers, a product detail and any available review detail. The displayed selected run ID must match. Empty review data is acceptable; fabricated evidence is not.
- [ ] At 390 px and desktop width verify navigation, evidence text, partial-run warning if applicable, and no horizontal page overflow. Check deployment resources contain static assets only and no database or Python/serverless backend. Record URL, commit, both run IDs, date and audit/check outcomes in the runbook. Do not create a public protection-bypass URL.
- [ ] Update `web/README.md` to document the root-versus-web CLI convention, `.vercel/output` audit invocation, manual workflow inputs, canonical project, validation-only default and separate production boundary. Commit documentation with `docs: document validated preview deployment procedure`.

## Completion and rollback

Completion requires passing Windows/Ubuntu Python CI, frontend CI, a successful real-data validation-only run, and an explicitly authorized READY protected preview for the selected snapshot. If the user authorizes only implementation, stop with locally verified changes and label remote validation/publication outstanding.

If an audit or build fails, publish nothing and retain logs. If preview rendering fails, leave production untouched, record the failed preview, and repair the build before another authorized attempt. Restore project settings from the recorded pre-change values if configuration rollback is needed; do not delete deployments. Revert scoped code commits if required rather than resetting the working tree. Leave fixture hash verification intact in every rollback path.

## References

- [Vercel Git configuration](https://vercel.com/docs/project-configuration/git-configuration): `git.deploymentEnabled` controls automatic Git deployments.
- [Vercel build CLI](https://vercel.com/docs/cli/build): pull settings first; build artifacts are written to `.vercel/output`; default build target is preview.
- [Vercel GitHub integration](https://vercel.com/docs/git/vercel-for-github): use prebuilt deployment for CI-built output.
- Existing design specification, `web/README.md`, `web/scripts/prepare-snapshot.mjs`, `web/scripts/assert-deploy-output.mjs`, and both current GitHub workflows were inspected for this plan.

## Planning self-review

Coverage: Tasks 2 and 4 address wrong project roots and duplicate builds; Task 3 addresses missing snapshot selection and absent publication; Task 1 addresses Windows hash failures; Task 2 addresses generated-output lint and frontend CI coverage. Every protected backend file remains outside the change list. Commands distinguish repository root from `web`, and GitHub artifact IDs from SQLite run IDs. External identifiers come from the inspected PR; artifact selection remains an execution-time inventory step because no successful artifact was selected during planning.
