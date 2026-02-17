# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, and financial transactions.

- **Frontend**: The frontend is a Next.js 14 application, utilizing the App Router for page management. The user interface is built with Shadcn/ui and styled with TailwindCSS, creating a responsive and modern design. Key frontend dependencies include `leaflet` for map visualizations, `recharts` for statistical charts, and `@tanstack/react-table` for data tables. Mutations (like updating ticket status) are now handled using **Next.js Server Actions** for a more direct server interaction.

- **Backend & Database**: The project leverages Supabase, a Backend-as-a-Service (BaaS) platform, which provides a PostgreSQL database, authentication, and auto-generated APIs. The database schema includes core tables for `trips`, `users`, `bookings`, `support_tickets`, and `transactions`. The `database/schema.sql` file defines the complete database structure, including tables, relationships, and indexes.

- **Authentication**: User authentication is handled by NextAuth.js (v5), with Google OAuth as the primary authentication provider. Access to the dashboard is restricted to authorized users listed in the `dash_authorized_users` table in the Supabase database. These records are enriched with `display_name` and `avatar_url` from the Google profile. Role-based access control is implemented (Admin, Support).

- **Data Flow**: The frontend communicates with the Supabase backend through the `@supabase/supabase-js` client library.
  - **Standard Data**: Fetched on the server-side using React Server Components with dedicated query functions.
  - **Aggregated Data (Stats)**: Heavy calculations MUST be performed database-side via **SQL RPC functions** (`SECURITY DEFINER`). The frontend calls these via `supabase.rpc()` to receive pre-processed JSON, ensuring memory safety.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages & API Routes
│   │   ├── site-requests/ # Intentions management (AI Matching)
│   │   ├── transactions/ # Transactions module
│   │   ├── map/          # Real-time trips map
│   │   └── ...
│   ├── src/features/ # Modular business logic (SOLID)
│   │   └── site-requests/ # Geocoding, Trip, and AI services
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client, queries & logic
│   ├── src/types/    # TypeScript definitions
│   └── package.json  # Frontend dependencies
├── database/          # SQL schemas & migrations
│   ├── schema.sql    # Full database schema dump
│   ├── tables.md     # Tables documentation
│   └── migrations/   # SQL migration files
├── docs/              # Technical Documentation
│   ├── WEBSITE_INTEGRATION.md # Guide site vitrine
│   ├── AI_MATCHING_SYSTEM.md  # Flux technique Matching IA
│   ├── GPT.md         # Philosophie d'interconnexion
│   └── ...
├── .env.local         # Local environment variables
└── README.md          # General project README
```

## Commands

### Frontend (Next.js)
```bash
cd frontend
npm install      # Install dependencies
npm run dev      # Start development server on http://localhost:3000
npm run build    # Create production build
npm run start    # Start production server
npm run lint     # Run ESLint for code quality
```

### Database (Supabase CLI)
```bash
# Push local migrations to your Supabase project
npx supabase db push

# Dump the current database schema to a file
npx supabase db dump --schema public -f database/schema.sql
```

## Database (Supabase)

### Main Tables
| Table | Description | PK |
|-------|-------------|----|
| `users` | User profiles | `uid` |
| `trips` | Trip listings | `trip_id` |
| `bookings` | Trip reservations by users | `id` |
| `support_tickets` | User support tickets | `ticket_id` |
| `transactions` | Financial transactions (Integrapay) | `id` |
| `dash_authorized_users` | Authorized dashboard users | `email` |

### Table `dash_authorized_users`
| Column | Type | Description |
|--------|------|-------------|
| `email` | varchar(255) | User's email (Primary Key) |
| `active` | boolean | Is user currently authorized? |
| `role` | varchar(50) | User's role (`admin`, `user`, etc.) |
| `added_at` | timestamp | Date user was added |
| `added_by` | varchar(255) | Admin email who added this user |
| `display_name` | text | User's display name from OAuth provider |
| `avatar_url` | text | User's avatar URL from OAuth provider |

## Architecture & Data Flow

### Data Flow Example (AI Matching)
1. **Trigger**: Admin clique sur "Aide IA" pour une demande client.
2. **Action**: `getAIMatchingAction` (Server Action) appelle Gemini.
3. **Services (SOLID)**: `TripService` (Admin) récupère les détails du trajet ; `GeocodingService` calcule les itinéraires et flèches.
4. **Visualisation**: `ComparisonMap` affiche les polylines, jonctions (Vert/Rouge) et sens du trajet.

### Data Flow Example (Trips Page)
```mermaid
graph TD
    A[User requests /trips] --> B(Next.js Server Component)
    B --> C{Call getTripsWithDriver & getTripsStats}
    C --> D[Supabase (trips, users tables)]
    D --> E{Data received}
    E --> F(Data transformed to Trip[] and TripDetail)
    F --> G(Passes props to Client Component)
    G --> H(TripTable: displays list of Trip)
    G --> I(TripDetails: displays selected TripDetail)
```

## Environment Variables

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://<your-project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

# NextAuth.js Configuration
NEXTAUTH_URL=http://localhost:3000
AUTH_SECRET=<32-char-base64-string>

# Google OAuth Credentials
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

## Available Queries (`frontend/src/lib/queries/`)
- `trips.ts`: `getTrips`, `getTripById`, `getTripsStats`, `getTripsWithDriver`, `getTripsForMap`
- `users.ts`: `getUsers`, `getUserById`, `getUsersStats`
- `support.ts`: `getTicketsWithUser`, `updateTicketStatus`, `addComment`
- `site-requests.ts`: `getSiteTripRequests`, `getPublicPendingTrips`
- `transactions.ts`: `getTransactions`, `getCashFlowStats`, `getRevenueStats`

## Theme Colors (Klando)

| Name | Hex | CSS Variable | Usage |
|------|-----|--------------|-------|
| Gold | `#EBC33F` | `--klando-gold` | Primary accents, links, titles |
| Burgundy | `#7B1F2F` | `--klando-burgundy` | Backgrounds, selected states |
| Dark Blue | `#081C36` | `--klando-dark` | Text, primary backgrounds |
| Light Blue | `#1B3A5F` | `--klando-blue-light` | Comment bubbles |
| Secondary Dark | `#102A4C` | `--klando-dark-s` | Comment bubbles |

## Convenciones & Performance

- **Principes SOLID**: Logique métier séparée de l'UI via des Services (`features/`).
- **Memory Safety**: Calculs lourds déportés en SQL RPC.
- **Extraction Robuste**: Parsing d'IA gérant l'insensibilité à la casse et les formats d'IDs multiples.
- **Clarté Visuelle**: Utilisation de flèches directionnelles et auto-correction du sens des tracés.

## Useful Documentation
- [docs/README.md](./docs/README.md) : Index.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Guide technique du Matching IA.
- [docs/DEVELOPMENT_GUIDELINES.md](./docs/DEVELOPMENT_GUIDELINES.md) : Standards de performance.
- [docs/WEBSITE_INTEGRATION.md](./docs/WEBSITE_INTEGRATION.md) : Guide intégration site.
