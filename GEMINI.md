# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, financial transactions, marketing strategy, and content production.

- **Frontend**: Next.js 14 (App Router) + Shadcn/ui + TailwindCSS.
- **Backend & Database**: Supabase (PostgreSQL) + SQL RPC functions for performance.
- **Authentication**: NextAuth.js (v5) + Google OAuth (Whitelisted access).
- **Intelligence**: Integrated Google Gemini API for strategic and operational analysis.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (marketing, editorial, transactions, map, stats, support)
│   ├── src/features/ # SOLID Business Logic (site-requests services)
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client, mail service, shared queries
│   └── src/types/    # TypeScript definitions
├── database/          # SQL schemas & migrations (find_matching_trips, marketing tables)
├── docs/              # Technical Documentation
└── README.md          # General project README
```

## Architecture & Logic Flow

### Unified Marketing & Editorial Cockpit
1.  **Strategy (/marketing)**: Analytical scan (SQL PostGIS) identifying matching opportunities.
2.  **Intelligence (/marketing)**: AI-generated strategic reports (Gemini) on Revenue and Conversion.
3.  **Observatoire (/marketing)**: Geographical demand analysis via Heatmaps and Flow mapping.
4.  **Production (/editorial)**: AI Social Post generator (TikTok, Instagram, X) and unified mailing drafts.
5.  **Planning (/editorial)**: Interactive calendar for scheduling content and collaborative comments.

### Data-Driven Workflows
*   **Analytical First**: High-performance SQL queries for proximity and flow calculation.
*   **Optional AI Finish**: Gemini used for language intelligence (posts, mailing, reports).
*   **Visual Context**: Integrated media library and map screenshot capture for customer outreach.
*   **Collaboration**: Internal comment system for dashboard users on every piece of content.
*   **SOLID Principles**: Modular actions and decoupled domains (Strategy vs Production).

## Key Performance Standards

- **Honest AI Thresholds**: Strict km limits (15km max) for matching suggestions.
- **Cost Efficiency**: SQL matching first, AI calls limited to text-based finalization.
- **UX Excellence**: High-contrast light themes for operational tools, real-time calendar updates.

## Current Status

### Done ✅
- [x] Marketing Cockpit (Strategy, Radar, Observatory).
- [x] Editorial Center (Calendar, Planning, Social Media, Mailing).
- [x] Internal Collaboration (User Comments on content).
- [x] Demand Observatory (Heatmap & Flows) via SQL RPC.
- [x] AI Communication agency (Social Post Generator).
- [x] Automated Mailing with map screenshot storage.
- [x] SOLID Refactor of the marketing and editorial modules.
- [x] High-precision Map Visualization (Directional arrows, auto-correction).
- [x] Optimized stats via SQL RPC functions.

### TODO 🚧
- [ ] Implement inter-user Chats module.
- [ ] Add audit logs for significant admin actions.
- [ ] Comprehensive testing for AI matching edge cases.

## Useful Documentation
- [docs/MARKETING_MODULE.md](./docs/MARKETING_MODULE.md) : **Detailed Marketing Cockpit Guide.**
- [docs/README.md](./docs/README.md) : Index.
- [docs/AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md) : AI & Architecture Guide.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Technical matching details.
