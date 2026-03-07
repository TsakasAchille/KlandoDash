# Marketing Module Guide (v1.8 - Growth Consolidated)

## Overview
Le module marketing a été refondu et consolidé avec le Pilotage Growth pour créer un espace de travail unique et puissant. L'objectif est de lier directement l'analyse stratégique des flux à l'action commerciale et marketing.

### 1. Croissance & Marketing (`/admin/pilotage`)
*L'ancien module `/marketing` est désormais fusionné ici.*
- **Performance Stratégique** : Analyse des KPIs d'acquisition, de rétention, et de liquidité.
- **Prospects** : Gestion des demandes de trajets (provenant du site web ou injectées par l'IA depuis Facebook/WhatsApp).
- **Carte des Flux** : Visualisation globale des trajets agrégés en corridors épais (`flowMode`) pour identifier les axes forts et faibles.
- **CRM Actions** : Moteur d'opportunités pour réengager les conducteurs et passagers.
- **Observatoire** : Historique des requêtes et analyse des tendances géographiques.

### 2. Centre Éditorial (`/editorial`)
*Focus : Production, Planification, Engagement.*
- **Social Media** : Création unifiée de posts TikTok, Instagram, LinkedIn, X et catégorie Autre.
- **Calendrier** : Planning global des publications et envois.

### 3. Messagerie Directe (`/messaging`)
*Focus : Contacts one-to-one ciblés.*
- **Espace dédié** : Gestion des messages (Email & WhatsApp) générés par l'IA ou manuellement.
- **Markdown & Images** : Support complet du Markdown et affichage des captures d'écran contextuelles dans les brouillons.

## Key Features & UI Standards

### AI-Driven Workflow
La génération IA a été centralisée pour plus d'efficacité :
1.  **Génération Flash** : Saisissez un sujet simple, et l'IA rédige instantanément le titre, le contenu, les hashtags et suggère un visuel.
2.  **Magic Refine** : Dans l'éditeur, un bouton permet d'améliorer un texte existant par IA en un clic.
3.  **Radar PostGIS** : L'IA analyse les demandes (Prospects) et trouve les conducteurs correspondants dans un rayon de 15km.

## IA Data Hub & Automatisation (`/ia`)
Une page dédiée et sécurisée permet aux agents IA externes (scripts) de "piloter" le Dashboard :
- **Pont de Données (JSON Bridge)** : Accès direct aux variables, statistiques et contacts via `ia-raw-data`.
- **Injection de Leads (Intake)** : Les scripts IA peuvent injecter les demandes trouvées sur Facebook dans la DB.
- **Smart Search** : Recherche de conducteurs historiques basée sur la **proximité géographique** (et non plus juste textuelle).

## Technical Structure (SOLID)
Les composants sont situés dans `src/features/marketing/components/tabs/` :
- `communication/` : PostList, PostSidebar, PostViewer, PostCompose.
- `messaging/` : MessageSidebar, MessageList, MessageViewer, MessageCompose.
- `shared/` : InsightDetailModal, FlowMap.

## Data Statuses
- **DRAFT** : Nouveau contenu, modifiable.
- **PUBLISHED / SENT** : Contenu finalisé.
- **TRASH** : Contenu supprimé (récupérable ou suppression définitive).
