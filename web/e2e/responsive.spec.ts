import { expect, test } from "@playwright/test";

const routes = [
  "/",
  "/reviews/",
  "/reviews/cmp-difference/",
  "/products/",
  "/products/fixture-difference/",
  "/changes/",
  "/providers/",
];
const viewports = [
  { width: 390, height: 844 },
  { width: 768, height: 1024 },
  { width: 1440, height: 1024 },
];

for (const viewport of viewports) {
  test(`avoids horizontal document overflow at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    for (const route of routes) {
      await page.goto(route);
      const overflow = await page.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth);
      expect(overflow, `${route} overflowed at ${viewport.width}px`).toBe(false);
    }
  });
}

test("keeps evidence in source, decision, comparison order on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/reviews/cmp-difference/");
  await expect(page.getByTestId("evidence-seam").getByRole("heading", { level: 2 })).toHaveText([
    "ClickPe evidence",
    "Stored decision",
    "Comparison evidence",
  ]);
});

test("removes motion when requested", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const durations = await page.locator("body, a, .skip-link").evaluateAll((elements) =>
    elements.map((element) => getComputedStyle(element).transitionDuration));
  expect(new Set(durations)).toEqual(new Set(["0s"]));
});

test("keeps navigation and evidence reachable at 200 percent zoom", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/reviews/cmp-difference/");
  await page.evaluate(() => { document.body.style.zoom = "2"; });
  await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
  await page.getByRole("heading", { name: "Comparison evidence" }).scrollIntoViewIfNeeded();
  await expect(page.getByRole("heading", { name: "Comparison evidence" })).toBeVisible();
});
