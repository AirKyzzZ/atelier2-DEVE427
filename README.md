# Taxonomy — DEVE427 TMA

[![CI](https://github.com/AirKyzzZ/atelier2-DEVE427/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AirKyzzZ/atelier2-DEVE427/actions/workflows/ci.yml)

**Cours:** DEVE427 — Développement d'applications & Tierce Maintenance Applicative
**Fork:** https://github.com/AirKyzzZ/atelier2-DEVE427
**Upstream:** https://github.com/shadcn-ui/taxonomy
**Jira:** https://m4xxime.atlassian.net/jira/software/projects/KAN/boards/1

---

## Atelier 1 — Choix du projet & périmètre de maintenance

### Projet choisi

`shadcn-ui/taxonomy` — application Next.js 13 (App Router, Server Components, MDX via Contentlayer, NextAuth, Prisma, Stripe). Le projet coche tous les critères imposés :

| Critère | Statut |
|---|---|
| Open source (MIT) | OK |
| Application web + API routes | OK |
| Exécutable localement (`pnpm dev`) | OK |
| Tests fonctionnels (quasi) inexistants | OK — aucun test avant ce fork |
| Inactif / faible activité | OK — dernière activité significative > 18 mois |
| Plusieurs dizaines de fichiers sources | OK — 15 dossiers métier, 100+ composants |
| Centaines de commits | OK — historique Git riche |

### Mission du fork

Après exploration du dépôt original (sources, issues ouvertes, PRs en suspens), le fork se donne pour périmètre de maintenance :

| Axe | Engagements du fork |
|---|---|
| **Stabilité** | Corriger les `var` globaux et expressions sans effet (page.tsx) qui provoquent des comportements non déterministes. Rendre `NEXTAUTH_URL` optionnel pour éviter les crashs en preview Vercel. |
| **Performance** | Supprimer les composants définis en plein render (`calendar.tsx`), remplacer les `key={index}` React par des identifiants stables dans toutes les nav (main/sidebar/mobile/toc). |
| **Sécurité** | Lever les TODO de `subscription.ts`, `route.ts`, `post.ts` qui trahissaient des contrôles manquants. Faire passer la gestion d'env vars par `@t3-oss/env-nextjs` pour valider les secrets au build. |
| **Ergonomie & accessibilité** | Assurer la non-régression des parcours nav (desktop + mobile) via tests Playwright (Atelier 3). |
| **Anomalies (bugs)** | Retours manquants dans `getXFromParams` (route handlers), assertion de type inutile dans `route.ts`, imports inutilisés (bruit). |
| **Fonctionnalités manquantes** | Mise en place d'une chaîne de qualité (SonarQube + Jira + Playwright) là où il n'existait rien. |

Ce périmètre évoluera si de nouvelles issues sont remontées par SonarQube ou par les tests de non-régression.

### Équipe et rôles MOE

| Initiales | Membre | Rôle MOE | Responsabilités |
|---|---|---|---|
| **MM** | Maxime Mansiet | Chef de projet / Tech Lead | Architecture, revue de code, suivi qualité, transitions Jira, fixes critiques (var global, calendar) et bugs `page.tsx` |
| **GL** | Grégoire Lefèvre | Développeur / Responsable refactoring & performance | Refactoring du cluster navigation (`key={index}` → ids stables) sur tous les composants nav (main/sidebar/mobile/toc) + nettoyage des imports dans `page.tsx` |
| **MB** | Mael Bourdin | Développeur / Responsable qualité & sécurité | Suppression des imports inutilisés (`layout.tsx`, `loading.tsx`), résolution des `TODO` à enjeu sécurité (`subscription.ts`, `route.ts`, `post.ts`), retrait d'assertion superflue, exécution SonarQube et validation des tickets |

Répartition des 20 tickets SonarQube (Atelier 2) — équilibrée 6 / 7 / 7 :

- **MM** (6 tickets) : KAN-4, KAN-11, KAN-12, KAN-21, KAN-22, KAN-23 — Critical / High (var, composants render, expressions sans effet)
- **GL** (7 tickets) : KAN-5, KAN-6, KAN-7, KAN-8, KAN-9, KAN-10, KAN-13 — Major / Minor (`key={index}` performance + imports)
- **MB** (7 tickets) : KAN-14, KAN-15, KAN-16, KAN-17, KAN-18, KAN-19, KAN-20 — Minor / Info (imports, assertion, TODO)

La validation par un pair (étape `En cours de revue`) tourne en triangle : MM → GL → MB → MM, ce qui garantit que personne ne valide ses propres fixes.

Le README est historisé (voir `git log -- README.md`).

---

## Atelier 2 — Outils de suivi

### Étape 1 — Workflow Jira personnalisé

Projet Jira de type Kanban **KAN — Cours TMA** (https://m4xxime.atlassian.net/jira/software/projects/KAN/boards/1).

Le workflow a été personnalisé pour intégrer une **étape de validation obligatoire** par un autre membre de l'équipe que l'assigné, et pour **contraindre les transitions** (pas de saut direct de `En cours` vers `Terminé`).

**Statuts :**

```
À faire  ──▶  En cours  ──▶  En cours de revue  ──▶  Terminé
   ▲              │                     │
   └──────────────┴─────────────────────┘  (retour possible en arrière)
```

- La transition `En cours → Terminé` est désactivée : il faut passer par `En cours de revue`.
- `En cours de revue` matérialise la validation par un pair : le responsable qualité (MB) valide les fixes de MM et vice-versa.

**Screenshot du workflow Jira** (vue Board, les 20 tickets sont en `Terminé` après validation dans `En cours de revue`) :

![Jira workflow board](./docs/jira-workflow.png)

**Automatisation — transition déclenchée par le commit.** Mael Bourdin a ajouté une règle Jira Automation qui lit les commits liés au ticket et transitionne automatiquement le ticket de `À faire` vers `En cours` dès qu'un premier commit apparaît. Elle évite l'oubli de transition manuelle lors d'un `fix(KAN-X):…` et garantit que le board reflète l'état réel du dépôt.

- **Trigger** : `Commit created` (événement remonté par l'intégration Git).
- **Condition** : `Status equals "À faire"` (pas de bruit sur les tickets déjà en cours ou en revue).
- **Action** : `Transition the work item to "En cours"`.
- **Owner / Actor** : MB / `Automation for Jira`.

![Jira automation — Commit created → En cours](./docs/jira-automation-commit.png)

### Étape 2 — Analyse SonarQube

SonarQube LTS 9.9 a été déployé localement via Docker (`localhost:9000`) sur le poste de MM. Le projet a été importé via `sonar-scanner` (configuration dans `.scannerwork/`).

**Résultats de l'analyse — 25 issues détectées, regroupées en 20 tickets Jira** (certaines règles concentrent plusieurs lignes dans un même fichier, traitées en un seul ticket) :

| Sévérité | Règle Sonar | Nb issues | Nb tickets | Description |
|----------|-------|----|----|-------------|
| CRITICAL | S3504 | 1 | 1 | `var` global (db.ts) |
| MAJOR | S6479 | 6 | 6 | `key={index}` dans les listes React (nav, sidebar, toc, mobile, main) |
| MAJOR | S6478 | 2 | 2 | Composant défini pendant le render (calendar) |
| MAJOR | S905 | 3 | 3 | Expressions sans effet / return manquant (page.tsx) |
| MINOR | S1128 | 7 | 3 | Imports inutilisés (page.tsx regroupe 5 imports, layout.tsx et loading.tsx en ont 1 chacun) |
| MINOR | S4325 | 1 | 1 | Assertion de type superflue (route.ts) |
| INFO | S1135 | 4 | 4 | Commentaires `TODO` non résolus |
| **Total** | | **24** | **20** | |

**Note d'écart :** le rapport SonarQube liste 24 issues individuelles → 20 tickets Jira. L'écart provient de la règle S1128 (imports inutilisés) qui a été traitée en un ticket par fichier impacté plutôt qu'en un ticket par import, car un seul commit supprime tous les imports concernés d'un même fichier.

**Screenshot SonarQube — dashboard post-correction** (Quality Gate `Passed`, toutes les issues des 20 tickets KAN-4..23 ont été résolues) :

![SonarQube dashboard](./docs/sonarqube-dashboard.png)

> La capture montre l'état du projet **après** les commits `fix(KAN-X)`. L'analyse initiale (avant fixes) avait remonté les 24 issues listées dans le tableau ci-dessus ; ces issues sont ce qui a servi à créer les tickets Jira. La suite de scripts pour reproduire le scan est dans `scripts/screenshot-sonar.mjs`.

### Étape 3 — Tickets Jira & corrections

Les 20 tickets KAN-4 → KAN-23 ont été créés dans Jira, parcourus dans le workflow (`À faire → En cours → En cours de revue → Terminé`) et chaque fix a été commité avec la référence du ticket dans le message :

```text
fix(KAN-4): replace var with const via globalThis cast in db.ts
fix(KAN-5,KAN-6,KAN-7,KAN-8,KAN-9): replace array index keys with stable identifiers
fix(KAN-10): move IconLeft/IconRight out of Calendar render function
fix(KAN-11,KAN-12,KAN-13,KAN-14): add missing return statement in getXFromParams
fix(KAN-15): remove unnecessary type assertion in route.ts
fix(KAN-16,KAN-20,KAN-21,KAN-22): resolve TODO comments (SonarQube S1135)
fix(KAN-17,KAN-18,KAN-19,KAN-20,KAN-21,KAN-22,KAN-23): remove unused imports
```

Tous les tickets sont en statut `Terminé` à la date de la remise.

---

## Atelier 3 — Tests fonctionnels & non-régression

Le plan de test complet est décrit dans [`TESTS.md`](./TESTS.md) (cas usuels, extrêmes, erreur et identification explicite des cas de non-régression liés aux tickets KAN).

### Stack de test

- **Playwright** (`@playwright/test`) configuré via `playwright.config.ts`.
- Exécution locale contre `http://localhost:3000` (le dev server peut être démarré automatiquement par Playwright via l'option `webServer`).
- Rapport HTML généré sous `playwright-report/` (ignoré par Git).

### Lancer les tests

```sh
# 1. Démarrer l'app (dans un terminal)
pnpm dev

# 2. Lancer la suite (dans un autre terminal)
pnpm exec playwright test                 # headless par défaut
pnpm exec playwright test --ui            # mode UI interactif
pnpm exec playwright show-report          # ouvrir le dernier rapport HTML
```

### Organisation des specs

```
tests/
├── home.spec.ts            # Cas usuels : accueil, nav desktop
├── navigation.spec.ts      # Non-régression KAN-5..10 (keys stables dans nav)
├── blog.spec.ts            # Non-régression KAN-8 (toc) + cas usuel contenu MDX
├── docs.spec.ts            # Non-régression KAN-13..15 (imports), KAN-21..23 (rendering)
└── responsive.spec.ts      # Cas usuel mobile + non-régression mobile-nav (KAN-9)
```

---

## CI/CD — GitHub Actions

Toute la chaîne qualité a été câblée dans `.github/workflows/ci.yml`. Le workflow se déclenche sur chaque `push` vers `main` et sur chaque pull request, avec aussi un déclencheur manuel (`workflow_dispatch`).

| Job | Outil | Rôle |
|---|---|---|
| **lint** | `next lint` (ESLint) | Style + règles React/Next.js |
| **typecheck** | `tsc --noEmit` | Vérifie les types sans émettre de JS |
| **build** | `pnpm build` (contentlayer + next build) | Garantit que la prod buildable |
| **playwright** | `playwright test` (chromium desktop + Pixel 7) | Atelier 3 — exécute les 5 specs e2e contre une instance MySQL Docker |
| **sonarqube** | SonarQube LTS Community en service container | Atelier 2 — scan + Quality Gate, fait échouer le job si la QG est rouge |

`lint` + `typecheck` tournent en parallèle et gates `build` / `playwright` / `sonarqube` (les jobs lourds n'attendent pas `build`, ils s'exécutent en parallèle).

**Variables d'environnement** : le workflow injecte des valeurs CI factices (mais valides pour la validation Zod de `@t3-oss/env-nextjs`) directement via le bloc `env:`. Pour brancher de vraies clefs, il suffit de définir les secrets GitHub homonymes ; l'expression `${{ secrets.X || 'default' }}` les pickup automatiquement.

**Reproductibilité locale** : tout est lançable à la main : `pnpm lint`, `pnpm typecheck`, `pnpm build`, `pnpm test:e2e`, et `sonar-scanner` une fois SonarQube démarré localement (`docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community`).

---

## Atelier 4 — Sécurité (STRIDE + Semgrep)

### Étape 1 — Modélisation des menaces (STRIDE)

Le schéma d'architecture (`presentation/assets/architecture-taxonomy.excalidraw`, exporté en PNG sous `docs/architecture-taxonomy.png`) découpe le système en 4 zones séparées par 3 frontières de confiance, chacune analysée ci-dessous selon les 6 catégories STRIDE (**S**poofing / **T**ampering / **R**epudiation / **I**nformation Disclosure / **D**enial of Service / **E**levation of Privilege).

![Schéma d'architecture taxonomy avec frontières de confiance](./docs/architecture-taxonomy.png)

#### Frontière 1 — Navigateur ↔ Serveur Next.js

Toute requête entre depuis un client non contrôlé : pages publiques (`/dashboard`, `/editor`, `/login`), routes API (`/api/posts`, `/api/users/*`, `/api/auth/*`), webhooks. Le seul garde-fou applicatif est `middleware.ts` et les `getServerSession` côté route.

| STRIDE | Menace | Vecteur / fichier | Mitigation actuelle | À faire |
|---|---|---|---|---|
| **S**poofing | Vol / rejeu du JWT NextAuth | Cookie capté via XSS ou MITM ; `middleware.ts:7` fait confiance au token sans binding IP/UA | Secret signé serveur (`NEXTAUTH_SECRET`), JWT strategy (`lib/auth.ts:19`) | Cookies `Secure` + `SameSite=Strict`, CSP, HSTS |
| **T**ampering | XSS stocké via blocs EditorJS forgés | `lib/validations/post.ts:7` : `content: z.any()` accepte n'importe quoi | Validation titre + auth + ownership (`route.ts:83-93`) | Schéma strict des blocs EditorJS, sanitisation côté serveur (DOMPurify), CSP `default-src 'self'` |
| **R**epudiation | Suppression de post non auditée | `DELETE /api/posts/[postId]` (`route.ts:14-42`) sans audit log | Timestamp `updatedAt` (`schema.prisma:80`) | Table `AuditLog (userId, action, resourceId, ip, ua, ts)` |
| **I**nfo Disclosure | Énumération d'utilisateurs via timing magic link | `lib/auth.ts:32-43` choisit un template Postmark différent selon `emailVerified` → temps de réponse différent | Validation Zod du format | Latence unifiée + message UI neutre |
| **D**oS | Saturation des routes API non protégées | `middleware.ts:45` matche seulement `/dashboard`, `/editor`, `/login`, `/register` — `/api/*` **hors périmètre** | Auth requise sur la plupart des routes | Rate limiting (Upstash, `@vercel/rate-limit`), quota IP + userId, timeout `/api/og` |
| **E**oP | Bypass quota freemium via TOCTOU | `app/api/posts/route.ts:54-63` : `db.post.count` puis `db.post.create` non transactionnel → 2 requêtes concurrentes = 4 posts | Vérification applicative + plan via Stripe | `db.$transaction` avec `count` + `create` atomiques, ou contrainte DB |

**Top 3 priorités F1** : (1) rate limiting global sur `/api/*`, (2) sanitisation du contenu des posts, (3) headers CSP + cookies durcis.

#### Frontière 2 — Serveur Next.js ↔ Base de données

Toutes les requêtes DB transitent par le singleton Prisma (`lib/db.ts:7-15`). Isole la logique applicative du stockage : `accounts`, `sessions`, `users`, `posts`, et colonnes Stripe dénormalisées.

| STRIDE | Menace | Vecteur / fichier | Mitigation actuelle | À faire |
|---|---|---|---|---|
| **S**poofing | `DATABASE_URL` exposé en clair | Leak via log, `.env` commité, dump Vercel = accès total | `env.mjs:13` valide la présence, `.gitignore` exclut `.env*` | Rotation, secret manager, rôle Postgres lecture seule pour tâches annexes |
| **T**ampering | Régression silencieuse sur `isPro` | `lib/subscription.ts:1` : `// @ts-nocheck` désactive TypeScript ; calcul `isPro` peut renvoyer `undefined` au lieu de `false` | Test e2e Playwright sur le flux | Retirer `@ts-nocheck`, aligner les types `UserSubscriptionPlan` |
| **R**epudiation | Aucune trace des updates `users.stripe*` | Webhook fait `db.user.update` (`webhooks/stripe/route.ts:35-47, 57-67`) sans journal | Contraintes d'unicité (`stripeCustomerId @unique`) | Table `SubscriptionEvent` append-only miroir des events Stripe (utile aussi pour idempotence) |
| **I**nfo Disclosure | Élargissement des champs renvoyés | Plusieurs routes ont un `select` explicite (bon), pas toutes | `select` explicite sur `GET /api/posts` | Linter ou code review qui exige `select` partout |
| **D**oS | Amplification DB via callback JWT | `lib/auth.ts:83-103` : `db.user.findFirst` à **chaque** requête authentifiée | Pool Prisma par défaut | Cache (Redis/LRU) ou claims dans le JWT au login |
| **E**oP | Bypass d'ownership si `authorId === undefined` | `app/api/posts/[postId]/route.ts:83-93` count où `authorId = session.user.id` ; si `session?.user.id === undefined` la garde tombe | Vérification ownership explicite | Garde `if (!session?.user?.id) return 401`, `authorId` non-nullable au schéma |

**Top 3 priorités F2** : (1) retirer `@ts-nocheck` de `lib/subscription.ts`, (2) mémoïser le lookup JWT, (3) journal d'audit `SubscriptionEvent`.

#### Frontière 3 — Serveur Next.js ↔ Services externes

Trois intégrations : **GitHub OAuth** (provider NextAuth), **Stripe** (checkout sortant + webhook entrant), **Postmark** (magic link + activation). Secrets dans `env.mjs:11-20`.

| STRIDE | Menace | Vecteur / fichier | Mitigation actuelle | À faire |
|---|---|---|---|---|
| **S**poofing | Faux webhook Stripe / replay | Forge de payload sur `/api/webhooks/stripe` | `stripe.webhooks.constructEvent` (`webhooks/stripe/route.ts:14-22`) vérifie la signature HMAC | Idempotence : stocker les `event.id` reçus pour rejeter les doublons |
| **T**ampering | Manipulation de `metadata.userId` au checkout | `webhooks/stripe/route.ts:37` met à jour le user via `metadata.userId` sans recroiser `stripeCustomerId` | `metadata` posée serveur-side au moment du checkout | Croiser : `where: { id: metadata.userId, stripeCustomerId: subscription.customer }` |
| **R**epudiation | Aucune trace des events Stripe traités | `route.ts:26-68` n'effectue que l'effet de bord | Logs Vercel éphémères | Table `StripeWebhookEvent(id, type, payload, received_at, processed_at)` |
| **I**nfo Disclosure | OAuth tokens GitHub stockés en clair | `schema.prisma:19-24` : `access_token`, `refresh_token`, `id_token` en clair | Scope minimal, `GITHUB_ACCESS_TOKEN` serveur séparé | Chiffrement applicatif des colonnes `*_token`, ou rotation |
| **D**oS | Épuisement quota Postmark / facture Stripe | `users/stripe/route.ts:35-51` crée une `checkout.session` sans rate limit ; même chose pour magic link (`auth.ts:48`) | Auth requise | Rate limit par userId (5/h sur Stripe, 3/h sur magic link) |
| **E**oP | Compte takeover via host header injection | `NEXTAUTH_URL` est `optional` (`env.mjs:8`) → en prod, NextAuth peut générer le magic link sur le mauvais domaine | Validation Zod du format | Rendre `NEXTAUTH_URL` obligatoire en prod, durée de vie courte du `VerificationToken` |

**Top 3 priorités F3** : (1) idempotence + double-check user sur le webhook Stripe, (2) rate limit sur `/api/users/stripe` et magic link, (3) `NEXTAUTH_URL` obligatoire en prod.

#### Synthèse STRIDE

Deux menaces se retrouvent sur plusieurs frontières et devraient être traitées en priorité au niveau application :

1. **Absence totale de rate limiting** (`middleware.ts:45` ne couvre pas `/api`) — impact DoS sur F1, amplification DB sur F2, coût tiers sur F3.
2. **Absence d'audit log** — répudiation possible sur les trois frontières (posts, users, subscriptions).

Les autres correctifs sont locaux et identifiés par fichier/ligne ci-dessus.

### Étape 2 — Analyse Semgrep

Le scan utilise un **ruleset custom** (`semgrep.yml` à la racine) qui cible exactement les classes de menaces identifiées par STRIDE plutôt que l'ensemble générique des règles publiques. Reproduction : `./scripts/run-semgrep.sh`.

Choix pédagogique : le registre public Semgrep nécessite un compte gratuit pour télécharger `p/owasp-top-ten` et consorts. Les règles custom sont rejouables hors-ligne et chaque match correspond 1:1 à un ticket Jira, ce qui rend la chaîne traçable.

| Sévérité | Règle Semgrep | Fichier:ligne | STRIDE | Ticket | Assigné |
|---|---|---|---|---|---|
| **CRITICAL** | `tma-validation-uses-z-any` | `lib/validations/post.ts:7` | Tampering · CWE-79 | [KAN-25](https://m4xxime.atlassian.net/browse/KAN-25) | MM |
| **MAJOR** | `tma-ts-nocheck-disables-types` | `lib/subscription.ts:1` | Tampering + EoP · CWE-1287 | [KAN-26](https://m4xxime.atlassian.net/browse/KAN-26) | MB |
| **MAJOR** | `tma-ts-nocheck-disables-types` | `lib/toc.ts:1` | Tampering · CWE-1287 | [KAN-27](https://m4xxime.atlassian.net/browse/KAN-27) | MB |
| **MAJOR** | `tma-no-rate-limit-on-api-routes` | `middleware.ts:45` | DoS · CWE-770 | [KAN-28](https://m4xxime.atlassian.net/browse/KAN-28) | GL |
| **MINOR** | `tma-jwt-callback-hits-db-on-every-request` | `lib/auth.ts:84` | DoS · CWE-400 | [KAN-29](https://m4xxime.atlassian.net/browse/KAN-29) | GL |

**Priorisation** (selon le PDF Atelier 4, "injection SQL > code mort") : KAN-25 (XSS stocké) > KAN-28 (DoS, coût tiers) > KAN-26/27 (tampering / type safety) > KAN-29 (perf).

### Étape 3 — Consolidation

Les fixes correspondant aux findings Semgrep critiques sont commités avec la convention `fix(KAN-X):`. La suite Playwright (Atelier 3) est ré-exécutée après chaque fix pour garantir la non-régression. Statut courant : tickets en attente de prise en charge — voir le board Jira.

---

## Running Locally (upstream)

```sh
pnpm install
cp .env.example .env.local   # et compléter les variables
pnpm dev
```

## License

MIT — voir [LICENSE.md](./LICENSE.md). Projet upstream : [shadcn-ui/taxonomy](https://github.com/shadcn-ui/taxonomy).
