import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { AppShell } from "./app-shell";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("AppShell", () => {
  it("provides landmark navigation, active state, skip link, and synthetic disclosure", () => {
    render(<AppShell snapshot={snapshot} activePath="/reviews/"><h1>Review queue</h1></AppShell>);
    expect(screen.getByRole("link", { name: "Skip to main content" }).getAttribute("href")).toBe("#main-content");
    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeTruthy();
    for (const name of ["Overview", "Review queue", "Products", "Changes", "Providers"]) {
      expect(screen.getByRole("link", { name })).toBeTruthy();
    }
    expect(screen.getByRole("link", { name: "Review queue" }).getAttribute("aria-current")).toBe("page");
    expect(screen.getByText("Synthetic interface preview")).toBeTruthy();
    expect(screen.getAllByRole("main")).toHaveLength(1);
  });
});
