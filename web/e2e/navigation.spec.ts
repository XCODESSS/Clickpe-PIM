import { expect, test } from "@playwright/test";

test("supports the complete read-only review journey", async ({ page }) => {
  const mutatingRequests: string[] = [];
  page.on("request", (request) => {
    if (["POST", "PUT", "PATCH", "DELETE"].includes(request.method())) {
      mutatingRequests.push(`${request.method()} ${request.url()}`);
    }
  });

  await page.goto("/");
  await expect(page.getByText("Synthetic interface preview")).toBeVisible();
  await page.getByRole("link", { name: "Review queue" }).click();
  await expect(page.getByRole("heading", { name: "Review queue" })).toBeVisible();
  await page.getByLabel("Status").selectOption("DIFFERENT");
  await expect(page).toHaveURL(/status=DIFFERENT/);
  await expect(page.getByText("1 review item")).toBeVisible();
  await page.getByRole("link", { name: "Fixture Difference Loan" }).click();
  await expect(page.getByRole("heading", { name: "Fixture Difference Loan: Loan Amount" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open clickpe evidence source" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open comparison evidence source" })).toBeVisible();

  await page.getByRole("link", { name: "Products" }).click();
  await page.getByRole("link", { name: "Fixture Difference Loan" }).click();
  await expect(page.getByRole("heading", { name: "Fixture Difference Loan" })).toBeVisible();
  await page.getByRole("link", { name: "Changes" }).click();
  await expect(page.getByRole("heading", { name: "Stored change history" })).toBeVisible();
  await page.getByRole("link", { name: "Providers" }).click();
  await expect(page.getByRole("heading", { name: "Provider relationships" })).toBeVisible();
  await expect(page.getByText("Synthetic interface preview")).toBeVisible();
  expect(mutatingRequests).toEqual([]);
});

test("keyboard users can skip, navigate, and open the first review", async ({ page }) => {
  await page.goto("/reviews/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();

  await page.reload();
  let reachedNavigation = false;
  let reachedReview = false;
  for (let index = 0; index < 20; index += 1) {
    await page.keyboard.press("Tab");
    const focused = page.locator(":focus");
    const text = (await focused.textContent())?.trim();
    if (text === "Review queue") reachedNavigation = true;
    if (text === "Fixture Difference Loan") {
      reachedReview = true;
      await page.keyboard.press("Enter");
      break;
    }
  }
  expect(reachedNavigation).toBe(true);
  expect(reachedReview).toBe(true);
  await expect(page.getByRole("heading", { name: "Fixture Difference Loan: Loan Amount" })).toBeVisible();
});
