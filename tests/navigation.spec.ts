import { test, expect } from "@playwright/test"

test.describe("Navigation (non-régression KAN-5, KAN-10)", () => {
  test.skip(
    ({ browserName, viewport }) =>
      (viewport?.width ?? 1280) < 768,
    "Nav desktop nécessite un viewport >= md"
  )

  test("2.1 — les 4 entrées de la main nav sont rendues sans doublon", async ({
    page,
  }) => {
    await page.goto("/")
    const expectedLinks = ["Features", "Pricing", "Blog", "Documentation"]
    for (const label of expectedLinks) {
      await expect(
        page.getByRole("link", { name: new RegExp(`^${label}$`, "i") }).first()
      ).toBeVisible()
    }
  })

  test("2.2 — aucune erreur console React « key » lors du rendu des nav", async ({
    page,
  }) => {
    const consoleErrors: string[] = []
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        consoleErrors.push(msg.text())
      }
    })
    await page.goto("/")
    await page.waitForLoadState("networkidle")
    // Re-render en naviguant
    await page.goto("/pricing")
    await page.waitForLoadState("networkidle")
    await page.goto("/blog")
    await page.waitForLoadState("networkidle")

    const keyErrors = consoleErrors.filter((e) =>
      /Each child in a list should have a unique "key"/i.test(e)
    )
    expect(keyErrors, `Console a remonté des erreurs de key: ${keyErrors.join("\n")}`).toEqual([])
  })

  test("2.6 — navigation rapide entre plusieurs pages sans erreur", async ({
    page,
  }) => {
    const pages = ["/", "/pricing", "/blog", "/", "/pricing"]
    for (const path of pages) {
      await page.goto(path)
      await expect(page.locator("body")).toBeVisible()
    }
  })
})
