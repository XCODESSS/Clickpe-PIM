# Operations runbook

## Routine sequence

1. Activate the isolated Python 3.12 environment.
2. Run `pytest -q` and Ruff before collection.
3. Review source terms, robots status, and `config/source_mapping.yaml` allowlists.
4. Run live mode once. Exit code 0 is complete, 2 is partial, and 1 is fatal/invalid.
5. Inspect the run manifest, source parse states, failed-source banner, and evidence hashes.
6. Open the dashboard locally and complete human review events.
7. Create a consistent backup before another monitoring run.

## Blocked source

Do not change identity, bypass CAPTCHA, submit forms, or retry aggressively. Preserve the blocked capture classification, leave last-good observations visibly stale, and retry in a later run under the same reviewed policy. A 403, 429, 5xx, CAPTCHA, timeout, or parser failure cannot remove a field or product.

## Parser or mapping drift

A missing expected heading is `unsupported`, not absence. Freeze the new bytes, add a regression fixture, update the recipe/version, and replay the previous bytes under the new version before interpreting a semantic change. Mapping/version changes without replay are method changes, not product changes.

## Recovery

Use `scripts/backup.py` while the WAL-mode database is live; it invokes SQLite's consistent backup API. Restore only into a new/empty directory. Restore validates archive paths, schema version, inventory, and every SHA-256 entry before returning a database path. It never overwrites the active state.

If a snapshot directory was renamed but the database run was not finalized, verify `manifest.json` and all artifact hashes before any manual recovery. Queries expose finalized runs only. Do not delete `.pending` state until its inputs and hashes have been investigated.

## Monitoring workflow

The repository workflow is manual (`workflow_dispatch`) until a reviewed release passes. A missing persistent-state artifact must fail unless the operator explicitly initializes a new baseline. Scheduling, remote publication, and outreach are separate user-authorized actions.

The lock was generated with uv 0.12.3. CI pins `actions/checkout` v7 at `3d3c42e5aac5ba805825da76410c181273ba90b1`, `actions/setup-python` v7 at `5fda3b95a4ea91299a34e894583c3862153e4b97`, `astral-sh/setup-uv` v10.1.0 at `bec219d24cd3e171d82865faccec33120bb574f4`, `actions/upload-artifact` v7 at `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`, and `actions/download-artifact` v8 at `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c`. These tag resolutions were checked on 2026-09-19.
