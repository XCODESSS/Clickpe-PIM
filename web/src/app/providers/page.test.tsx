import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { ProvidersContent } from "./page";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("provider relationships", () => {
  it("keeps entity roles separate and reports relationship counts", () => {
    const secondRole = { ...snapshot.providers[0]!, role: "servicer", programmes: 0, products: 1 };
    const { container } = render(<ProvidersContent snapshot={{ ...snapshot, providers: [...snapshot.providers, secondRole] }} />);
    expect(screen.getByText("Roles and programmes stay separate. This view does not rank providers.")).toBeTruthy();
    expect(screen.getAllByText("fixture_lender_b")).toHaveLength(2);
    expect(screen.getByText("Lender")).toBeTruthy();
    expect(screen.getByText("Servicer")).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "Approved applicable source count" })).toBeTruthy();
    expect(container.textContent).not.toMatch(/\b(score|star|position|best provider)\b/i);
  });

  it("states when no relationship rows were stored", () => {
    render(<ProvidersContent snapshot={{ ...snapshot, providers: [] }} />);
    expect(screen.getByText("No stored provider relationship is available for this run.")).toBeTruthy();
  });
});
