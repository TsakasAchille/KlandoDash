# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, financial transactions, and marketing growth.

- **Frontend**: Next.js 14 (App Router) + Shadcn/ui + TailwindCSS.
- **Backend & Database**: Supabase (PostgreSQL) + SQL RPC functions for performance.
- **Authentication**: NextAuth.js (v5) + Google OAuth (Whitelisted access).
- **Intelligence**: Integrated Google Gemini API for strategic and operational analysis.

## Project Structure

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Pages (marketing, transactions, map, stats, support)
│   ├── src/features/ # SOLID Business Logic (site-requests services)
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client, mail service, shared queries
│   └── src/types/    # TypeScript definitions
├── database/          # SQL schemas & migrations (find_matching_trips, marketing tables)
├── docs/              # Technical Documentation
└── README.md          # General project README
```

## Architecture & Logic Flow

### Unified Marketing Cockpit
1.  **Strategy**: Analytical scan (SQL PostGIS) identifying matching opportunities.
2.  **Communication**: AI Social Post generator (TikTok, Instagram, X) and strategic angles.
3.  **Intelligence**: AI-generated strategic reports (Gemini) on Revenue and Conversion.
4.  **Mailing**: Automated draft system with integrated map screenshot capture.
5.  **Observatoire**: Geographical demand analysis via Heatmaps and Flow mapping.

### Data-Driven Workflows
*   **Analytical First**: High-performance SQL queries for proximity and flow calculation.
*   **Optional AI Finish**: Gemini used for language intelligence (posts, mailing, reports).
*   **Visual Context**: Automated map capture (`html2canvas`) for professional customer outreach.
*   **SOLID Principles**: Modular actions and tab components for maintainability.

## Key Performance Standards

- **Honest AI Thresholds**: Strict km limits (15km max) for matching suggestions.
- **Cost Efficiency**: SQL matching first, AI calls limited to text-based finalization.
- **UX Excellence**: High-contrast light themes for operational tools, real-time map invalidation.

## Current Status

### Done ✅
- [x] Marketing Cockpit with 6 strategic pillars.
- [x] Demand Observatory (Heatmap & Flows) via SQL RPC.
- [x] AI Communication agency (Social Post Generator).
- [x] Automated Mailing with map screenshot storage.
- [x] SOLID Refactor of the marketing module (Actions/Tabs/Shared).
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
