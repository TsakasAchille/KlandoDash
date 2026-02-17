# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, and financial transactions.

- **Frontend**: The frontend is a Next.js 14 application, utilizing the App Router for page management. The user interface is built with Shadcn/ui and styled with TailwindCSS, creating a responsive and modern design. Key frontend dependencies include `leaflet` for map visualizations, `recharts` for statistical charts, and `@tanstack/react-table` for data tables. Mutations are handled using **Next.js Server Actions**.

- **Backend & Database**: The project leverages Supabase (PostgreSQL), providing a database, authentication, and auto-generated APIs. Aggregated data and stats are performed database-side via **SQL RPC functions** (`SECURITY DEFINER`) for performance and memory safety.

- **Authentication**: User authentication is handled by NextAuth.js (v5), with Google OAuth as the primary provider. Access is restricted to whitelisted users in the `dash_authorized_users` table.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (site-requests, transactions, map, stats, support)
│   ├── src/features/ # SOLID Business Logic (site-requests services & components)
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client, shared queries & core utils
│   └── src/types/    # TypeScript definitions
├── database/          # SQL schemas & migrations (find_matching_trips v2, stats rpc)
├── docs/              # Technical Documentation (AI Matching flow, Development guidelines)
└── README.md          # General project README
```

## Architecture & Logic Flow

### AI Matching Workflow (SOLID)
1. **Request**: Admin triggers matching for a client intention.
2. **Context**: `AIMatchingService` computes real-time km distances between client and driver points using `GeocodingService`.
3. **Intelligence**: Gemini receives the km context and generates a message using standardized `prompts.ts` templates (WhatsApp focused, car/flag emojis).
4. **Extraction**: `TripService` (Admin) fetches the full trip geometry using prefix-based search to handle partial IDs.
5. **Rendering**: `ComparisonMap` renders polylines with directional arrows and auto-corrects inverted paths.

## Key Performance Standards

- **SOLID Principles**: Business logic (geocoding, trip queries, AI) is strictly isolated from React components.
- **Honest AI Thresholds**: Adaptive messaging based on real distance (e.g., 5km is not "near" but a "solid option").
- **Reliable Map Lifecycle**: Manual Leaflet cleanup and `invalidateSize` calls to prevent DOM-related crashes.

## Current Status

### Done ✅
- [x] SOLID Architecture for Site Requests (Services/Features).
- [x] Advanced AI Matching with distance-aware prompts and robust ID extraction.
- [x] High-precision Map Visualization (Directional arrows, auto-correction, junction lines).
- [x] Optimized stats via SQL RPC functions.
- [x] Whitelisted Google OAuth Authentication.
- [x] Support ticket system with chat-like comments.
- [x] Transactions and cash-flow tracking.

### TODO 🚧
- [ ] Implement inter-user Chats module.
- [ ] Add audit logs for significant admin actions.
- [ ] Comprehensive testing for AI matching edge cases.

## Useful Documentation
- [docs/README.md](./docs/README.md) : Index.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : **Detailed AI matching technical guide.**
- [docs/DEVELOPMENT_GUIDELINES.md](./docs/DEVELOPMENT_GUIDELINES.md) : Standards.
- [docs/WEBSITE_INTEGRATION.md](./docs/WEBSITE_INTEGRATION.md) : Website sync guide.
