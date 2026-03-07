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
Les composants lourds (`CommunicationTab`, `MessagingTab`, `MapClient`) sont découpés en sous-composants spécialisés (List, Editor, Preview, Sidebar) isolés dans le dossier `features/`.

### 2. Centre Éditorial & Messagerie (Production Focus)
- **Espaces Dédiés** : Messagerie Directe (`/messaging`) et Social Media (`/editorial`) sont désormais séparés pour une meilleure clarté opérationnelle.
- **Interface Messagerie** : Gestion unifiée Email & WhatsApp Business avec sélecteur de canal et envoi assisté (wa.me).
- **IA Génératrice** : Suggestions mixtes (Email/WA) basées sur les nouveaux prospects et les utilisateurs inactifs.
- **Centre Social Media** : Création de posts TikTok, Instagram, LinkedIn, X avec un planificateur (Calendrier) global.

### 3. IA Data Hub & Automatisation
- **IA Data Hub (`/ia`)** : Page dédiée fournissant un flux de données brutes pour l'ingestion par des agents IA externes.
- **Pilotage par URL** : Support des paramètres `?origin=...&dest=...` pour déclencher des recherches automatiques.
- **Visual Capture Hub** : Pont Base64 permettant à l'IA d'injecter des captures d'écran Facebook directement dans le stockage Supabase pour enrichir les brouillons.
- **Rôle IA Dédié** : Nouveau profil utilisateur `ia` restreint uniquement à l'Accueil et au Hub de données.

### 4. Radar de Matching & Capture
- **Haute Fidélité** : Utilisation de `preferCanvas: true` dans Leaflet pour garantir un alignement parfait des tracés lors des captures `html2canvas`.
- **Auto-Correction** : Inversion automatique des polylines si le sens de saisie diverge du trajet conducteur.
- **Règles d'Or Leaflet (Layouts & Tabs)** : 
  1. **Toujours `forceMount`** le `TabsContent` qui contient une carte pour éviter que Leaflet s'initialise dans un conteneur à 0px (display: none). Gérer la visibilité via CSS (`hidden`).
  2. **Styles Inline** : Utiliser des `style={{ height: '75vh', display: 'grid' }}` pour les conteneurs de carte complexes afin d'empêcher le layout de s'écraser face aux conflits Tailwind/Parents (`overflow-auto`).
  3. **Pas de `key` dynamique** : Ne pas forcer le re-render du composant Map, utiliser plutôt le `ResizeObserver` intégré pour redimensionner proprement.

## Current Status

### Done ✅
- [x] Refactorisation SOLID complète.
- [x] Cockpit de Pilotage Growth (KPIs : Activation, Rétention, Liquidité).
- [x] RPC `get_pilotage_metrics` optimisée avec Focus Remplissage Réalisé.
- [x] Centre Éditorial Responsif (Navigation Mobile par piles vs Desktop colonnes).
- [x] Unification de la création Social Media (Générateur IA intégré au popup).
- [x] IA Data Hub avec pilotage par URL et pont Base64 pour images.
- [x] Support LinkedIn et Catégorie Autre dans les communications.
- [x] Migration SMTP Google (Nodemailer) pour le mailing.
- [x] Rôle `ia` avec accès restreint.
- [x] Implémentation des Journaux d'Audit (Audit Logs) pour les actions admin.
- [x] Module de Chat inter-utilisateurs (Modération et Supervision).
- [x] Tests et validation des cas limites de matching PostGIS (Direction & Waypoints).

### TODO 🚧
- [ ] Système de Notifications Desktop pour les nouveaux tickets/messages.
- [ ] Support Multi-images dans le chat de modération.
- [ ] Module de Statistiques Financières avancées (Revenus conducteurs vs Klando).
- [ ] Export PDF des rapports d'activité marketing.

## Useful Documentation
- [docs/IA_PAGE_COMMANDS.md](./docs/IA_PAGE_COMMANDS.md) : **Guide d'automatisation pour les agents IA.**
- [docs/MARKETING_MODULE.md](./docs/MARKETING_MODULE.md) : Detailed Marketing Cockpit Guide.
- [docs/WEBSITE_INTEGRATION.md](./docs/WEBSITE_INTEGRATION.md) : Guide d'intégration Klando.site.
- [docs/AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md) : AI & Architecture Guide.
- [docs/AI_MATCHING_SYSTEM.md](./docs/AI_MATCHING_SYSTEM.md) : Technical matching details.
