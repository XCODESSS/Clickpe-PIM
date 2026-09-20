import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { EvidenceSeam } from "./evidence-seam";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("EvidenceSeam", () => {
  it("keeps both sources, exact evidence, and the neutral stored decision visible", () => {
    render(<EvidenceSeam review={snapshot.reviews[0]!} />);
    expect(screen.getByRole("heading", { name: "ClickPe evidence" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Comparison evidence" })).toBeTruthy();
    expect(screen.getByText("Loan amount up to INR 5 lakh")).toBeTruthy();
    expect(screen.getByText("Loan amount up to INR 3 lakh")).toBeTruthy();
    expect(screen.getByText(snapshot.reviews[0]!.reason)).toBeTruthy();
    expect(screen.getByText("/response/0/content/headline")).toBeTruthy();
    expect(screen.getByText("a".repeat(64))).toBeTruthy();
    expect(screen.getByRole("link", { name: "Open clickpe evidence source" })).toBeTruthy();
    expect(screen.getByText("Review items are not findings of error or wrongdoing.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /record review/i })).toBeNull();
    expect(document.querySelector("form")).toBeNull();
  });

  it("does not create a link for an unsafe source URL", () => {
    const review = {
      ...snapshot.reviews[0]!,
      left: { ...snapshot.reviews[0]!.left!, sourceUrl: "javascript:alert(1)" },
    };
    render(<EvidenceSeam review={review} />);
    expect(screen.getAllByText("Source URL unavailable.")).toHaveLength(1);
  });
});
