import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { ChangesContent } from "./page";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("stored changes", () => {
  it("renders only projected change rows with their stored dimensions", () => {
    render(<ChangesContent snapshot={snapshot} />);
    expect(screen.getByText("Value changed")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Fixture Difference Loan" })).toBeTruthy();
    expect(screen.getByText("Loan Amount")).toBeTruthy();
    expect(screen.getByText("provider_difference")).toBeTruthy();
    expect(screen.getByText("20 Sept 2026, 13:00")).toBeTruthy();
    expect(screen.queryByText("Fixture Match Loan")).toBeNull();
    expect(screen.getByText("Baseline is not a historical change")).toBeTruthy();
  });

  it("distinguishes an empty history from a measured zero", () => {
    render(<ChangesContent snapshot={{ ...snapshot, changes: [] }} />);
    expect(screen.getByText("No stored historical change is available for this run.")).toBeTruthy();
  });
});
