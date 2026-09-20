import { mkdirSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

const output = resolve(".artifacts/visual");

test.beforeAll(() => mkdirSync(output, { recursive: true }));

test("captures the required visual review surfaces", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1024 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Evidence register" })).toBeVisible();
  await page.screenshot({ path: resolve(output, "overview-1440x1024.png") });

  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto("/reviews/cmp-difference/");
  await expect(page.getByRole("heading", { name: "Fixture Difference Loan: Loan Amount" })).toBeVisible();
  await page.screenshot({ path: resolve(output, "review-768x1024.png") });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/reviews/cmp-difference/");
  await expect(page.getByText("Synthetic interface preview")).toBeVisible();
  await page.screenshot({ path: resolve(output, "review-390x844.png") });
});
