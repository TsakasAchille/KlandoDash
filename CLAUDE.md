# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KlandoDash is a dashboard application for Klando, a carpooling/ride-sharing service in Senegal. The project has migrated from Streamlit to Next.js with Supabase as the primary database.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui (active)
│   ├── src/app/      # Pages (App Router)
│   ├── src/components/
│   ├── src/lib/      # Supabase client + queries
│   └── src/types/    # TypeScript types
├── database/          # SQL schemas, migrations, queries
│   ├── schema.sql    # Full schema dump
│   ├── tables.md     # Tables documentation
│   ├── migrations/   # SQL migrations
│   └── tests/        # Query tests
├── src/               # Streamlit app (legacy - deprecated)
└── data/              # Local data cache (legacy)
```

## Commands

### Frontend (Next.js)
```bash
cd frontend
npm run dev      # Dev server on http://localhost:3000
npm run build    # Production build
npm run start    # Production server
```

### Database Tests
```bash
cd database/tests
SUPABASE_URL=xxx SUPABASE_SERVICE_ROLE_KEY=xxx node test.js
```

### Supabase CLI
```bash
npx supabase link --project-ref zzxeimcchndnrildeefl
npx supabase db push              # Push migrations
npx supabase db dump --schema public -f schema.sql
```

## Database (Supabase)

**Project:** `zzxeimcchndnrildeefl` (West EU - Paris)

### Main Tables
| Table | Description | PK | Rows |
|-------|-------------|-----|------|
| `users` | User profiles | `uid` | ~50 |
| `trips` | Trip listings | `trip_id` | 37 |
| `bookings` | Reservations | `id` | 21 |
| `chats` | Messages | `id` | - |
| `transactions` | Payments | `id` | - |
| `dash_authorized_users` | Utilisateurs autorisés dashboard | `email` | ~8 |

### Key Relations
```
users ──< trips (driver_id → uid)
users ──< bookings (user_id → uid)
trips ──< bookings (trip_id)
trips ──< chats (trip_id)
```

### Indexes (trips)
- `idx_trips_status` - Filter by status
- `idx_trips_departure_schedule` - Sort by date DESC
- `idx_trips_driver_id` - Join with users
- `idx_trips_status_departure` - Combined filter+sort
- `idx_trips_created_at` - Sort by creation DESC

### Query Best Practices
```typescript
// ❌ Avoid SELECT *
const { data } = await supabase.from("trips").select("*");

// ✅ Specific columns + indexes
const { data } = await supabase
  .from("trips")
  .select("trip_id, departure_name, destination_name, status, driver_id")
  .eq("status", "ACTIVE")
  .order("departure_schedule", { ascending: false })
  .limit(50);

// ✅ Joins with specific columns
const { data } = await supabase
  .from("trips")
  .select(`
    trip_id, departure_name, status,
    driver:users!fk_driver (display_name, rating)
  `)
  .limit(50);
```

## Frontend Architecture (Next.js 14)

### Structure
```
frontend/src/
├── app/
│   ├── layout.tsx          # Root layout + SessionProvider
│   ├── page.tsx            # Home
│   ├── login/              # Page de connexion
│   ├── trips/              # Trips page
│   ├── users/              # Users page
│   └── stats/              # Stats dashboard
├── components/
│   ├── sidebar.tsx         # Navigation + UserMenu
│   ├── user-menu.tsx       # Menu utilisateur (avatar, rôle, déconnexion)
│   ├── providers.tsx       # SessionProvider wrapper
│   ├── layout-content.tsx  # Layout conditionnel (avec/sans sidebar)
│   ├── ui/                 # Shadcn components
│   ├── trips/              # Trip components
│   └── users/              # User components
├── lib/
│   ├── auth.ts             # Configuration NextAuth.js
│   ├── supabase.ts         # Supabase clients
│   ├── queries/
│   │   ├── trips.ts        # Trip queries
│   │   ├── users.ts        # User queries
│   │   └── stats.ts        # Dashboard stats
│   └── utils.ts            # formatDate, formatPrice, cn
├── middleware.ts           # Protection des routes (redirect /login)
└── types/
    ├── trip.ts             # Trip types
    └── user.ts             # User types
```

### Data Flow
```
Server Component (page.tsx)
    │
    ├── getTripsWithDriver() ──► Supabase
    └── getTripsStats() ───────► Supabase
    │
    ▼ props
Client Component (trips-client.tsx)
    │
    ├── TripTable (selection state)
    └── TripDetails (display)
```

### Available Queries (`lib/queries/trips.ts`)
```typescript
getTrips(options)        // List with minimal columns
getTripById(tripId)      // Detail with driver join
getTripsStats()          // Aggregated stats
getTripsWithDriver(limit) // Enriched list with driver info
```

## Theme Colors (Klando)

| Name | Hex | CSS Variable | Usage |
|------|-----|--------------|-------|
| Gold | `#EBC33F` | `--klando-gold` | Primary accents, titles |
| Burgundy | `#7B1F2F` | `--klando-burgundy` | Selected states |
| Dark | `#081C36` | `--klando-dark` | Backgrounds |

## Authentication (NextAuth.js v5)

Le dashboard utilise NextAuth.js avec Google OAuth. Seuls les utilisateurs présents dans la table `dash_authorized_users` avec `active=true` peuvent accéder.

### Flux d'authentification
```
Utilisateur ──► / ──► middleware.ts ──► Non connecté? ──► /login
                                              │
                                        Connecté? ──► Accès autorisé
```

### Table `dash_authorized_users`
| Colonne | Type | Description |
|---------|------|-------------|
| `email` | varchar(255) | Email (PK) |
| `active` | boolean | Autorisation active |
| `role` | varchar(50) | `admin` ou `user` |
| `added_at` | timestamp | Date d'ajout |
| `added_by` | varchar(255) | Ajouté par |

### Fichiers clés
- `src/lib/auth.ts` - Configuration NextAuth + callbacks
- `src/middleware.ts` - Protection des routes
- `src/app/login/page.tsx` - Page de connexion
- `src/components/user-menu.tsx` - Menu utilisateur dans la sidebar

## Environment Variables

### Root `.env.local` (symlink vers frontend/)
```env
# Supabase
SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_role_key>
NEXT_PUBLIC_SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>

# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<générer avec: openssl rand -base64 32>
AUTH_SECRET=<même valeur que NEXTAUTH_SECRET>

# Google OAuth (depuis Google Cloud Console)
GOOGLE_CLIENT_ID=<client_id>
GOOGLE_CLIENT_SECRET=<client_secret>
```

## Key Conventions

- **Language**: French for UI text and comments
- **Currency**: XOF (West African CFA franc)
- **Distances**: kilometers
- **Dates**: French locale (`DD/MM/YYYY HH:mm`)
- **RLS**: Disabled for admin dashboard (uses service_role key)
- **Status values**: UPPERCASE (`ACTIVE`, `COMPLETED`, `ARCHIVED`, `CANCELLED`, `PENDING`)

## Current Status

### Done ✅
- [x] Next.js frontend setup with Shadcn/ui
- [x] Supabase integration with optimized queries
- [x] Trips page with list, details, pagination (5/page), status filter
- [x] Users page with list, details, pagination (10/page), role filter
- [x] Stats page with dashboard metrics
- [x] Database indexes for performance
- [x] Dark theme with Klando colors
- [x] Authentication NextAuth.js v5 + Google OAuth
- [x] Whitelist utilisateurs via `dash_authorized_users`
- [x] UserMenu avec avatar, rôle, déconnexion

### TODO 🚧
- [ ] Chats page
- [ ] Routes admin (vérification `role === "admin"`)
- [ ] Audit log des connexions
