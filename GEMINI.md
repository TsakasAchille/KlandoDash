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
│   ├── src/features/ # SOLID Business Logic
│   ├── src/components/ # Reusable UI components
│   ├── src/lib/      # Supabase client, mail service, shared queries
│   └── src/types/    # TypeScript definitions
├── database/          # SQL schemas & migrations (find_matching_trips, marketing tables)
├── docs/              # Technical Documentation
└── README.md          # General project README
```

## Architecture & Logic Flow

### Unified Marketing Cockpit
1.  **Strategy**: Analytical scan (SQL PostGIS) to identify matching opportunities without systematic AI costs.
2.  **Intelligence**: AI-generated strategic reports (Gemini) on Revenue, Conversion, and Quality.
3.  **Mailing**: AI-driven email campaigns dispatched via Resend.
4.  **Radar**: Precision execution workbench for geographical matching.

### Data-Driven Workflows
*   **Analytical First**: High-performance SQL queries for proximity calculation.
*   **Optional AI Finish**: Gemini is used only when language intelligence is required (message drafting, report writing).
*   **SOLID Principles**: Modular architecture with extracted tab components for maintainability.

## Key Performance Standards

- **Honest AI Thresholds**: Strict km limits (15km max) for matching suggestions.
- **Stateless Intelligence**: AI only sees anonymized context relevant to the current task.
- **Reliable UI**: Controlled tab states and robust error handling for asynchronous actions.

## Current Status

### Done ✅
- [x] Marketing Cockpit with Strategy, Intelligence, Radar, and Mailing tabs.
- [x] SOLID Architecture for modular tab management.
- [x] Advanced AI Matching with distance-aware prompts.
- [x] Premium report rendering with ReactMarkdown.
- [x] Professional mailing system with Resend integration.
- [x] Whitelisted Google OAuth Authentication.

### TODO 🚧
- [ ] Implement inter-user Chats module.
- [ ] Add audit logs for significant admin actions.
- [ ] Comprehensive testing for AI matching edge cases.

## Useful Documentation
- [docs/README.md](./docs/README.md) : Index.
- [docs/AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md) : **AI & Marketing Architecture Guide.**
- [docs/Klando-Gemini.md](./docs/Klando-Gemini.md) : Data Visibility Matrix.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Analytical matching details.
