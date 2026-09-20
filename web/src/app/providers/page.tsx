import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { formatField } from "@/lib/format";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";
import type { PublicSnapshot } from "@/lib/snapshot/types";

export const metadata: Metadata = { title: "Provider relationships" };

export function ProvidersContent({ snapshot }: { snapshot: PublicSnapshot }) {
  return (
    <AppShell snapshot={snapshot} activePath="/providers/">
      <header className="route-header">
        <h1>Provider relationships</h1>
        <p>Roles and programmes stay separate. This view does not rank providers.</p>
      </header>
      {snapshot.providers.length === 0 ? (
        <p className="ledger-empty">No stored provider relationship is available for this run.</p>
      ) : (
        <div className="ledger-scroll">
          <table className="ledger-table provider-ledger">
            <thead>
              <tr>
                <th>Entity ID</th><th>Role</th><th>Programme count</th><th>Product count</th>
                <th>Approved applicable source count</th><th>Open review count</th>
              </tr>
            </thead>
            <tbody>
              {snapshot.providers.map((provider) => (
                <tr key={`${provider.entityId}:${provider.role}`}>
                  <th scope="row" data-label="Entity ID">{provider.entityId}</th>
                  <td data-label="Role">{formatField(provider.role)}</td>
                  <td data-label="Programme count">{provider.programmes}</td>
                  <td data-label="Product count">{provider.products}</td>
                  <td data-label="Approved applicable source count">{provider.approvedSources}</td>
                  <td data-label="Open review count">{provider.openReviews}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppShell>
  );
}

export default function ProvidersPage() {
  return <ProvidersContent snapshot={getSnapshot()} />;
}
