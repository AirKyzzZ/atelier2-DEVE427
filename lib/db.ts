import { PrismaClient } from "@prisma/client"

const globalWithPrisma = global as typeof globalThis & {
  cachedPrisma: PrismaClient
}

let prisma: PrismaClient
if (process.env.NODE_ENV === "production") {
  prisma = new PrismaClient()
} else {
  if (!globalWithPrisma.cachedPrisma) {
    globalWithPrisma.cachedPrisma = new PrismaClient()
  }
  prisma = globalWithPrisma.cachedPrisma
}

export const db = prisma
