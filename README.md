# Taxonomy — DEVE427 Atelier 2

**Cours:** DEVE427 - Développement d'applications & TMA  
**Auteur:** Maxime Mansiet  
**GitHub:** https://github.com/AirKyzzZ/atelier2-DEVE427  
**Jira:** https://m4xxime.atlassian.net/jira/software/projects/KAN/boards/1

---

## Étape 1 — Workflow Jira personnalisé

Le projet Jira "Cours TMA" (KAN) a été configuré avec un workflow personnalisé incluant une étape de validation intermédiaire.

**Statuts du workflow :**
- À faire → En cours → **En validation** → Terminé

**Contraintes de transitions :** seul le responsable qualité peut valider un ticket (transition vers "Terminé" bloquée sans passer par "En validation").

> **Screenshot du workflow Jira :**  
> *(Ajouter ici une capture d'écran du workflow depuis Jira > Paramètres du projet > Workflow)*

---

## Étape 2 — Analyse SonarQube

SonarQube LTS 9.9 déployé localement via Docker sur `localhost:9000`.

**Résultats de l'analyse (shadcn/ui taxonomy) :**

| Sévérité | Règle | Nb | Description |
|----------|-------|----|-------------|
| CRITICAL | S3504 | 1 | `var` déclaration globale |
| MAJOR | S905 | 4 | Expression sans effet (return manquant) |
| MAJOR | S6479 | 6 | Clé React basée sur l'index du tableau |
| MAJOR | S6478 | 2 | Composants définis dans la fonction de rendu |
| MINOR | S1128 | 7 | Imports inutilisés |
| MINOR | S4325 | 1 | Assertion de type inutile |
| INFO | S1135 | 4 | Commentaires TODO |
| **Total** | | **25** | |

> **Screenshot SonarQube :**  
> *(Ajouter ici une capture du dashboard SonarQube)*

---

## Étape 3 — Tickets Jira & corrections

20 tickets créés dans Jira (KAN-4 à KAN-23), assignés à Maxime Mansiet (KAN-4→KAN-13) et Mael Bourdin (KAN-14→KAN-23).

Chaque fix est commité avec la référence du ticket :

```
fix(KAN-4): replace var with const via globalThis cast in db.ts
fix(KAN-5,KAN-6,KAN-7,KAN-8,KAN-9): replace array index keys with stable identifiers
fix(KAN-10): move IconLeft/IconRight out of Calendar render function
fix(KAN-11,KAN-12,KAN-13,KAN-14): add missing return statement in getXFromParams
fix(KAN-15): remove unnecessary type assertion in route.ts
fix(KAN-16,KAN-20,KAN-21,KAN-22): resolve TODO comments
fix(KAN-17,...,KAN-23): remove unused imports
```

---

# Taxonomy

An open source application built using the new router, server components and everything new in Next.js 13.

> **Warning**
> This app is a work in progress. I'm building this in public. You can follow the progress on Twitter [@shadcn](https://twitter.com/shadcn).
> See the roadmap below.

## About this project

This project as an experiment to see how a modern app (with features like authentication, subscriptions, API routes, static pages for docs ...etc) would work in Next.js 13 and server components.

**This is not a starter template.**

A few people have asked me to turn this into a starter. I think we could do that once the new features are out of beta.

## Note on Performance

> **Warning**
> This app is using the unstable releases for Next.js 13 and React 18. The new router and app dir is still in beta and not production-ready.
> **Expect some performance hits when testing the dashboard**.
> If you see something broken, you can ping me [@shadcn](https://twitter.com/shadcn).

## Features

- New `/app` dir,
- Routing, Layouts, Nested Layouts and Layout Groups
- Data Fetching, Caching and Mutation
- Loading UI
- Route handlers
- Metadata files
- Server and Client Components
- API Routes and Middlewares
- Authentication using **NextAuth.js**
- ORM using **Prisma**
- Database on **PlanetScale**
- UI Components built using **Radix UI**
- Documentation and blog using **MDX** and **Contentlayer**
- Subscriptions using **Stripe**
- Styled using **Tailwind CSS**
- Validations using **Zod**
- Written in **TypeScript**

## Roadmap

- [x] ~Add MDX support for basic pages~
- [x] ~Build marketing pages~
- [x] ~Subscriptions using Stripe~
- [x] ~Responsive styles~
- [x] ~Add OG image for blog using @vercel/og~
- [x] Dark mode

## Known Issues

A list of things not working right now:

1. ~GitHub authentication (use email)~
2. ~[Prisma: Error: ENOENT: no such file or directory, open '/var/task/.next/server/chunks/schema.prisma'](https://github.com/prisma/prisma/issues/16117)~
3. ~[Next.js 13: Client side navigation does not update head](https://github.com/vercel/next.js/issues/42414)~
4. [Cannot use opengraph-image.tsx inside catch-all routes](https://github.com/vercel/next.js/issues/48162)

## Why not tRPC, Turborepo or X?

I might add this later. For now, I want to see how far we can get using Next.js only.

If you have some suggestions, feel free to create an issue.

## Running Locally

1. Install dependencies using pnpm:

```sh
pnpm install
```

2. Copy `.env.example` to `.env.local` and update the variables.

```sh
cp .env.example .env.local
```

3. Start the development server:

```sh
pnpm dev
```

## License

Licensed under the [MIT license](https://github.com/shadcn/taxonomy/blob/main/LICENSE.md).
