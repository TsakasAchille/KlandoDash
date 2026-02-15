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
| `transactions` | Payments (synced from Firebase) | `id` | ~57 |
| `dash_authorized_users` | Utilisateurs autorisés dashboard | `email` | ~8 |
| `support_tickets` | Tickets de support | `ticket_id` | - |
| `support_comments` | Commentaires sur tickets | `comment_id` | - |

### Key Relations
```
users ──< trips (driver_id → uid)
users ──< bookings (user_id → uid)
trips ──< bookings (trip_id)
trips ──< chats (trip_id)
bookings ──< transactions (bookings.transaction_id → transactions.id)
users ──< transactions (user_id → uid) [no FK, joined manually]
```

### Table `transactions` (synced from Firebase via Intech)
| Colonne | Type | Description |
|---------|------|-------------|
| `id` | text (PK) | ID transaction |
| `user_id` | text | ID utilisateur (= users.uid, pas de FK) |
| `intech_transaction_id` | text | ID Intech |
| `amount` | integer | Montant en XOF |
| `status` | text | SUCCESS, PENDING, FAILED, REFUNDED, CANCELLED |
| `type` | text | TRIP_PAYMENT, DRIVER_PAYMENT, REFUND |
| `code_service` | text | Contient CASH_IN ou CASH_OUT |
| `phone` | text | Numéro du client |
| `msg` | text | Message Intech |
| `created_at` | timestamp | Date création |
| `updated_at` | timestamp | Date mise à jour |

### Logique métier transactions
- **Marge Klando** = `transactions.amount` - `trips.driver_price` (via bookings.transaction_id) — inclut 15% TVA
- **Cash flow** (logique Intech inversée) :
  - `XXXXX_CASH_IN` dans `code_service` → argent qui **SORT** pour Klando
  - `XXXXX_CASH_OUT` dans `code_service` → argent qui **RENTRE** pour Klando
- **Stats** : agrégations uniquement sur `status = 'SUCCESS'`
- **Pas de FK** entre `transactions.user_id` et `users.uid` → joins manuels (2 requêtes séparées)
- **`users` table** : la colonne téléphone s'appelle `phone_number` (pas `phone`)

### Indexes (transactions)
- `idx_transactions_user_id` - Filter by user
- `idx_transactions_status` - Filter by status
- `idx_transactions_created_at` - Sort by date DESC
- `idx_transactions_type` - Filter by type
- `idx_transactions_user_created` - Combined user + date
- `idx_transactions_status_created` - Combined status + date

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
│   ├── api/                # API Routes
│   │   ├── admin/users/    # User management API
│   │   ├── mention-users/  # Autocomplete mentions
│   │   ├── support/        # Ticket comments API
│   │   └── users/[uid]/    # User trips & transactions API
│   ├── login/              # Page de connexion
│   ├── trips/              # Trips page
│   ├── users/              # Users page
│   ├── transactions/       # Transactions page
│   ├── stats/              # Stats dashboard (+ cash flow + revenus)
│   ├── map/                # Real-time trips visualization map
│   └── support/            # Support tickets
├── components/
│   ├── sidebar.tsx         # Navigation + UserMenu
│   ├── user-menu.tsx       # Menu utilisateur (avatar, rôle, déconnexion)
│   ├── refresh-button.tsx  # Global manual refresh component
│   ├── providers.tsx       # SessionProvider wrapper
│   ├── layout-content.tsx  # Layout conditionnel (avec/sans sidebar)
│   ├── ui/                 # Shadcn components (+ skeleton.tsx)
│   ├── trips/              # Trip components
│   ├── map/                # Map components (filters, popups)
│   ├── users/              # User components (+ transactions tab)
│   ├── transactions/       # Transaction components
│   ├── support/            # Support ticket components
│   └── emails/             # React Email templates (Resend)
├── lib/
│   ├── auth.ts             # Configuration NextAuth.js
│   ├── supabase.ts         # Supabase clients
│   ├── queries/
│   │   ├── trips.ts        # Trip queries (+ getTripsForMap)
│   │   ├── users.ts        # User queries
│   │   ├── transactions.ts # Transaction queries + cash flow + revenue
│   │   ├── stats.ts        # Dashboard stats (+ transactions + cash flow)
│   │   └── support.ts      # Support ticket queries
│   └── utils.ts            # formatDate, formatPrice, cn
├── middleware.ts           # Protection des routes (redirect /login)
└── types/
    ├── trip.ts             # Trip types
    ├── transaction.ts      # Transaction types + cash flow + revenue
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

### Available Queries (`lib/queries/`)
```typescript
// trips.ts
getTrips(options)         // List with minimal columns
getTripById(tripId)       // Detail with driver join
getTripsStats()           // Aggregated stats
getTripsWithDriver(limit) // Enriched list with driver info
getPassengersForTrip(id)  // Passengers for a trip
getTripsForMap(limit)     // Geo-data for trips map

// users.ts
getUsers(options)         // List with pagination and advanced filters (role, verified, gender, minRating, isNew)
getUserById(uid)          // Detail with stats
getUsersStats()           // Aggregated stats
getDriversList()          // List of drivers

// transactions.ts
getTransactions(options)       // List with filters (status, type, userId)
getTransactionsWithUser(limit) // List with user info (manual join, no FK)
getTransactionById(id)         // Detail with user + booking + trip
getTransactionsStats()         // Aggregated stats
getCashFlowStats({ from?, to? })  // Cash in/out (SUCCESS only)
getRevenueStats({ from?, to? })   // Klando margin via bookings
getTransactionsForUser(userId)    // User transaction history

// support.ts
getTicketsWithUser()      // List with user info
getTicketDetail(id)       // Detail with comments
updateTicketStatus(id, s) // Server Action
addComment(id, email, t)  // Add comment to ticket
```

## Theme Colors (Klando)

| Name | Hex | CSS Variable | Usage |
|------|-----|--------------|-------|
| Gold | `#EBC33F` | `--klando-gold` | Primary accents, titles |
| Burgundy | `#7B1F2F` | `--klando-burgundy` | Selected states |
| Dark | `#081C36` | `--klando-dark` | Backgrounds |
| Light Blue | `#1B3A5F` | `--klando-blue-light` | Comment bubbles |
| Secondary Dark | `#102A4C` | `--klando-dark-s` | Comment bubbles |
| Grizzly Grey | `#A0AEC0` | `--klando-grizzly` | Text muted |

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
| `role` | varchar(50) | `admin`, `support` ou `user` |
| `added_at` | timestamp | Date d'ajout |
| `added_by` | varchar(255) | Ajouté par |
| `display_name` | text | Nom depuis OAuth provider |
| `avatar_url` | text | Avatar depuis OAuth provider |

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

# Resend (emails)
RESEND_API_KEY=<api_key>
RESEND_FROM_EMAIL=KlandoDash <onboarding@resend.dev>  # Dev: resend.dev, Prod: no-reply@klando-sn.com
```

## Key Conventions

- **Language**: French for UI text and comments
- **Currency**: XOF (West African CFA franc)
- **Distances**: kilometers
- **Dates**: French locale (`DD/MM/YYYY HH:mm`)
- **RLS**: Disabled for admin dashboard (uses service_role key)
- **Status values**: UPPERCASE (`ACTIVE`, `COMPLETED`, `ARCHIVED`, `CANCELLED`, `PENDING`)
- **User roles**: `admin` (full access), `support` (support page only), `user` (read-only)

## Current Status

### Done ✅
- [x] Next.js frontend setup with Shadcn/ui
- [x] Supabase integration with optimized queries
- [x] Trips page with list, details, deep linking, passenger profiles
- [x] Users page with list, details, deep linking
- [x] Stats page with dashboard metrics
- [x] Database indexes for performance
- [x] Dark theme with Klando colors
- [x] Authentication NextAuth.js v5 + Google OAuth
- [x] Whitelist utilisateurs via `dash_authorized_users`
- [x] UserMenu avec avatar, rôle, déconnexion
- [x] Basic admin API pour user management (`/api/admin/users`)
- [x] Support tickets module avec interface chat
- [x] Changement de statut ticket via Server Actions
- [x] Mentions (@user) dans les commentaires
- [x] Notifications email via Resend (mentions)
- [x] Rôle `support` avec accès restreint
- [x] Transactions page avec liste, détails, deep linking, cash flow
- [x] Map page avec visualisation des trajets en temps réel
- [x] Intégration transactions dans page users (onglets Trajets/Transactions)
- [x] Stats : cash flow (entrées/sorties/solde), revenus réels (marge Klando), distribution transactions
- [x] Global Skeleton Loading pour les transitions de pages
- [x] Filtres de recherche (UserTable, TripTable)
- [x] Tableaux responsifs optimisés pour mobile
- [x] Fiche utilisateur avec indicateurs circulaires et biographie
- [x] Indexes et RLS pour table transactions

### TODO 🚧
- [ ] Chats page (communication inter-utilisateurs)
- [ ] Export CSV transactions (compta)
- [ ] Routes admin avancées et permissions
- [ ] Audit log des connexions et actions
- [ ] Tests automatisés
- [ ] Export de données
