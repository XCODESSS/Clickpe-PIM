import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

import { describe, expect, it } from "vitest";

function audit(files: Record<string, string | Buffer>) {
  const root = mkdtempSync(join(tmpdir(), "clickpe-output-audit-"));
  for (const [name, value] of Object.entries(files)) {
    const path = join(root, name);
    mkdirSync(join(path, ".."), { recursive: true });
    writeFileSync(path, value);
  }
  return spawnSync(process.execPath, ["scripts/assert-deploy-output.mjs", root], {
    cwd: process.cwd(),
    encoding: "utf8",
  });
}

describe("deployment output audit", () => {
  it("reports every unsafe filename and private text rule without echoing secret values", () => {
    const fixtureSecret = "fixture-secret-do-not-deploy";
    const result = audit({
      "raw/monitor.sqlite": Buffer.from([0, 1, 2, 3]),
      "raw/monitor.sqlite-wal": Buffer.from([0, 1]),
      "raw/cache.db": "database bytes",
      ".env.production": "PUBLIC=no",
      "reviewer.html": "Private Reviewer Token reviewed_by review_events",
      "path.js": String.raw`const localEvidence = "C:\private\capture.html";`,
      "environment.txt": "PIM_SNAPSHOT_PATH",
      "fixture.html": fixtureSecret,
    });
    expect(result.status).toBe(1);
    const report = `${result.stdout}${result.stderr}`;
    for (const rule of [
      "database-file", "environment-file", "private-reviewer-token", "reviewed-by-field",
      "review-events-table", "windows-drive-path", "snapshot-path-environment", "fixture-secret",
    ]) expect(report).toContain(`[${rule}]`);
    for (const path of [
      "raw/monitor.sqlite", "raw/monitor.sqlite-wal", "raw/cache.db", ".env.production",
      "reviewer.html", "path.js", "environment.txt", "fixture.html",
    ]) expect(report).toContain(path);
    expect(report).not.toContain(fixtureSecret);
    expect(report).not.toContain("Private Reviewer Token");
    expect(report).not.toContain(String.raw`C:\private\capture.html`);
  });

  it("allows public evidence, hashes, URLs, locators, and neutral review language", () => {
    const result = audit({
      "index.html": [
        "<h1>Public evidence review</h1>",
        "<p>SHA-256 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</p>",
        "<a href=\"https://example.org/source\">Source URL</a>",
        "<code>/response/0/content/headline</code>",
      ].join(""),
      "_next/static/media/font.woff2": Buffer.from("Private Reviewer Token"),
    });
    expect(result.status).toBe(0);
    expect(result.stdout).toContain("Deploy output audit passed");
  });

  it("fails closed when the requested output directory is missing", () => {
    const result = spawnSync(process.execPath, ["scripts/assert-deploy-output.mjs", join(tmpdir(), "missing-clickpe-output")], {
      cwd: process.cwd(),
      encoding: "utf8",
    });
    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("Deploy output directory does not exist");
  });
});
