import { formatField, formatHash, formatTimestamp, formatValue } from "@/lib/format";
import type { EvidenceView, ReviewView } from "@/lib/snapshot/types";

import { StatusMark } from "./status-mark";

function safeUrl(value: string | null): string | null {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? parsed.href : null;
  } catch {
    return null;
  }
}

function SourceEvidence({ title, evidence }: { title: string; evidence: EvidenceView | null }) {
  if (!evidence) {
    return (
      <section className="evidence-source">
        <h2>{title}</h2>
        <p>This side has no stored observation for the selected comparison.</p>
      </section>
    );
  }
  const url = safeUrl(evidence.sourceUrl);
  return (
    <section className="evidence-source">
      <h2>{title}</h2>
      <StatusMark value={evidence.state} />
      <blockquote>{evidence.rawText || "No source quote was stored."}</blockquote>
      <p className="evidence-value">{formatValue(evidence)}</p>
      <dl className="evidence-meta">
        <div><dt>Source</dt><dd>{formatField(evidence.sourceType)} · {evidence.sourceId}</dd></div>
        <div><dt>Retrieved</dt><dd>{formatTimestamp(evidence.retrievedAt)}</dd></div>
        <div><dt>Locator</dt><dd>{evidence.locator}</dd></div>
        <div><dt>SHA-256</dt><dd className="hash">{formatHash(evidence.sha256)}</dd></div>
        <div><dt>Source link</dt><dd>{url ? <a href={url} target="_blank" rel="noreferrer noopener">Open {title.toLowerCase()} source</a> : "Source URL unavailable."}</dd></div>
      </dl>
    </section>
  );
}

export function EvidenceSeam({ review }: { review: ReviewView }) {
  return (
    <div className="evidence-seam" data-testid="evidence-seam">
      <SourceEvidence title="ClickPe evidence" evidence={review.left} />
      <section className="evidence-decision">
        <h2>Stored decision</h2>
        <StatusMark value={review.status} />
        <p className="decision-reason">{review.reason}</p>
        <dl className="decision-meta">
          <div><dt>Reason code</dt><dd>{formatField(review.reasonCode)}</dd></div>
          <div><dt>Comparison</dt><dd>{formatField(review.kind)}</dd></div>
          <div><dt>Mapping scope</dt><dd>{review.mapping ? formatField(review.mapping.scope) : "No stored mapping"}</dd></div>
        </dl>
        <p className="neutral-limitation">Review items are not findings of error or wrongdoing.</p>
      </section>
      <SourceEvidence title="Comparison evidence" evidence={review.right} />
    </div>
  );
}
