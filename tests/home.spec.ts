import { test, expect } from "@playwright/test"

test.describe("Accueil & pages marketing (cas usuels)", () => {
  test("1.1 — la homepage répond 200 et affiche le h1", async ({ page }) => {
    const response = await page.goto("/")
    expect(response?.status()).toBeLessThan(400)
    await expect(
      page.getByRole("heading", {
        level: 1,
        name: /An example app built using Next\.js 13 server components/i,
      })
    ).toBeVisible()
  })

  test("1.2 — le CTA Get Started redirige vers /login", async ({ page }) => {
    await page.goto("/")
    await page.getByRole("link", { name: /Get Started/i }).first().click()
    await expect(page).toHaveURL(/\/login$/)
  })

  test("1.3 — la section Features est visible", async ({ page }) => {
    await page.goto("/")
    const features = page.locator("#features")
    await features.scrollIntoViewIfNeeded()
    await expect(features).toBeVisible()
    await expect(
      features.getByRole("heading", { level: 2, name: "Features" })
    ).toBeVisible()
  })

  test("1.4 — la section Proudly Open Source est rendue", async ({ page }) => {
    await page.goto("/")
    await expect(
      page.getByRole("heading", { level: 2, name: /Proudly Open Source/i })
    ).toBeVisible()
  })

  test("1.5 — la page Pricing affiche le plan PRO", async ({ page }) => {
    await page.goto("/pricing")
    await expect(
      page.getByRole("heading", { name: /Simple, transparent pricing/i })
    ).toBeVisible()
    await expect(page.getByText("$19")).toBeVisible()
  })

  test("1.6 — une route inexistante retourne 404", async ({ page }) => {
    const response = await page.goto("/cette-page-nexiste-pas-xyz")
    expect(response?.status()).toBe(404)
  })

  test("5.1 — la page Login affiche le formulaire email", async ({ page }) => {
    await page.goto("/login")
    await expect(page).toHaveURL(/\/login$/)
    await expect(
      page.getByRole("heading", { name: /Welcome back|Login|Sign in/i })
    ).toBeVisible({ timeout: 10_000 })
  })

  test("5.2 — la page Register est accessible", async ({ page }) => {
    const response = await page.goto("/register")
    expect(response?.status()).toBeLessThan(400)
  })
})
