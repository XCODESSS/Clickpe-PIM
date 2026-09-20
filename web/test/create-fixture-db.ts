import Database from "better-sqlite3";

function compact(value: unknown): string {
  return JSON.stringify(value);
}

export function createFixtureDb(path: string): void {
  const db = new Database(path);
  db.exec(`
    PRAGMA user_version=1;
    CREATE TABLE scrape_runs (
      run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
      status TEXT NOT NULL, catalogue_complete INTEGER NOT NULL,
      synthetic INTEGER NOT NULL, manifest_json TEXT NOT NULL
    );
    CREATE TABLE products (
      product_id TEXT PRIMARY KEY, record_json TEXT NOT NULL,
      first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, active_status TEXT NOT NULL
    );
    CREATE TABLE sources (source_id TEXT PRIMARY KEY, url TEXT NOT NULL, source_type TEXT NOT NULL, record_json TEXT NOT NULL);
    CREATE TABLE captures (
      capture_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, source_id TEXT NOT NULL,
      retrieved_at TEXT NOT NULL, status TEXT NOT NULL, sha256 TEXT, raw_path TEXT,
      record_json TEXT NOT NULL
    );
    CREATE TABLE product_snapshots (run_id TEXT NOT NULL, product_id TEXT NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(run_id,product_id));
    CREATE TABLE product_attributes (
      observation_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, product_id TEXT NOT NULL,
      source_id TEXT NOT NULL, capture_id TEXT NOT NULL, field TEXT NOT NULL,
      state TEXT NOT NULL, record_json TEXT NOT NULL
    );
    CREATE TABLE mappings (mapping_id TEXT PRIMARY KEY, product_id TEXT NOT NULL, source_id TEXT NOT NULL, record_json TEXT NOT NULL);
    CREATE TABLE comparisons (comparison_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, product_id TEXT NOT NULL, record_json TEXT NOT NULL);
    CREATE TABLE conflicts (
      fingerprint TEXT PRIMARY KEY, comparison_id TEXT NOT NULL, priority INTEGER NOT NULL,
      severity TEXT NOT NULL, state TEXT NOT NULL, last_seen TEXT NOT NULL, record_json TEXT NOT NULL
    );
    CREATE TABLE review_events (
      event_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, reviewed_at TEXT NOT NULL,
      reviewer TEXT NOT NULL, disposition TEXT NOT NULL, note TEXT NOT NULL
    );
    CREATE TABLE changes (change_id TEXT PRIMARY KEY, product_id TEXT NOT NULL, detected_at TEXT NOT NULL, record_json TEXT NOT NULL);
  `);

  const manifest = compact({
    cohort_ids: ["fixture_difference", "fixture_match"],
    source_parse_status: { clickpe_catalogue: "ok", provider_difference: "ok" },
  });
  const insertRun = db.prepare("INSERT INTO scrape_runs VALUES (?,?,?,?,?,?,?)");
  insertRun.run("ui_fixture_run", "2026-09-20T07:00:00Z", "2026-09-20T08:00:00Z", "complete", 1, 0, manifest);
  insertRun.run("synthetic_run", "2026-09-20T07:00:00Z", "2026-09-20T08:00:00Z", "complete", 1, 1, manifest);
  insertRun.run("unfinished_run", "2026-09-20T07:00:00Z", null, "running", 0, 0, manifest);
  insertRun.run("failed_run", "2026-09-20T07:00:00Z", "2026-09-20T08:00:00Z", "failed", 0, 0, manifest);

  const products = [
    { product_id: "fixture_difference", name: "Fixture Difference Loan", category: "personal_loan", provider_name_raw: "Fixture Lender", clickpe_url: "https://example.org/clickpe/difference", active_status: "active" },
    { product_id: "fixture_match", name: "Fixture Match Loan", category: "personal_loan", provider_name_raw: null, clickpe_url: "https://example.org/clickpe/match", active_status: "active" },
  ];
  const insertProduct = db.prepare("INSERT INTO products VALUES (?,?,?,?,?)");
  const insertSnapshot = db.prepare("INSERT INTO product_snapshots VALUES (?,?,?)");
  for (const product of products) {
    insertProduct.run(product.product_id, compact(product), "2026-09-20T08:00:00Z", "2026-09-20T08:00:00Z", "active");
    insertSnapshot.run("ui_fixture_run", product.product_id, compact(product));
  }

  const sources = [
    ["clickpe_catalogue", "https://example.org/clickpe", "clickpe_catalogue"],
    ["provider_difference", "https://example.org/provider", "official_product"],
  ];
  const insertSource = db.prepare("INSERT INTO sources VALUES (?,?,?,?)");
  for (const [sourceId, url, sourceType] of sources) insertSource.run(sourceId, url, sourceType, compact({ sourceId }));

  const insertCapture = db.prepare("INSERT INTO captures VALUES (?,?,?,?,?,?,?,?)");
  for (const [index, [sourceId, url, sourceType]] of sources.entries()) {
    const capture = {
      capture_id: `capture_${index}`,
      run_id: "ui_fixture_run",
      source_id: sourceId,
      source_type: sourceType,
      url,
      final_url: url,
      retrieved_at: "2026-09-20T08:00:00Z",
      status: "ok",
      http_status: 200,
      sha256: String(index + 1).repeat(64),
      raw_path: "C:\\private\\capture.html",
      media_type: "text/html",
      error_code: null,
    };
    insertCapture.run(capture.capture_id, capture.run_id, sourceId, capture.retrieved_at, "ok", capture.sha256, capture.raw_path, compact(capture));
  }

  const value = (upper: string) => ({ kind: "money", lower: null, upper, text: null, boolean: null, options: [], unit: "INR", period: "unknown", basis: "unknown", qualifier: "up_to", approximate: false });
  const observations = [
    { observation_id: "obs_left", run_id: "ui_fixture_run", product_id: "fixture_difference", source_id: "clickpe_catalogue", capture_id: "capture_0", field: "loan_amount", state: "present", value: value("500000"), raw_text: "Loan amount up to INR 5 lakh", locator: "/response/0/content/headline", context: "offer", extracted_at: "2026-09-20T08:00:00Z", extractor_version: "1", confidence: 1, conditions: [] },
    { observation_id: "obs_right", run_id: "ui_fixture_run", product_id: "fixture_difference", source_id: "provider_difference", capture_id: "capture_1", field: "loan_amount", state: "present", value: value("300000"), raw_text: "Loan amount up to INR 3 lakh", locator: "#amount", context: "offer", extracted_at: "2026-09-20T08:00:00Z", extractor_version: "1", confidence: 0.98, conditions: [] },
  ];
  const insertObservation = db.prepare("INSERT INTO product_attributes VALUES (?,?,?,?,?,?,?,?)");
  for (const item of observations) insertObservation.run(item.observation_id, item.run_id, item.product_id, item.source_id, item.capture_id, item.field, item.state, compact(item));

  const mapping = { mapping_id: "map_difference", product_id: "fixture_difference", source_id: "provider_difference", entity_id: "fixture_lender", role: "lender", programme: "Fixture Programme", segment: null, geography: "India", scope: "same_programme", review_state: "approved", confidence: 1, evidence_capture_id: "capture_1", evidence_locator: "#programme", rationale: "Synthetic reviewed scope.", reviewed_by: "Private Reviewer Token", reviewed_at: "2026-09-20T08:00:00Z", effective_from: null, effective_to: null };
  db.prepare("INSERT INTO mappings VALUES (?,?,?,?)").run(mapping.mapping_id, mapping.product_id, mapping.source_id, compact(mapping));

  const comparison = { comparison_id: "cmp_difference", run_id: "ui_fixture_run", product_id: "fixture_difference", field: "loan_amount", left_id: "obs_left", right_id: "obs_right", mapping_id: "map_difference", kind: "external", status: "DIFFERENT", reason: "Possible loan amount difference; review programme applicability and the cited source terms.", reason_code: "endpoint_difference", confidence: 0.98, compared_endpoints: ["upper"] };
  db.prepare("INSERT INTO comparisons VALUES (?,?,?,?)").run(comparison.comparison_id, comparison.run_id, comparison.product_id, compact(comparison));
  db.prepare("INSERT INTO conflicts VALUES (?,?,?,?,?,?,?)").run("fingerprint_difference", comparison.comparison_id, 88, "high", "open", "2026-09-20T08:00:00Z", compact({ private: false }));
  db.prepare("INSERT INTO review_events VALUES (?,?,?,?,?,?)").run("event_private", "fingerprint_difference", "2026-09-20T08:00:00Z", "Private Reviewer Token", "dismissed", "Private Reviewer Token");

  const change = { change_id: "change_difference", product_id: "fixture_difference", source_id: "provider_difference", field: "loan_amount", type: "VALUE_CHANGED", previous_id: "old", current_id: "obs_right", detected_at: "2026-09-20T08:00:00Z", synthetic: false };
  db.prepare("INSERT INTO changes VALUES (?,?,?,?)").run(change.change_id, change.product_id, change.detected_at, compact(change));
  db.close();
}
