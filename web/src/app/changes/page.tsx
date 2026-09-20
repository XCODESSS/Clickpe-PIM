import Link from "next/link";
import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { formatField, formatTimestamp } from "@/lib/format";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";
import type { PublicSnapshot } from "@/lib/snapshot/types";

export const metadata: Metadata = { title: "Stored changes" };

const changeLabels: Record<string, string> = {
  VALUE_CHANGED: "Value changed",
  PRODUCT_ADDED: "Product added",
  PRODUCT_REMOVED: "Product removed",
  SOURCE_DISAPPEARED: "Source disappeared",
  FIELD_ADDED: "Field added",
  FIELD_REMOVED: "Field removed",
};

export function ChangesContent({ snapshot }: { snapshot: PublicSnapshot }) {
  return (
    <AppShell snapshot={snapshot} activePath="/changes/">
      <header className="route-header">
        <h1>Stored change history</h1>
        <p>Reverse-chronological events recorded by the monitor. No cause is inferred from an event type.</p>
        <p className="method-note">Baseline is not a historical change</p>
      </header>
      {snapshot.changes.length === 0 ? (
        <p className="ledger-empty">No stored historical change is available for this run.</p>
      ) : (
        <div className="ledger-scroll">
          <table className="ledger-table change-ledger">
            <thead>
              <tr><th>Event</th><th>Product</th><th>Field</th><th>Source</th><th>Detected</th></tr>
            </thead>
            <tbody>
              {snapshot.changes.map((change) => (
                <tr key={change.changeId}>
                  <td data-label="Event">{changeLabels[change.type] ?? formatField(change.type)}</td>
                  <th scope="row" data-label="Product">
                    <Link href={`/products/${encodeURIComponent(change.productId)}/`}>{change.productName}</Link>
                  </th>
                  <td data-label="Field">{change.field ? formatField(change.field) : "Unknown"}</td>
                  <td data-label="Source">{change.sourceId ?? "Unknown"}</td>
                  <td data-label="Detected"><time dateTime={change.detectedAt}>{formatTimestamp(change.detectedAt)}</time></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

export default function ChangesPage() {
  return <ChangesContent snapshot={getSnapshot()} />;
}
