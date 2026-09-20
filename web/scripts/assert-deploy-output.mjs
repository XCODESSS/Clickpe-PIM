import { readdirSync, readFileSync, statSync } from "node:fs";
import { basename, relative, resolve, sep } from "node:path";

const imageAndFontExtensions = new Set([
  ".avif", ".gif", ".ico", ".jpeg", ".jpg", ".png", ".svgz", ".webp", ".woff", ".woff2",
]);

const textRules = [
  ["private-reviewer-token", /Private Reviewer Token/i],
  ["reviewed-by-field", /\breviewed_by\b/i],
  ["review-events-table", /\breview_events\b/i],
  ["windows-drive-path", /(?:^|[\s"'`(])(?:[A-Za-z]:\\)[^\s"'`)]*/m],
  ["snapshot-path-environment", /\bPIM_SNAPSHOT_PATH\b/],
  ["fixture-secret", /fixture-secret-do-not-deploy/i],
];

function extension(path) {
  const name = basename(path).toLocaleLowerCase();
  if (name.endsWith(".sqlite-wal")) return ".sqlite-wal";
  const dot = name.lastIndexOf(".");
  return dot >= 0 ? name.slice(dot) : "";
}

function filenameRule(path) {
  const name = basename(path).toLocaleLowerCase();
  if (name === ".env" || name.startsWith(".env.")) return "environment-file";
  if ([".sqlite", ".sqlite-wal", ".sqlite-shm", ".db"].includes(extension(path))) return "database-file";
  return null;
}

function filesUnder(root) {
  const found = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = resolve(root, entry.name);
    if (entry.isDirectory()) found.push(...filesUnder(path));
    else if (entry.isFile()) found.push(path);
  }
  return found;
}

function decodeText(path) {
  if (imageAndFontExtensions.has(extension(path))) return null;
  const bytes = readFileSync(path);
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    return null;
  }
}

export function auditDeployOutput(directory) {
  const root = resolve(directory);
  if (!statSync(root, { throwIfNoEntry: false })?.isDirectory()) {
    throw new Error(`Deploy output directory does not exist: ${directory}`);
  }
  const findings = [];
  for (const path of filesUnder(root)) {
    const displayPath = relative(root, path).split(sep).join("/");
    const fileRule = filenameRule(path);
    if (fileRule) findings.push({ rule: fileRule, path: displayPath });
    const text = decodeText(path);
    if (text === null) continue;
    for (const [rule, pattern] of textRules) {
      if (pattern.test(text)) findings.push({ rule, path: displayPath });
    }
  }
  return findings;
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(import.meta.filename)) {
  const directory = process.argv[2];
  if (!directory) {
    console.error("Usage: node scripts/assert-deploy-output.mjs <directory>");
    process.exitCode = 2;
  } else {
    try {
      const findings = auditDeployOutput(directory);
      if (findings.length) {
        console.error("Deploy output audit failed:");
        for (const finding of findings) console.error(`[${finding.rule}] ${finding.path}`);
        process.exitCode = 1;
      } else {
        console.log(`Deploy output audit passed: ${directory}`);
      }
    } catch (error) {
      console.error(error instanceof Error ? error.message : "Deploy output audit failed.");
      process.exitCode = 2;
    }
  }
}
