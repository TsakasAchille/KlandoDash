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
- **Interface Dual-Pane** : Navigation à gauche (largeur 320px fixe), zone de production à droite (scroll indépendant).
- **IA Génératrice Intégrée** : Accessible directement via le bouton "Nouveau Post", permettant de générer un brouillon complet (titre, contenu, hashtags, idée visuelle) à partir d'un simple sujet.
- **Support Multi-Plateforme** : TikTok, Instagram, LinkedIn, X, et catégorie "Autre".
- **Gestion de Corbeille** : Système complet de suppression, restauration et suppression définitive.

### 3. IA Data Hub & Automatisation
- **IA Data Hub (`/ia`)** : Page dédiée fournissant un flux de données brutes pour l'ingestion par des agents IA externes.
- **Pilotage par URL** : Support des paramètres `?origin=...&dest=...` pour déclencher des recherches automatiques.
- **Visual Capture Hub** : Pont Base64 permettant à l'IA d'injecter des captures d'écran Facebook directement dans le stockage Supabase pour enrichir les brouillons.
- **Rôle IA Dédié** : Nouveau profil utilisateur `ia` restreint uniquement à l'Accueil et au Hub de données.

### 4. Radar de Matching & Capture
- **Haute Fidélité** : Utilisation de `preferCanvas: true` dans Leaflet pour garantir un alignement parfait des tracés lors des captures `html2canvas`.
- **Auto-Correction** : Inversion automatique des polylines si le sens de saisie diverge du trajet conducteur.

## Current Status

### Done ✅
- [x] Refactorisation SOLID complète.
- [x] Centre Éditorial Responsif (Navigation Mobile par piles vs Desktop colonnes).
- [x] Unification de la création Social Media (Générateur IA intégré au popup).
- [x] IA Data Hub avec pilotage par URL et pont Base64 pour images.
- [x] Support LinkedIn et Catégorie Autre dans les communications.
- [x] Migration SMTP Google (Nodemailer) pour le mailing.
- [x] Rôle `ia` avec accès restreint.
- [x] Implémentation des Journaux d'Audit (Audit Logs) pour les actions admin.
- [x] Module de Chat inter-utilisateurs (Modération et Supervision).

### TODO 🚧
- [ ] Tests exhaustifs sur les cas limites de matching PostGIS.

## Useful Documentation
- [docs/IA_PAGE_COMMANDS.md](./docs/IA_PAGE_COMMANDS.md) : **Guide d'automatisation pour les agents IA.**
- [docs/MARKETING_MODULE.md](./docs/MARKETING_MODULE.md) : Detailed Marketing Cockpit Guide.
- [docs/WEBSITE_INTEGRATION.md](./docs/WEBSITE_INTEGRATION.md) : Guide d'intégration Klando.site.
- [docs/AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md) : AI & Architecture Guide.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Technical matching details.
