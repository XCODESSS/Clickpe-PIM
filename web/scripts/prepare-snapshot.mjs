import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

import Database from "better-sqlite3";

import { publicSnapshotSchema } from "../src/lib/snapshot/types.ts";

function json(value, label) {
  try {
    return JSON.parse(value);
  } catch {
    throw new Error(`Stored ${label} JSON is invalid.`);
  }
}

function nullableString(value) {
  return typeof value === "string" ? value : null;
}

function projectValue(value) {
  if (!value || typeof value !== "object") return null;
  return {
    kind: String(value.kind ?? "unknown"),
    lower: nullableString(value.lower),
    upper: nullableString(value.upper),
    text: nullableString(value.text),
    boolean: typeof value.boolean === "boolean" ? value.boolean : null,
    options: Array.isArray(value.options) ? value.options.map(String) : [],
    unit: nullableString(value.unit),
    period: String(value.period ?? "unknown"),
    basis: String(value.basis ?? "unknown"),
    qualifier: String(value.qualifier ?? "exact"),
    approximate: Boolean(value.approximate),
  };
}

function projectEvidence(row) {
  const observation = json(row.observation_json, "observation");
  const capture = json(row.capture_json, "capture");
  return {
    observationId: String(observation.observation_id),
    sourceId: String(observation.source_id),
    sourceType: String(row.source_type),
    sourceUrl: nullableString(row.url),
    retrievedAt: String(capture.retrieved_at),
    sha256: nullableString(capture.sha256),
    field: String(observation.field),
    state: String(observation.state),
    rawText: String(observation.raw_text ?? ""),
    locator: String(observation.locator ?? ""),
    context: String(observation.context ?? "unknown"),
    confidence: Number(observation.confidence),
    value: projectValue(observation.value),
  };
}

function projectMapping(mapping) {
  if (!mapping) return null;
  return {
    role: String(mapping.role ?? "unknown"),
    programme: nullableString(mapping.programme),
    segment: nullableString(mapping.segment),
    geography: nullableString(mapping.geography),
    scope: String(mapping.scope ?? "unknown"),
    reviewState: String(mapping.review_state ?? "candidate"),
    confidence: Number(mapping.confidence ?? 0),
    rationale: String(mapping.rationale ?? ""),
  };
}

function finalizeSnapshot(snapshot) {
  const { buildId: _discarded, ...withoutBuildId } = snapshot;
  void _discarded;
  const canonical = JSON.stringify(withoutBuildId);
  const buildId = createHash("sha256").update(canonical).digest("hex");
  return publicSnapshotSchema.parse({
    schemaVersion: 1,
    buildId,
    run: withoutBuildId.run,
    overview: withoutBuildId.overview,
    products: withoutBuildId.products,
    reviews: withoutBuildId.reviews,
    changes: withoutBuildId.changes,
    providers: withoutBuildId.providers,
  });
}

function prepareDemo() {
  const fixture = resolve(process.cwd(), "test", "fixtures", "public-snapshot.json");
  return finalizeSnapshot(publicSnapshotSchema.parse(json(readFileSync(fixture, "utf8"), "fixture")));
}

function prepareReal(snapshotPath, expectedRunId) {
  if (!expectedRunId) throw new Error("PIM_EXPECTED_RUN_ID is required for a non-demo build.");
  const db = new Database(resolve(snapshotPath), { readonly: true, fileMustExist: true });
  try {
    db.pragma("query_only = ON");
    if (db.pragma("user_version", { simple: true }) !== 1) {
      throw new Error("Unsupported SQLite schema version.");
    }
    const run = db.prepare(`
      SELECT run_id, finished_at, status, catalogue_complete, synthetic, manifest_json
      FROM scrape_runs
      WHERE run_id = ? AND finished_at IS NOT NULL AND status IN ('complete', 'partial')
    `).get(expectedRunId);
    if (!run) throw new Error("The expected finalized run was not found.");
    if (Boolean(run.synthetic)) throw new Error("A synthetic run cannot be used for a non-demo build.");

    const manifest = json(run.manifest_json, "run manifest");
    const cohortIds = Array.isArray(manifest.cohort_ids) ? manifest.cohort_ids.map(String) : [];
    const cohortSet = new Set(cohortIds);
    const sourceStatuses = manifest.source_parse_status && typeof manifest.source_parse_status === "object"
      ? manifest.source_parse_status
      : {};

    const productRows = db.prepare(
      "SELECT record_json FROM product_snapshots WHERE run_id=? ORDER BY product_id",
    ).all(expectedRunId);
    const comparisonRows = db.prepare(`
      SELECT c.record_json AS comparison_json, f.fingerprint, f.priority, f.severity, f.state
      FROM comparisons c LEFT JOIN conflicts f ON f.comparison_id=c.comparison_id
      WHERE c.run_id=? ORDER BY COALESCE(f.priority,-1) DESC,c.product_id,c.comparison_id
    `).all(expectedRunId);
    const observationRows = db.prepare(`
      SELECT a.record_json AS observation_json, cap.record_json AS capture_json,
             s.url, s.source_type
      FROM product_attributes a
      JOIN captures cap ON cap.capture_id=a.capture_id
      JOIN sources s ON s.source_id=a.source_id
      WHERE a.run_id=? ORDER BY a.observation_id
    `).all(expectedRunId);
    const mappingRows = db.prepare(`
      SELECT record_json FROM mappings
      WHERE product_id IN (SELECT product_id FROM product_snapshots WHERE run_id=?)
      ORDER BY product_id,mapping_id
    `).all(expectedRunId);
    const changeRows = db.prepare(`
      SELECT record_json FROM changes
      WHERE product_id IN (SELECT product_id FROM product_snapshots WHERE run_id=?)
      ORDER BY detected_at DESC,change_id
    `).all(expectedRunId);
    const finalizedRuns = Number(db.prepare(`
      SELECT COUNT(*) AS finalized_runs
      FROM scrape_runs
      WHERE finished_at IS NOT NULL AND status IN ('complete','partial') AND synthetic=0
    `).get().finalized_runs);

    const rawProducts = productRows.map((row) => json(row.record_json, "product"));
    const rawMappings = mappingRows.map((row) => json(row.record_json, "mapping"));
    const evidence = observationRows.map(projectEvidence);
    const evidenceById = new Map(evidence.map((item) => [item.observationId, item]));
    const productNameById = new Map(rawProducts.map((item) => [String(item.product_id), String(item.name)]));
    const publicMappingById = new Map(rawMappings.map((item) => [String(item.mapping_id), projectMapping(item)]));

    const reviews = comparisonRows.map((row) => {
      const item = json(row.comparison_json, "comparison");
      return {
        comparisonId: String(item.comparison_id),
        fingerprint: nullableString(row.fingerprint),
        productId: String(item.product_id),
        productName: productNameById.get(String(item.product_id)) ?? String(item.product_id),
        field: String(item.field),
        kind: String(item.kind),
        status: String(item.status),
        reason: String(item.reason),
        reasonCode: String(item.reason_code),
        confidence: Number(item.confidence),
        priority: typeof row.priority === "number" ? row.priority : null,
        severity: nullableString(row.severity),
        state: nullableString(row.state),
        mapping: item.mapping_id ? publicMappingById.get(String(item.mapping_id)) ?? null : null,
        left: item.left_id ? evidenceById.get(String(item.left_id)) ?? null : null,
        right: item.right_id ? evidenceById.get(String(item.right_id)) ?? null : null,
      };
    });

    const products = rawProducts.map((item) => {
      const productId = String(item.product_id);
      return {
        productId,
        name: String(item.name),
        category: String(item.category),
        providerName: nullableString(item.provider_name_raw),
        activeStatus: String(item.active_status ?? "unknown"),
        clickpeUrl: nullableString(item.clickpe_url),
        cohortMember: cohortSet.has(productId),
        observations: evidence.filter((observation) => observationRows.find((row) => json(row.observation_json, "observation").observation_id === observation.observationId && json(row.observation_json, "observation").product_id === productId)),
        mappings: rawMappings.filter((mapping) => String(mapping.product_id) === productId).map(projectMapping),
        reviewCount: reviews.filter((review) => review.productId === productId && review.status !== "MATCH").length,
      };
    });

    const changes = changeRows.map((row) => {
      const item = json(row.record_json, "change");
      const productId = String(item.product_id);
      return {
        changeId: String(item.change_id),
        productId,
        productName: productNameById.get(productId) ?? productId,
        sourceId: nullableString(item.source_id),
        field: nullableString(item.field),
        type: String(item.type),
        detectedAt: String(item.detected_at),
      };
    });

    const providerGroups = new Map();
    for (const mapping of rawMappings) {
      const entityId = nullableString(mapping.entity_id) ?? "unresolved";
      const key = `${entityId}\u0000${String(mapping.role)}`;
      if (!providerGroups.has(key)) {
        providerGroups.set(key, {
          entityId,
          role: String(mapping.role),
          programmes: new Set(),
          products: new Set(),
          sources: new Set(),
          openReviews: new Set(),
        });
      }
      const group = providerGroups.get(key);
      if (mapping.programme) group.programmes.add(String(mapping.programme));
      group.products.add(String(mapping.product_id));
      if (mapping.review_state === "approved" && mapping.scope === "same_programme") {
        group.sources.add(String(mapping.source_id));
      }
      for (const review of reviews) {
        const reviewRaw = comparisonRows.find((row) => json(row.comparison_json, "comparison").comparison_id === review.comparisonId);
        const comparison = reviewRaw ? json(reviewRaw.comparison_json, "comparison") : null;
        if (comparison?.mapping_id === mapping.mapping_id && review.state === "open") {
          group.openReviews.add(review.comparisonId);
        }
      }
    }
    const providers = [...providerGroups.values()]
      .map((group) => ({
        entityId: group.entityId,
        role: group.role,
        programmes: group.programmes.size,
        products: group.products.size,
        approvedSources: group.sources.size,
        openReviews: group.openReviews.size,
      }))
      .sort((left, right) => `${left.entityId}:${left.role}`.localeCompare(`${right.entityId}:${right.role}`));

    const approvedCoverage = new Set(
      rawMappings
        .filter((mapping) => mapping.review_state === "approved" && mapping.scope === "same_programme" && sourceStatuses[mapping.source_id] === "ok")
        .map((mapping) => String(mapping.product_id)),
    ).size;

    return finalizeSnapshot({
      schemaVersion: 1,
      buildId: "0".repeat(64),
      run: {
        runId: String(run.run_id),
        finishedAt: String(run.finished_at),
        status: String(run.status),
        synthetic: false,
        catalogueComplete: Boolean(run.catalogue_complete),
      },
      overview: {
        inventoryProducts: products.length,
        cohortProducts: cohortIds.length,
        reviewItems: reviews.filter((review) => review.status !== "MATCH").length,
        highPriorityItems: reviews.filter((review) => review.state === "open" && (review.priority ?? -1) >= 70).length,
        failedSources: Object.values(sourceStatuses).filter((status) => status !== "ok").length,
        coverageNumerator: approvedCoverage,
        coverageDenominator: cohortIds.length,
        recentChanges: changes.length,
        finalizedRuns,
      },
      products,
      reviews,
      changes,
      providers,
    });
  } finally {
    db.close();
  }
}

function main() {
  const output = resolve(process.env.PIM_PUBLIC_SNAPSHOT_OUT ?? ".cache/public-snapshot.json");
  const snapshot = process.env.PIM_UI_DEMO === "1"
    ? prepareDemo()
    : prepareReal(process.env.PIM_SNAPSHOT_PATH ?? "", process.env.PIM_EXPECTED_RUN_ID ?? "");
  mkdirSync(dirname(output), { recursive: true });
  const temporary = `${output}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  rmSync(output, { force: true });
  renameSync(temporary, output);
  process.stdout.write(`Prepared public snapshot ${snapshot.buildId}.\n`);
}

try {
  main();
} catch (error) {
  const message = error instanceof Error ? error.message : "Snapshot preparation failed.";
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
}
