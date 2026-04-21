# Plan de Test — DEVE427 Atelier 3

Ce document recense les cas de tests critiques pour le fork `AirKyzzZ/atelier2-DEVE427`.
La dernière colonne indique le spec Playwright qui automatise le cas, et la colonne « NR » marque les tests de non-régression liés aux tickets Jira corrigés à l'Atelier 2.

Légende :

- **Type** : U = cas usuel · X = cas extrême · E = cas d'erreur
- **NR** : ticket KAN couvert (non-régression). Vide = test d'acceptation pur.

---

## 1. Accueil / Marketing

| # | Fonctionnalité | Type | Scénario | Résultat attendu | NR | Spec |
|---|---|---|---|---|---|---|
| 1.1 | Chargement homepage | U | `GET /` | 200, `h1` « An example app built using Next.js 13 server components. » visible | — | `home.spec.ts` |
| 1.2 | CTA « Get Started » | U | Clic sur « Get Started » depuis l'accueil | Redirige vers `/login` | — | `home.spec.ts` |
| 1.3 | Section Features ancrée | U | Scroll jusqu'à `#features`, vérifier `h2` « Features » | Section visible, ancre `/#features` cliquable | — | `home.spec.ts` |
| 1.4 | Section Open Source | U | Vérifier présence `h2` « Proudly Open Source » | Section visible | — | `home.spec.ts` |
| 1.5 | Page Pricing | U | `GET /pricing` | `h2` « Simple, transparent pricing » visible, prix `$19` | — | `home.spec.ts` |
| 1.6 | Route inexistante | E | `GET /page-qui-nexiste-pas` | 404 Next.js | — | `home.spec.ts` |

## 2. Navigation (MainNav, MobileNav, SidebarNav)

| # | Fonctionnalité | Type | Scénario | Résultat attendu | NR | Spec |
|---|---|---|---|---|---|---|
| 2.1 | Nav desktop visible | U | Viewport ≥ md, vérifier les 4 entrées (Features, Pricing, Blog, Documentation) | 4 liens rendus, `href` distincts, pas de doublon | KAN-5, KAN-10 | `navigation.spec.ts` |
| 2.2 | Clé de liste stable | U | Après reclic sur un même lien, aucun warning console React « key » | Pas d'erreur console Array key | KAN-5, KAN-6, KAN-7, KAN-9, KAN-10 | `navigation.spec.ts` |
| 2.3 | Nav mobile fermée par défaut | U | Viewport Pixel 7, vérifier menu fermé | Le panneau mobile n'est pas visible | KAN-9 | `responsive.spec.ts` |
| 2.4 | Ouverture nav mobile | U | Tap sur le bouton « Menu » | Panneau mobile apparaît avec les 4 liens | KAN-9 | `responsive.spec.ts` |
| 2.5 | Navigation vers Blog depuis mobile | U | Tap sur « Blog » depuis la mobile nav | Redirige vers `/blog` | KAN-9 | `responsive.spec.ts` |
| 2.6 | Navigation rapide répétée | X | Naviguer rapidement entre 5 pages successives | Aucune erreur hydration, pas de blanc d'écran | KAN-5..10 | `navigation.spec.ts` |

## 3. Blog (Contentlayer / MDX / TOC)

| # | Fonctionnalité | Type | Scénario | Résultat attendu | NR | Spec |
|---|---|---|---|---|---|---|
| 3.1 | Index du blog | U | `GET /blog` | `h1` « Blog », au moins 1 article listé | — | `blog.spec.ts` |
| 3.2 | Lien vers article | U | Clic sur le premier article | URL correspond au slug de l'article, titre en `h1` | — | `blog.spec.ts` |
| 3.3 | Table des matières (TOC) | U | Sur un article, vérifier la présence d'une TOC à droite | TOC rendue avec les ancres des `h2`/`h3` | KAN-8 | `blog.spec.ts` |
| 3.4 | Clé stable dans TOC | U | Inspecter `aside` / `nav` TOC | Pas d'erreur console React key | KAN-8 | `blog.spec.ts` |

## 4. Documentation & pages MDX statiques

| # | Fonctionnalité | Type | Scénario | Résultat attendu | NR | Spec |
|---|---|---|---|---|---|---|
| 4.1 | Page Guides | U | `GET /guides` | Liste des guides rendue sans erreur | KAN-13, KAN-21, KAN-22, KAN-23 | `docs.spec.ts` |
| 4.2 | Page Terms | U | `GET /terms` | Contenu MDX rendu (h1 visible) | KAN-14, KAN-15 | `docs.spec.ts` |
| 4.3 | Page Privacy | U | `GET /privacy` | Contenu MDX rendu | KAN-14, KAN-15 | `docs.spec.ts` |
| 4.4 | Sidebar docs stable | U | Ouvrir `/guides`, recharger plusieurs fois | Sidebar nav rendue identique, pas d'erreur key | KAN-6, KAN-7 | `docs.spec.ts` |

## 5. Auth (pages publiques)

| # | Fonctionnalité | Type | Scénario | Résultat attendu | NR | Spec |
|---|---|---|---|---|---|---|
| 5.1 | Page Login | U | `GET /login` | Formulaire email + bouton visible | — | `home.spec.ts` |
| 5.2 | Page Register | U | `GET /register` | Formulaire visible | — | `home.spec.ts` |

---

## Synthèse non-régression

| Ticket | Scénario couvert | Spec |
|---|---|---|
| KAN-4 (var db.ts) | Non couvert par un test UI direct (code côté serveur). Couvert indirectement par le boot de l'app lors de chaque spec (le serveur crashait si `var` global mal initialisée) | toutes |
| KAN-5 | Nav desktop sans warning key | `navigation.spec.ts` |
| KAN-6, KAN-7 | Sidebar docs sans warning key | `docs.spec.ts` |
| KAN-8 | TOC blog sans warning key | `blog.spec.ts` |
| KAN-9 | Mobile nav sans warning key | `responsive.spec.ts` |
| KAN-10 | Main nav sans warning key | `navigation.spec.ts` |
| KAN-11, KAN-12 | Composant `calendar` défini hors render (app ne crash plus) | indirectement : boot de l'app |
| KAN-13 | Imports inutilisés retirés dans `page.tsx` (dashboard) — la page se rend toujours | `docs.spec.ts` (rendering générique) |
| KAN-14, KAN-15 | Imports inutilisés retirés dans `layout.tsx` / `loading.tsx` — rendu inchangé | `docs.spec.ts` (MDX pages) |
| KAN-16 | Assertion de type inutile retirée dans `route.ts` (auth) — la page login s'affiche | `home.spec.ts` (Login) |
| KAN-17..20 | TODO résolus, pages rendues normalement | couvert par boot + rendering |
| KAN-21, KAN-22, KAN-23 | `return` manquants corrigés dans `page.tsx` — pas de page blanche | `docs.spec.ts` + `home.spec.ts` |

## Exécution

```sh
# headless (par défaut)
pnpm exec playwright test

# mode UI interactif
pnpm exec playwright test --ui

# rapport HTML (ouvert dans le navigateur)
pnpm exec playwright show-report
```

Le rapport est généré sous `playwright-report/` (ignoré par Git, cf. `.gitignore`).
