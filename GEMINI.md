# KlandoDash Project Summary

## Project Overview

KlandoDash is the administration dashboard for Klando, a carpooling service in Senegal. This full-stack project is built with a modern tech stack, providing a comprehensive interface for managing trips, users, support tickets, financial transactions, and marketing growth.

- **Frontend**: Next.js 14 (App Router) + Shadcn/ui + TailwindCSS.
- **Backend & Database**: Supabase (PostgreSQL) + SQL RPC functions for performance.
- **Authentication**: NextAuth.js (v5) + Google OAuth (Whitelisted access).
- **Intelligence**: Integrated Google Gemini API for strategic and operational analysis.

## Project Structure (SOLID Refactored)

```
KlandoDash/
├── frontend/          # Next.js 14 + Shadcn/ui
│   ├── src/app/      # Routes (Pages) - Simplified, orchestrates features
│   ├── src/features/ # Domain Business Logic & Components (SOLID)
│   │   ├── marketing/# Strategy, Intelligence, Observatoire
│   │   ├── editorial/# Production Center (Social Media, Mailing, Calendar)
│   │   └── map/      # High-precision Visualization
│   ├── src/components/ # Reusable UI (Shadcn, Shared)
│   ├── src/lib/      # Supabase client, gemini, mail service, shared queries
│   └── src/types/    # TypeScript definitions
├── database/          # SQL schemas & migrations (find_matching_trips, marketing tables)
├── docs/              # Technical Documentation
└── README.md          # General project README
```

## Architecture & Logic Flow

### 1. Feature-Driven Design (SOLID)
Les composants lourds (`CommunicationTab`, `MailingTab`, `MapClient`) sont découpés en sous-composants spécialisés (List, Editor, Preview, Sidebar) isolés dans le dossier `features/`.

### 2. Centre Éditorial (Production Focus)
- **Interface Split-View** : Navigation à gauche, zone de production à droite (750px fixe pour zéro scroll).
- **IA Radar Intégrée** : Générateur IA affiché par défaut avec accès direct aux Angles Stratégiques (Génération en 1 clic).
- **Dual-Mode Social Media** : Support natif des "Posts Visuels" (PNG pur) vs "Posts Standards" (Texte + Media).
- **Gestion de Corbeille** : Système complet de suppression, restauration et suppression définitive.

### 3. Radar de Matching & Capture
- **Haute Fidélité** : Utilisation de `preferCanvas: true` dans Leaflet pour garantir un alignement parfait des tracés lors des captures `html2canvas` pour les brouillons.
- **Auto-Correction** : Les polylines de trajets sont automatiquement inversées si le sens de saisie ne correspond pas au trajet conducteur.

## Current Status

### Done ✅
- [x] Refactorisation SOLID complète (Features directory).
- [x] Centre Éditorial avec Navigation Collante (Sticky Header).
- [x] Social Media Workspace (Visual Posts & Trash).
- [x] Automated Mailing avec capture de carte alignée.
- [x] High-precision Map Visualization (Directional arrows).
- [x] Optimisation de l'IA Radar (Inspiration -> Génération immédiate).

### TODO 🚧
- [ ] Implémentation du module de Chat inter-utilisateurs.
- [ ] Ajout de journaux d'audit (Audit Logs) pour les actions admin.
- [ ] Tests exhaustifs sur les cas limites de matching PostGIS.

## Useful Documentation
- [docs/MARKETING_MODULE.md](./docs/MARKETING_MODULE.md) : **Detailed Marketing Cockpit Guide.**
- [docs/WEBSITE_INTEGRATION.md](./docs/WEBSITE_INTEGRATION.md) : Guide d'intégration Klando.site.
- [docs/AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md) : AI & Architecture Guide.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Technical matching details.
