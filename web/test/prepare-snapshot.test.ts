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
