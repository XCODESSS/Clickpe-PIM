import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const routes = [
  "/",
  "/reviews/",
  "/reviews/cmp-difference/",
  "/reviews/cmp-missing/",
  "/products/",
  "/products/fixture-difference/",
  "/products/fixture-match/",
  "/changes/",
  "/providers/",
];

for (const route of routes) {
  test(`has no serious or critical axe findings on ${route}`, async ({ page }) => {
    await page.goto(route);
    const results = await new AxeBuilder({ page }).analyze();
    const blocking = results.violations.filter(({ impact }) => impact === "serious" || impact === "critical");
    expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
  });
}
