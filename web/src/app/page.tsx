import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { EmptyState } from "@/components/empty-state";
import { EvidenceSeam } from "@/components/evidence-seam";
import { RunRegister } from "@/components/run-register";
import { formatField, formatTimestamp } from "@/lib/format";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";
import type { PublicSnapshot } from "@/lib/snapshot/types";

export const metadata: Metadata = { title: "Overview" };

export function OverviewContent({ snapshot }: { snapshot: PublicSnapshot }) {
  const featured = snapshot.reviews
    .filter((item) => item.status !== "MATCH" && item.left && item.right)
    .toSorted((left, right) => (right.priority ?? -1) - (left.priority ?? -1))[0] ?? null;
  const partial = snapshot.run.status === "partial" || snapshot.overview.failedSources > 0;
  return (
    <AppShell snapshot={snapshot} activePath="/">
      <header className="route-header">
        <h1>Evidence register</h1>
        <p>Finalized run {snapshot.run.runId} · {formatTimestamp(snapshot.run.finishedAt)}</p>
        <p>Review items are not findings of error or wrongdoing.</p>
      </header>
      {partial ? (
        <p className="run-warning" role="status">Some sources did not complete. Stored values may be older than this run.</p>
      ) : null}
      {snapshot.products.length === 0 ? (
        <EmptyState title="No products">This finalized snapshot contains no products. Select another run before publishing.</EmptyState>
      ) : featured ? (
        <section className="overview-feature" aria-labelledby="featured-heading">
          <div className="section-heading">
            <div>
              <h2 id="featured-heading">{featured.productName}: {formatField(featured.field)}</h2>
              <p>Highest stored-priority review with evidence on both sides.</p>
            </div>
            <a href={`/reviews/${encodeURIComponent(featured.comparisonId)}/`}>Open evidence detail</a>
          </div>
          <EvidenceSeam review={featured} />
        </section>
      ) : (
        <EmptyState title="No two-sided review">No two-source review item is available in this snapshot.</EmptyState>
      )}
      <RunRegister snapshot={snapshot} />
    </AppShell>
  );
}

export default function OverviewPage() {
  return <OverviewContent snapshot={getSnapshot()} />;
}
