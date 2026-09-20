import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { StatusMark } from "@/components/status-mark";
import { formatField, formatHash, formatTimestamp, formatValue } from "@/lib/format";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";
import type { EvidenceView, PublicSnapshot } from "@/lib/snapshot/types";

export const metadata: Metadata = { title: "Product detail" };
export const dynamicParams = false;

export function generateStaticParams() {
  return getSnapshot().products.map(({ productId }) => ({ productId }));
}

function safeUrl(value: string | null): string | null {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null;
  } catch {
    return null;
  }
}

function ObservationRecord({ evidence }: { evidence: EvidenceView }) {
  const sourceUrl = safeUrl(evidence.sourceUrl);
  return (
    <article className="observation-record">
      <header>
        <StatusMark value={evidence.state} />
        <strong>{formatValue(evidence)}</strong>
      </header>
      <blockquote>{evidence.rawText || "No source quote was stored."}</blockquote>
      <dl className="definition-grid">
        <div><dt>Source type</dt><dd>{formatField(evidence.sourceType)}</dd></div>
        <div><dt>Unit</dt><dd>{evidence.value?.unit ?? "Unknown"}</dd></div>
        <div><dt>Period</dt><dd>{evidence.value ? formatField(evidence.value.period) : "Unknown"}</dd></div>
        <div><dt>Basis</dt><dd>{evidence.value ? formatField(evidence.value.basis) : "Unknown"}</dd></div>
        <div><dt>Locator</dt><dd>{evidence.locator}</dd></div>
        <div><dt>Evidence ID</dt><dd>{evidence.observationId}</dd></div>
        <div><dt>Retrieved</dt><dd>{formatTimestamp(evidence.retrievedAt)}</dd></div>
        <div><dt>SHA-256</dt><dd className="hash">{formatHash(evidence.sha256)}</dd></div>
        <div><dt>Source link</dt><dd>{sourceUrl ? <a href={sourceUrl} target="_blank" rel="noreferrer noopener">Open {formatField(evidence.sourceType)} source</a> : "Source URL unavailable."}</dd></div>
      </dl>
    </article>
  );
}

export function ProductDetailContent({ snapshot, productId }: { snapshot: PublicSnapshot; productId: string }) {
  const product = snapshot.products.find((item) => item.productId === productId);
  if (!product) notFound();
  const byField = new Map<string, EvidenceView[]>();
  for (const observation of product.observations) {
    const items = byField.get(observation.field) ?? [];
    items.push(observation);
    byField.set(observation.field, items);
  }
  const hasResolvedLender = product.mappings.some((mapping) => mapping.role === "lender" && mapping.reviewState === "approved" && mapping.scope === "same_programme");
  return (
    <AppShell snapshot={snapshot} activePath="/products/">
      <header className="route-header">
        <h1>{product.name}</h1>
        <p>{product.productId} · {formatField(product.category)} · Provider display: {product.providerName ?? "Unknown"}</p>
      </header>
      {!hasResolvedLender ? <p className="run-warning">Unresolved lender. No approved same-programme lender relationship is stored for this product.</p> : null}
      <section className="mapping-register" aria-labelledby="mapping-heading">
        <h2 id="mapping-heading">Stored relationships</h2>
        {product.mappings.length === 0 ? <p>No relationship mapping is stored.</p> : product.mappings.map((mapping, index) => (
          <dl className="definition-grid mapping-row" key={`${mapping.role}-${mapping.programme ?? "unknown"}-${index}`}>
            <div><dt>Role</dt><dd>{formatField(mapping.role)}</dd></div>
            <div><dt>Programme</dt><dd>{mapping.programme ?? "Unknown"}</dd></div>
            <div><dt>Segment</dt><dd>{mapping.segment ?? "Unknown"}</dd></div>
            <div><dt>Geography</dt><dd>{mapping.geography ?? "Unknown"}</dd></div>
            <div><dt>Scope</dt><dd>{formatField(mapping.scope)}</dd></div>
            <div><dt>Review state</dt><dd>{formatField(mapping.reviewState)}</dd></div>
            <div><dt>Confidence</dt><dd>{mapping.confidence}</dd></div>
            <div><dt>Rationale</dt><dd>{mapping.rationale}</dd></div>
          </dl>
        ))}
      </section>
      <section className="observation-register" aria-labelledby="observation-heading">
        <h2 id="observation-heading">Stored observations</h2>
        {byField.size === 0 ? <p>No public observations are stored for this product in the selected run.</p> : [...byField.entries()].map(([field, observations]) => (
          <section className="field-group" key={field} aria-labelledby={`field-${field}`}>
            <h3 id={`field-${field}`}>{formatField(field)} <span>{observations.length} {observations.length === 1 ? "assertion" : "assertions"}</span></h3>
            {observations.map((observation) => <ObservationRecord evidence={observation} key={observation.observationId} />)}
          </section>
        ))}
      </section>
    </AppShell>
  );
}

export default async function ProductDetailPage({ params }: { params: Promise<{ productId: string }> }) {
  const { productId } = await params;
  return <ProductDetailContent snapshot={getSnapshot()} productId={productId} />;
}
