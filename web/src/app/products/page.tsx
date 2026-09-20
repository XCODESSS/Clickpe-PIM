import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { ProductLedger } from "@/components/product-ledger";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";

export const metadata: Metadata = { title: "Products" };

export default function ProductsPage() {
  const snapshot = getSnapshot();
  return (
    <AppShell snapshot={snapshot} activePath="/products/">
      <header className="route-header">
        <h1>Product evidence</h1>
        <p>Search the selected inventory without changing cohort membership, active state, or stored source claims.</p>
      </header>
      <ProductLedger products={snapshot.products} />
    </AppShell>
  );
}
