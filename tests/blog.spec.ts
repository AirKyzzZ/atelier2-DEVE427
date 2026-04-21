import { test, expect } from "@playwright/test"

test.describe("Blog & TOC (non-régression KAN-8)", () => {
  test("3.1 — l'index /blog affiche au moins un article", async ({ page }) => {
    await page.goto("/blog")
    await expect(
      page.getByRole("heading", { level: 1, name: /^Blog$/ })
    ).toBeVisible()
    await expect(page.getByText(/built using Contentlayer/i)).toBeVisible()
    const articles = page.locator("article")
    await expect(articles.first()).toBeVisible()
  })

  test("3.2 — cliquer sur un article ouvre sa page détail", async ({ page }) => {
    await page.goto("/blog")
    const firstArticle = page.locator("article").first()
    const firstLink = firstArticle.locator("a").first()
    await firstLink.click()
    // Attendre la navigation hors de /blog
    await page.waitForURL((url) => !url.pathname.endsWith("/blog"))
    await expect(page.locator("h1")).toBeVisible()
  })

  test("3.3 / 3.4 — aucune erreur React key lors du rendu du blog et de la TOC", async ({
    page,
  }) => {
    const consoleErrors: string[] = []
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text())
    })
    await page.goto("/blog")
    await page.waitForLoadState("networkidle")

    const firstLink = page.locator("article a").first()
    if (await firstLink.isVisible().catch(() => false)) {
      await firstLink.click()
      await page.waitForLoadState("networkidle")
    }

    const keyErrors = consoleErrors.filter((e) =>
      /unique "key"/i.test(e)
    )
    expect(keyErrors, keyErrors.join("\n")).toEqual([])
  })
})
