PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=5000;
CREATE TABLE IF NOT EXISTS scrape_runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
  status TEXT NOT NULL, catalogue_complete INTEGER NOT NULL DEFAULT 0,
  synthetic INTEGER NOT NULL DEFAULT 0, manifest_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS providers (provider_id TEXT PRIMARY KEY, record_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY, record_json TEXT NOT NULL,
  first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, active_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (source_id TEXT PRIMARY KEY, url TEXT NOT NULL, source_type TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS captures (
  capture_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs,
  source_id TEXT NOT NULL REFERENCES sources, retrieved_at TEXT NOT NULL,
  status TEXT NOT NULL, sha256 TEXT, raw_path TEXT, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS product_snapshots (
  run_id TEXT NOT NULL REFERENCES scrape_runs, product_id TEXT NOT NULL REFERENCES products,
  record_json TEXT NOT NULL, PRIMARY KEY(run_id, product_id)
);
CREATE TABLE IF NOT EXISTS product_attributes (
  observation_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs,
  product_id TEXT NOT NULL REFERENCES products, source_id TEXT NOT NULL REFERENCES sources,
  capture_id TEXT NOT NULL REFERENCES captures, field TEXT NOT NULL,
  state TEXT NOT NULL, record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mappings (mapping_id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products, source_id TEXT NOT NULL REFERENCES sources, record_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS product_entities (product_id TEXT NOT NULL REFERENCES products, provider_id TEXT NOT NULL REFERENCES providers, role TEXT NOT NULL, evidence_json TEXT NOT NULL, PRIMARY KEY(product_id,provider_id,role));
CREATE TABLE IF NOT EXISTS comparisons (comparison_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES scrape_runs, product_id TEXT NOT NULL REFERENCES products, record_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conflicts (fingerprint TEXT PRIMARY KEY, comparison_id TEXT NOT NULL REFERENCES comparisons, priority INTEGER NOT NULL, severity TEXT NOT NULL, state TEXT NOT NULL, last_seen TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review_events (event_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL REFERENCES conflicts, reviewed_at TEXT NOT NULL, reviewer TEXT NOT NULL, disposition TEXT NOT NULL, note TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS changes (change_id TEXT PRIMARY KEY, product_id TEXT NOT NULL REFERENCES products, detected_at TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS attributes_lookup ON product_attributes(product_id,source_id,field,run_id);
PRAGMA user_version=1;

