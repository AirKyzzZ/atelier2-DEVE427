import { test, expect, devices } from "@playwright/test"

// Ces tests forcent un viewport mobile pour couvrir la MobileNav
// indépendamment du projet Playwright en cours.
test.use({ ...devices["Pixel 7"] })

test.describe("Responsive / Mobile nav (non-régression KAN-9)", () => {
  test("2.3 / 2.4 — le menu mobile s'ouvre au tap sur « Menu »", async ({
    page,
  }) => {
    await page.goto("/")
    const menuButton = page.getByRole("button", { name: /Menu/i })
    await expect(menuButton).toBeVisible()

    // Avant clic, les liens Blog/Pricing ne sont pas visibles (menu fermé)
    // On ouvre
    await menuButton.click()

    await expect(
      page.getByRole("link", { name: /^Blog$/i }).first()
    ).toBeVisible()
    await expect(
      page.getByRole("link", { name: /^Pricing$/i }).first()
    ).toBeVisible()
  })

  test("2.5 — clic sur « Blog » dans la mobile nav redirige vers /blog", async ({
    page,
  }) => {
    await page.goto("/")
    await page.getByRole("button", { name: /Menu/i }).click()
    await page.getByRole("link", { name: /^Blog$/i }).first().click()
    await expect(page).toHaveURL(/\/blog$/)
  })

  test("mobile nav ne génère pas d'erreur React key", async ({ page }) => {
    const consoleErrors: string[] = []
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text())
    })
    await page.goto("/")
    await page.getByRole("button", { name: /Menu/i }).click()
    await page.waitForTimeout(500)

    const keyErrors = consoleErrors.filter((e) =>
      /unique "key"/i.test(e)
    )
    expect(keyErrors, keyErrors.join("\n")).toEqual([])
  })
})
