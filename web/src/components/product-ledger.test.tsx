import { readFileSync } from "node:fs";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { publicSnapshotSchema } from "@/lib/snapshot/types";

import { ProductLedger } from "./product-ledger";

const snapshot = publicSnapshotSchema.parse(JSON.parse(readFileSync("test/fixtures/public-snapshot.json", "utf8")));

describe("ProductLedger", () => {
  it.each([
    ["difference", "1 product"],
    ["fixture-match", "1 product"],
    ["personal loan", "2 products"],
    ["fixture lender b", "1 product"],
  ])("searches name, ID, category, and provider with %s", async (query, expectedCount) => {
    const user = userEvent.setup();
    render(<ProductLedger products={snapshot.products} />);
    await user.type(screen.getByLabelText("Search products"), query);
    expect(screen.getByText(expectedCount)).toBeTruthy();
  });

  it("provides stable links and directional zero-result copy", async () => {
    const user = userEvent.setup();
    render(<ProductLedger products={snapshot.products} />);
    expect(screen.getByRole("link", { name: "Fixture Difference Loan" }).getAttribute("href")).toBe("/products/fixture-difference");
    await user.type(screen.getByLabelText("Search products"), "no such product");
    expect(screen.getByText("No products match this search. Clear the search to see the full product list.")).toBeTruthy();
  });
});
