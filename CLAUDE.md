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
│   ├── layout.tsx          # Root layout + sidebar
│   ├── page.tsx            # Home
│   ├── trips/              # Trips page
│   ├── users/              # Users page
│   └── stats/              # Stats dashboard
├── components/
│   ├── sidebar.tsx         # Navigation
│   ├── ui/                 # Shadcn components
│   ├── trips/              # Trip components
│   └── users/              # User components
├── lib/
│   ├── supabase.ts         # Supabase clients
│   ├── queries/
│   │   ├── trips.ts        # Trip queries
│   │   ├── users.ts        # User queries
│   │   └── stats.ts        # Dashboard stats
│   └── utils.ts            # formatDate, formatPrice, cn
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

## Environment Variables

### Root `.env.local`
```env
SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co
SUPABASE_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_role_key>
```

### Frontend `frontend/.env.local`
```env
NEXT_PUBLIC_SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
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

### TODO 🚧
- [ ] Chats page
