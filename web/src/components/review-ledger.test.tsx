import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { ReviewLedger } from "./review-ledger";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("ReviewLedger", () => {
  it("filters stored fields and clears without exposing raw evidence", async () => {
    const user = userEvent.setup();
    render(<ReviewLedger reviews={snapshot.reviews} />);
    for (const name of ["Field", "Status", "Severity", "Product"]) expect(screen.getByLabelText(name)).toBeTruthy();
    expect(screen.getByText("2 review items")).toBeTruthy();
    expect(screen.queryByText("Loan amount up to INR 5 lakh")).toBeNull();
    await user.selectOptions(screen.getByLabelText("Status"), "MISSING_PROVIDER");
    expect(screen.getByText("1 review item")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Fixture Match Loan" }).getAttribute("href")).toBe("/reviews/cmp-missing");
    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(screen.getByText("2 review items")).toBeTruthy();
  });

  it("uses a real keyboard-operable link and gives directional empty copy", async () => {
    window.history.replaceState(null, "", "/");
    const user = userEvent.setup();
    render(<ReviewLedger reviews={snapshot.reviews} />);
    const link = screen.getByRole("link", { name: "Fixture Difference Loan" });
    link.focus();
    expect(document.activeElement).toBe(link);
    await user.selectOptions(screen.getByLabelText("Field"), "loan_amount");
    await user.selectOptions(screen.getByLabelText("Status"), "MISSING_PROVIDER");
    expect(screen.getByText("No review items match these filters. Clear filters to see the full queue.")).toBeTruthy();
  });
});
