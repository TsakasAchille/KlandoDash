# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KlandoDash is a dashboard application for Klando, a carpooling/ride-sharing service in Senegal. The project has migrated from Streamlit to Next.js with Supabase as the primary database.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui (active)
│   ├── src/app/      # Pages (App Router)
│   ├── src/marketing # Module de croissance (IA + Prospects + Radar)
│   ├── src/components/
│   ├── src/lib/      # Supabase client + queries + mail
│   └── src/types/    # TypeScript types
├── database/          # SQL schemas, migrations, queries
│   ├── schema.sql    # Full schema dump
│   ├── migrations/   # SQL migrations
│   └── tests/        # Query tests
├── docs/              # Technical documentation
└── src/               # Streamlit app (legacy - deprecated)
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
| Table | Description | PK |
|-------|-------------|-----|
| `users` | User profiles | `uid` |
| `trips` | Trip listings | `trip_id` |
| `bookings` | Reservations | `id` |
| `transactions` | Payments (synced from Firebase) | `id` |
| `dash_authorized_users` | Utilisateurs autorisés dashboard | `email` |
| `support_tickets` | Tickets de support | `ticket_id` |
| `dash_ai_recommendations` | Opportunités marketing IA | `id` |
| `dash_marketing_insights` | Rapports stratégiques IA | `id` |
| `dash_marketing_emails` | Brouillons et historique mailing | `id` |

## Authentication (NextAuth.js v5)

Le dashboard utilise NextAuth.js avec Google OAuth. Seuls les utilisateurs présents dans la table `dash_authorized_users` avec `active=true` peuvent accéder.

| Rôle | Accès |
|------|-------|
| `admin` | Accès total (Finance, Stats, Marketing, Admin) |
| `marketing` | Accès Croissance (Prospects, IA Strategy, Mailing, Map, Support) |
| `support` | Accès Service Client (Tickets, Chats, Users, Map) |

## Theme Colors (Klando)

| Name | Hex | Usage |
|------|-----|-------|
| Gold | `#EBC33F` | Primary accents, titles |
| Burgundy | `#7B1F2F` | Selected states |
| Dark | `#081C36` | Backgrounds |
| Light Blue | `#1B3A5F` | UI Elements |

## Current Status

### Done ✅
- [x] Unified Marketing Cockpit (Strategy, Intelligence, Prospects, Radar, Mailing)
- [x] SOLID architecture for modular UI components
- [x] Analytical Strategic Scan (SQL PostGIS) for cost-efficient matching
- [x] AI Strategic Reports (Gemini) with premium Markdown rendering
- [x] AI-driven Mailing system with Resend integration
- [x] Role-based access control (Admin / Marketing / Support)
- [x] Professional dark theme optimized for growth operations
- [x] High-precision map visualization with Leaflet
- [x] Support ticket module with mentions and notifications
