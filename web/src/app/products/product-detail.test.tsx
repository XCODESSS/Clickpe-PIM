import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

vi.mock("next/navigation", () => ({ notFound: () => { throw new Error("NEXT_NOT_FOUND"); } }));
vi.mock("@/lib/snapshot/get-snapshot", async () => {
  const { readFileSync: read } = await import("node:fs");
  const { publicSnapshotSchema: schema } = await import("@/lib/snapshot/types");
  const fixture = schema.parse(JSON.parse(read("test/fixtures/public-snapshot.json", "utf8")));
  return { getSnapshot: () => fixture };
});

import { generateStaticParams, ProductDetailContent } from "./[productId]/page";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("product evidence detail", () => {
  it("generates every native product route", () => {
    expect(generateStaticParams()).toEqual([
      { productId: "fixture-difference" },
      { productId: "fixture-match" },
    ]);
  });

  it("keeps state labels, zero, false, and unresolved lender distinct", () => {
    render(<ProductDetailContent snapshot={snapshot} productId="fixture-match" />);
    for (const value of ["Unknown", "Absent", "Ambiguous", "Unsupported", "Failed", "0 INR", "No"]) {
      expect(screen.getAllByText(value).length).toBeGreaterThan(0);
    }
    expect(screen.getByText(/Unresolved lender/)).toBeTruthy();
  });

  it("renders contradictory assertions separately and rejects an unknown ID", () => {
    render(<ProductDetailContent snapshot={snapshot} productId="fixture-difference" />);
    expect(screen.getByText("2 assertions")).toBeTruthy();
    expect(screen.getByText("Loan amount up to INR 5 lakh")).toBeTruthy();
    expect(screen.getByText("Loan amount up to INR 3 lakh")).toBeTruthy();
    expect(() => render(<ProductDetailContent snapshot={snapshot} productId="missing" />)).toThrow("NEXT_NOT_FOUND");
  });
});
