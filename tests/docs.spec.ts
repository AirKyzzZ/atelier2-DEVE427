import { test, expect } from "@playwright/test"

test.describe("Docs & pages MDX (non-régression KAN-13..15, KAN-21..23)", () => {
  test("4.1 — /guides affiche la liste des guides", async ({ page }) => {
    const response = await page.goto("/guides")
    expect(response?.status()).toBeLessThan(400)
    await expect(page.locator("h1").first()).toBeVisible()
  })

  test("4.2 — /terms rend le contenu MDX", async ({ page }) => {
    const response = await page.goto("/terms")
    expect(response?.status()).toBeLessThan(400)
    await expect(page.locator("h1").first()).toBeVisible()
  })

  test("4.3 — /privacy rend le contenu MDX", async ({ page }) => {
    const response = await page.goto("/privacy")
    expect(response?.status()).toBeLessThan(400)
    await expect(page.locator("h1").first()).toBeVisible()
  })

  test("4.4 — la sidebar docs ne génère pas d'erreur key React", async ({
    page,
  }) => {
    const consoleErrors: string[] = []
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text())
    })
    await page.goto("/guides")
    await page.waitForLoadState("networkidle")
    // Second rendu pour forcer le re-render
    await page.reload()
    await page.waitForLoadState("networkidle")

    const keyErrors = consoleErrors.filter((e) =>
      /unique "key"/i.test(e)
    )
    expect(keyErrors, keyErrors.join("\n")).toEqual([])
  })
})
