# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, and financial transactions.

- **Frontend**: The frontend is a Next.js 14 application, utilizing the App Router for page management. The user interface is built with Shadcn/ui and styled with TailwindCSS, creating a responsive and modern design. Key frontend dependencies include `leaflet` for map visualizations, `recharts` for statistical charts, and `@tanstack/react-table` for data tables. Mutations (like updating ticket status) are now handled using **Next.js Server Actions** for a more direct server interaction.

- **Backend & Database**: The project leverages Supabase, a Backend-as-a-Service (BaaS) platform, which provides a PostgreSQL database, authentication, and auto-generated APIs. The database schema includes core tables for `trips`, `users`, `bookings`, `support_tickets`, and `transactions`. The `database/schema.sql` file defines the complete database structure, including tables, relationships, and indexes.

- **Authentication**: User authentication is handled by NextAuth.js (v5), with Google OAuth as the primary authentication provider. Access to the dashboard is restricted to authorized users listed in the `dash_authorized_users` table in the Supabase database. These records are now enriched with `display_name` and `avatar_url` directly from the Google profile during login via a NextAuth `signIn` callback. Role-based access control is implemented, including `admin` and `support` roles.

- **Data Flow**: The frontend communicates with the Supabase backend through the `@supabase/supabase-js` client library. Data fetching is performed on the server-side using React Server Components, with dedicated query functions in `frontend/src/lib/queries/`. These functions are optimized to fetch only the required data, ensuring efficient data retrieval.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (App Router)
│   │   ├── transactions/ # Transactions module
│   │   ├── map/          # Real-time trips map
│   │   └── ...
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client + queries, auth utilities
│   ├── src/types/    # TypeScript type definitions
│   ├── .env.example  # Example environment variables
│   └── package.json  # Frontend dependencies and scripts
├── database/          # SQL schemas, migrations, queries
│   ├── schema.sql    # Full database schema dump
│   ├── tables.md     # Tables documentation
│   └── migrations/   # SQL migration files
├── .env.local         # Local environment variables (symlinked to frontend/.env.local)
├── package.json       # Root project dependencies (if any)
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
# Link your local Supabase project to a remote one (replace with your project ref)
npx supabase link --project-ref your-supabase-project-ref

# Push local migrations to your Supabase project
npx supabase db push

# Dump the current database schema to a file
npx supabase db dump --schema public -f database/schema.sql
```

## Database (Supabase)

**Platform**: Supabase (PostgreSQL)

### Main Tables
| Table | Description | PK |
|-------|-------------|----|
| `users` | User profiles | `uid` |
| `trips` | Trip listings | `trip_id` |
| `bookings` | Trip reservations by users | `id` |
| `support_tickets` | User support tickets | `ticket_id` |
| `transactions` | Financial transactions (Integrapay) | `id` |
| `dash_authorized_users` | Authorized dashboard users | `email` |

### Key Relations
```mermaid
erDiagram
    users ||--o{ trips : "driver_id FK"
    users ||--o{ bookings : "user_id FK"
    trips ||--o{ bookings : "trip_id FK"
    users ||--o{ dash_authorized_users : "email FK"
    users ||--o{ support_tickets : "user_id FK"
    users ||--o{ transactions : "user_id FK"
    bookings ||--o? transactions : "transaction_id FK"
```

### Query Best Practices
- **Avoid `SELECT *`**: Always specify columns to fetch only necessary data.
- **Utilize Indexes**: Ensure relevant columns are indexed for efficient filtering and sorting.
- **Leverage Joins**: Use Supabase's foreign table relationships for efficient data retrieval across tables (e.g., `driver:users!fk_driver`).

## Frontend Architecture (Next.js 14)

### Structure (`frontend/src/`)
```
frontend/src/
├── app/                  # App Router pages and layouts
│   ├── layout.tsx        # Root layout, SessionProvider
│   ├── page.tsx          # Home page
│   ├── api/              # API Routes (serverless functions)
│   │   └── admin/        # Admin-specific API routes
│   │       └── users/    # API for user management
│   ├── login/            # Login page and layout
│   ├── trips/            # Trips page and client components
│   ├── users/            # Users page and client components
│   ├── stats/            # Statistics dashboard page
│   ├── transactions/     # Transactions management page
│   └── map/              # Real-time trips visualization map
├── components/           # Reusable UI components
│   ├── ui/               # Shadcn/ui components
│   ├── sidebar.tsx       # Main navigation sidebar
│   ├── user-menu.tsx     # User profile menu (avatar, role, logout)
│   ├── refresh-button.tsx # Global manual refresh component
│   └── providers.tsx     # Context providers (e.g., NextAuth SessionProvider)
├── lib/                  # Utility functions and configurations
│   ├── auth.ts           # NextAuth.js configuration
│   ├── supabase.ts       # Supabase client initialization
│   ├── queries/          # Data fetching functions for specific entities
│   │   ├── trips.ts      # Trip-related data queries
│   │   ├── users.ts      # User-related data queries
│   │   ├── transactions.ts # Transaction-related data queries
│   │   └── stats.ts      # Dashboard metrics queries
│   └── utils.ts          # General utility functions (formatters, class mergers)
├── middleware.ts         # Authentication middleware for route protection (RBAC)
└── types/                # TypeScript global type definitions
    ├── trip.ts           # Trip data structures
    ├── user.ts           # User data structures
    └── transaction.ts    # Transaction data structures
```

### Data Flow Example (Trips Page)
```mermaid
graph TD
    A[User requests /trips] --> B(Next.js Server Component: frontend/src/app/trips/page.tsx)
    B --> C{Call getTripsWithDriver & getTripsStats}
    C --> D[Supabase (trips, users tables)]
    D --> E{Data received}
    E --> F(Data transformed to Trip[] and TripDetail)
    F --> G(Passes props to Client Component: frontend/src/app/trips/trips-client.tsx)
    G --> H(TripTable: displays list of Trip)
    G --> I(TripDetails: displays selected TripDetail)
    H -- User selects a trip --> J{Update URL: /trips?selected=TRIP_ID}
    J --> A
```

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

### Key Authentication Files
- `frontend/src/lib/auth.ts`: NextAuth.js configuration, callbacks.
- `frontend/src/middleware.ts`: Route protection and redirection.
- `frontend/src/app/login/page.tsx`: Login user interface.
- `frontend/src/components/user-menu.tsx`: User session display and logout functionality.

## Environment Variables

The project requires a `.env.local` file in the root directory (symlinked to `frontend/.env.local`).

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://<your-project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key> # Used for admin operations

# NextAuth.js Configuration
NEXTAUTH_URL=http://localhost:3000 # Base URL of your application
NEXTAUTH_SECRET=<32-char-base64-string> # Generate with: openssl rand -base64 32
AUTH_SECRET=<same-as-NEXTAUTH_SECRET> # NextAuth v5 specific

# Google OAuth Credentials (from Google Cloud Console)
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
```

## Available Queries (`frontend/src/lib/queries/`)
- `trips.ts`: `getTrips`, `getTripById`, `getTripsStats`, `getTripsWithDriver`, `getPassengersForTrip`, `getTripsForMap`, `getDriversList`
- `users.ts`: `getUsers`, `getUserById`, `getUsersStats`, `getDriversList`
- `support.ts`: `getTicketsWithUser`, `getTicketDetail`, `updateTicketStatus`, `addComment`
- `transactions.ts`: `getTransactions`, `getTransactionById`, `getCashFlowStats`, `getRevenueStats`, `getTransactionsForUser`

## Theme Colors (Klando)

The dashboard uses a custom color palette defined in `tailwind.config.ts`.

| Name | Hex | CSS Variable | Usage |
|------|-----|--------------|-------|
| Gold | `#EBC33F` | `--klando-gold` | Primary accents, links, titles |
| Burgundy | `#7B1F2F` | `--klando-burgundy` | Backgrounds, selected states |
| Dark Blue | `#081C36` | `--klando-dark` | Text, primary backgrounds |
| Light Blue | `#1B3A5F` | `--klando-blue-light` | Comment bubbles |
| Secondary Dark | `#102A4C` | `--klando-dark-s` | Comment bubbles |
| Grizzly Grey | `#A0AEC0` | `--klando-grizzly` | Text |

## Key Conventions

- **Language**: French for UI text, comments, and documentation.
- **Currency**: XOF (West African CFA franc).
- **Distances**: Kilometers.
- **Dates**: French locale (`DD/MM/YYYY HH:mm`).
- **Row Level Security (RLS)**: Generally disabled for the admin dashboard (uses `service_role` key for direct access).
- **Status Values**: Uppercase (`ACTIVE`, `COMPLETED`, `ARCHIVED`, `CANCELLED`, `PENDING`).

## Current Status

### Done ✅
- [x] Next.js frontend setup with Shadcn/ui.
- [x] Supabase integration with optimized queries.
- [x] Trips page with list, details, deep linking, passenger profiles.
- [x] Users page with list, details, deep linking.
- [x] Stats page with dashboard metrics.
- [x] Transactions module with cash flow and revenue tracking.
- [x] Map page for real-time trip visualization.
- [x] Database indexes for performance.
- [x] Dark theme with Klando colors.
- [x] Authentication using NextAuth.js v5 + Google OAuth.
- [x] User whitelisting via `dash_authorized_users` table.
- [x] Role-based access control (Admin, Support).
- [x] UserMenu with avatar, role, and logout.
- [x] Refresh button for manual data revalidation.
- [x] Global Skeleton Loading for smooth page transitions.
- [x] Responsive tables with optimized mobile display.
- [x] Search filters for users (name/email) and trips (city/ID).
- [x] Redesigned User Details with circular indicators and bio.
- [x] Basic admin API for user management (`/api/admin/users`).
- [x] Support tickets module with chat-like interface for comments.
- [x] Ability to change support ticket status via Server Actions.
- [x] Mention/Tag system in support comments (emails via Resend).

### TODO 🚧
- [ ] Fix mention notification email rendering (known issue with `render` in App Router).
- [ ] Implement a Chats page for inter-user communication.
- [ ] Develop more robust admin routes and permissions beyond basic user management.
- [ ] Implement an audit log for user connections and significant actions.
- [ ] Add comprehensive testing for all new features and bug fixes.
- [ ] Implement data export functionality for various tables.