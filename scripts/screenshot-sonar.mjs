import { chromium } from "@playwright/test"

const BASE = process.env.SONAR_URL ?? "http://localhost:9000"
const USER = process.env.SONAR_USER ?? "admin"
const PASS = process.env.SONAR_PASS ?? "admin123!"
const OUT = process.env.SONAR_OUT ?? "docs/sonarqube-dashboard.png"

const browser = await chromium.launch()
const ctx = await browser.newContext({
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 2,
})
const page = await ctx.newPage()

console.log("Login…")
await page.goto(`${BASE}/sessions/new`)
await page.fill('input[name="login"]', USER)
await page.fill('input[name="password"]', PASS)
await page.click('button[type="submit"]')
await page.waitForURL((u) => !u.pathname.startsWith("/sessions/"), {
  timeout: 15000,
})

console.log("Open dashboard…")
await page.goto(`${BASE}/dashboard?id=taxonomy`, { waitUntil: "networkidle" })
// Let Sonar widgets settle
await page.waitForTimeout(2500)

console.log(`Save → ${OUT}`)
await page.screenshot({ path: OUT, fullPage: true })

await browser.close()
console.log("done")
