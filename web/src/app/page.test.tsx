import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { OverviewContent } from "./page";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("overview", () => {
  it("opens with the highest stored-priority two-sided review and partial state", () => {
    render(<OverviewContent snapshot={snapshot} />);
    expect(screen.getByRole("heading", { name: "Fixture Difference Loan: Loan Amount" })).toBeTruthy();
    expect(screen.getByText(snapshot.reviews[0]!.reason)).toBeTruthy();
    expect(screen.getByText("Some sources did not complete. Stored values may be older than this run.")).toBeTruthy();
    expect(screen.getAllByText("Review items are not findings of error or wrongdoing.").length).toBeGreaterThan(0);
  });

  it("explains an all-match snapshot without inventing a review", () => {
    const allMatch = {
      ...snapshot,
      run: { ...snapshot.run, status: "complete" as const },
      overview: { ...snapshot.overview, reviewItems: 0, failedSources: 0 },
      reviews: snapshot.reviews.map((review) => ({ ...review, status: "MATCH" as const })),
    };
    render(<OverviewContent snapshot={allMatch} />);
    expect(screen.getByText("No two-source review item is available in this snapshot.")).toBeTruthy();
  });

  it("directs publishing away from an empty snapshot", () => {
    render(<OverviewContent snapshot={{ ...snapshot, products: [] }} />);
    expect(screen.getByText("This finalized snapshot contains no products. Select another run before publishing.")).toBeTruthy();
  });
});
