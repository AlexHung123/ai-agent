// import { PrismaClient } from '@prisma/client';
// import { PrismaPg } from '@prisma/adapter-pg';

// // Use environment variable for connection string, with fallback to default
// const connectionString = process.env.LIMESURVEY_DATABASE_URL || 
//   "postgresql://postgres:pass1234@192.168.1.170:5432/limesurveydb?schema=public";

// const adapter = new PrismaPg({ connectionString });

// declare global {
//   // eslint-disable-next-line no-var
//   var __prisma: PrismaClient | undefined;
// }

// export const prisma =
//   global.__prisma ??
//   new PrismaClient({
//     adapter,
//     log: ['error'],
//   });

// if (process.env.NODE_ENV !== 'production') global.__prisma = prisma;

// src/lib/postgres/db.ts

import { PrismaClient } from '@/generated/prisma'
import { PrismaPg } from '@prisma/adapter-pg'

const connectionString = 'postgresql://postgres:pass1234@192.168.56.150:5432/limesurveydb'

const adapter = new PrismaPg({ connectionString })

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined
}

export const prisma =
  global.__prisma ??
  new PrismaClient({
    adapter,
    log: ['error'],
  })

if (process.env.NODE_ENV !== 'production') {
  global.__prisma = prisma
}
