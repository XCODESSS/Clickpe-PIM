import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

vi.mock("next/navigation", () => ({
  notFound: () => { throw new Error("NEXT_NOT_FOUND"); },
}));

vi.mock("@/lib/snapshot/get-snapshot", async () => {
  const { readFileSync: read } = await import("node:fs");
  const { publicSnapshotSchema: schema } = await import("@/lib/snapshot/types");
  const fixture = schema.parse(JSON.parse(read("test/fixtures/public-snapshot.json", "utf8")));
  return { getSnapshot: () => fixture };
});

import { generateStaticParams, ReviewDetailContent } from "./[comparisonId]/page";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("review evidence detail", () => {
  it("generates every static comparison route", () => {
    expect(generateStaticParams()).toEqual([
      { comparisonId: "cmp-difference" },
      { comparisonId: "cmp-missing" },
    ]);
  });

  it("shows one-sided evidence, mapping scope, and no mutation controls", () => {
    const { container } = render(<ReviewDetailContent snapshot={snapshot} comparisonId="cmp-missing" />);
    expect(screen.getByText("This side has no stored observation for the selected comparison.")).toBeTruthy();
    expect(screen.getAllByText("No stored mapping").length).toBeGreaterThan(0);
    expect(screen.getByText("This view presents stored public evidence and a comparison decision. It does not establish an error, violation, or suitable loan.")).toBeTruthy();
    expect(container.querySelector("form")).toBeNull();
    expect(container.querySelector("input")).toBeNull();
    expect(screen.queryByRole("button", { name: /submit|record/i })).toBeNull();
  });

  it("rejects an unknown static ID", () => {
    expect(() => render(<ReviewDetailContent snapshot={snapshot} comparisonId="unknown" />)).toThrow("NEXT_NOT_FOUND");
  });
});
