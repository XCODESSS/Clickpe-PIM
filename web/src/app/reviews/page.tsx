import type { Metadata } from "next";

import { AppShell } from "@/components/app-shell";
import { ReviewLedger } from "@/components/review-ledger";
import { getSnapshot } from "@/lib/snapshot/get-snapshot";

export const metadata: Metadata = { title: "Review queue" };

export default function ReviewsPage() {
  const snapshot = getSnapshot();
  const reviews = snapshot.reviews.filter((item) => item.status !== "MATCH");
  return (
    <AppShell snapshot={snapshot} activePath="/reviews/">
      <header className="route-header">
        <h1>Review queue</h1>
        <p>Filter stored comparison decisions. Open a row to inspect the exact public evidence and mapping scope.</p>
      </header>
      <ReviewLedger reviews={reviews} />
    </AppShell>
  );
}
