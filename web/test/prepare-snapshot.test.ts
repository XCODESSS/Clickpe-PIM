// @vitest-environment node

import { createHash } from "node:crypto";
import { copyFileSync, mkdtempSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { tmpdir } from "node:os";

import Database from "better-sqlite3";
import { describe, expect, it } from "vitest";

import { createFixtureDb } from "./create-fixture-db";

function hash(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function prepare(dbPath: string, outPath: string, runId: string) {
  return spawnSync(process.execPath, ["scripts/prepare-snapshot.mjs"], {
    cwd: process.cwd(),
    env: {
      ...process.env,
      PIM_SNAPSHOT_PATH: dbPath,
      PIM_EXPECTED_RUN_ID: runId,
      PIM_PUBLIC_SNAPSHOT_OUT: outPath,
    },
    encoding: "utf8",
  });
}

describe("read-only public projection", () => {
  it("limits history and run counts to the selected completion time across UTC offsets", () => {
    const root = mkdtempSync(join(tmpdir(), "clickpe-pim-history-"));
    const dbPath = join(root, "fixture.sqlite");
    const outPath = join(root, "snapshot.json");
    createFixtureDb(dbPath);
    const db = new Database(dbPath);
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
    db.prepare("INSERT INTO scrape_runs VALUES (?,?,?,?,?,?,?)").run(
      "later_run", "2026-09-24T07:00:00Z", "2026-09-24T08:00:00Z", "complete", 1, 0,
      JSON.stringify({ cohort_ids: [], source_parse_status: {} }),
    );
    db.exec("INSERT INTO product_snapshots SELECT 'later_run', product_id, record_json FROM product_snapshots WHERE run_id='ui_fixture_run'");
    db.close();
    const before = hash(dbPath);

    const historicalResult = prepare(dbPath, outPath, "ui_fixture_run");
    expect(historicalResult.stderr).toBe("");
    expect(historicalResult.status).toBe(0);
    const historical = JSON.parse(readFileSync(outPath, "utf8"));
    expect(historical.changes.map((change: { changeId: string }) => change.changeId)).toEqual([
      "change_difference", "offset_before", "earlier",
    ]);
    expect(historical.overview.recentChanges).toBe(3);
    expect(historical.overview.finalizedRuns).toBe(1);

    const laterResult = prepare(dbPath, outPath, "later_run");
    expect(laterResult.stderr).toBe("");
    expect(laterResult.status).toBe(0);
    const later = JSON.parse(readFileSync(outPath, "utf8"));
    expect(later.changes.map((change: { changeId: string }) => change.changeId)).toEqual([
      "later", "offset_after", "change_difference", "offset_before", "earlier",
    ]);
    expect(later.overview.recentChanges).toBe(5);
    expect(later.overview.finalizedRuns).toBe(2);
    expect(hash(dbPath)).toBe(before);
  });

  it("selects one finalized run without changing the database or leaking private fields", () => {
    const root = mkdtempSync(join(tmpdir(), "clickpe-pim-ui-"));
    const dbPath = join(root, "fixture.sqlite");
    const outPath = join(root, "snapshot.json");
    createFixtureDb(dbPath);
    const before = hash(dbPath);
    const result = prepare(dbPath, outPath, "ui_fixture_run");
    expect(result.stderr).toBe("");
    expect(result.status).toBe(0);
    expect(hash(dbPath)).toBe(before);
    const raw = readFileSync(outPath, "utf8");
    expect(raw).not.toContain("Private Reviewer Token");
    expect(raw).not.toContain("C:\\private\\capture.html");
    const snapshot = JSON.parse(raw);
    expect(snapshot.run.runId).toBe("ui_fixture_run");
    expect(snapshot.products).toHaveLength(2);
    expect(snapshot.reviews[0].priority).toBe(88);
    expect(snapshot.reviews[0].left.rawText).toContain("5 lakh");
    expect(snapshot.reviews[0].right.rawText).toContain("3 lakh");
  });

  it.each([
    ["missing_run", "expected finalized run"],
    ["unfinished_run", "expected finalized run"],
    ["failed_run", "expected finalized run"],
    ["synthetic_run", "synthetic run"],
  ])("rejects invalid run selection %s", (runId, expected) => {
    const root = mkdtempSync(join(tmpdir(), "clickpe-pim-ui-"));
    const dbPath = join(root, "fixture.sqlite");
    createFixtureDb(dbPath);
    const result = prepare(dbPath, `${dbPath}.json`, runId);
    expect(result.status).not.toBe(0);
    expect(result.stderr.toLowerCase()).toContain(expected);
  });

  it("rejects an unsupported schema version", () => {
    const root = mkdtempSync(join(tmpdir(), "clickpe-pim-ui-"));
    const source = join(root, "fixture.sqlite");
    const copy = `${source}.copy`;
    createFixtureDb(source);
    copyFileSync(source, copy);
    const db = new Database(copy);
    db.pragma("user_version = 2");
    db.close();
    const result = prepare(copy, `${copy}.json`, "ui_fixture_run");
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("Unsupported SQLite schema version");
  });
});
