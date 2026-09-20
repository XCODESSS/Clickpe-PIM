import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { EvidenceSeam } from "@/components/evidence-seam";
import { formatField } from "@/lib/format";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";
import type { PublicSnapshot } from "@/lib/snapshot/types";

export const metadata: Metadata = { title: "Evidence detail" };
export const dynamicParams = false;

export function generateStaticParams() {
  return getSnapshot().reviews.map(({ comparisonId }) => ({ comparisonId }));
}

export function ReviewDetailContent({ snapshot, comparisonId }: { snapshot: PublicSnapshot; comparisonId: string }) {
  const review = snapshot.reviews.find((item) => item.comparisonId === comparisonId);
  if (!review) notFound();
  return (
    <AppShell snapshot={snapshot} activePath="/reviews/">
      <header className="route-header">
        <h1>{review.productName}: {formatField(review.field)}</h1>
        <p>Stored priority {review.priority ?? "Unknown"} · {formatField(review.status)}</p>
      </header>
      <EvidenceSeam review={review} />
      <section className="detail-register" aria-labelledby="comparison-detail-heading">
        <h2 id="comparison-detail-heading">Comparison record</h2>
        <dl className="definition-grid">
          <div><dt>Kind</dt><dd>{formatField(review.kind)}</dd></div>
          <div><dt>Reason code</dt><dd>{formatField(review.reasonCode)}</dd></div>
          <div><dt>Confidence</dt><dd>{review.confidence}</dd></div>
          <div><dt>Priority</dt><dd>{review.priority ?? "Unknown"}</dd></div>
          <div><dt>Severity</dt><dd>{review.severity ? formatField(review.severity) : "Unknown"}</dd></div>
          <div><dt>Mapping scope</dt><dd>{review.mapping ? formatField(review.mapping.scope) : "No stored mapping"}</dd></div>
          <div><dt>Mapping rationale</dt><dd>{review.mapping?.rationale ?? "No stored mapping rationale."}</dd></div>
        </dl>
        <p className="method-note">This view presents stored public evidence and a comparison decision. It does not establish an error, violation, or suitable loan.</p>
      </section>
    </AppShell>
  );
}

export default async function ReviewDetailPage({ params }: { params: Promise<{ comparisonId: string }> }) {
  const { comparisonId } = await params;
  return <ReviewDetailContent snapshot={getSnapshot()} comparisonId={comparisonId} />;
}
