import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { RunRegister } from "./run-register";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("RunRegister", () => {
  it("renders nine stored register values without metric cards", () => {
    const { container } = render(<RunRegister snapshot={snapshot} />);
    for (const label of [
      "Inventory products", "Monitored cohort", "Applicable official-source coverage",
      "Review items", "High priority", "Source failures", "Recent changes",
      "Finalized runs", "Run status",
    ]) expect(screen.getByText(label)).toBeTruthy();
    expect(screen.getByText("1/2")).toBeTruthy();
    expect(container.querySelector(".metric-card")).toBeNull();
  });

  it("renders unknown rather than a zero percentage for an empty denominator", () => {
    render(<RunRegister snapshot={{ ...snapshot, overview: { ...snapshot.overview, coverageDenominator: 0, coverageNumerator: 0 } }} />);
    expect(screen.getByText("Unknown")).toBeTruthy();
  });
});
