# Marketing Module Guide (v1.7 - AI Integrated)

## Overview
Le module marketing sépare l'analyse stratégique de la production de contenu.

### 1. Marketing Stratégique (`/marketing`)
*Focus : Analyse, Détection, Intelligence.*
- **Radar de Matching** : Scan PostGIS (max 15km) pour identifier les clients dont le trajet croise celui d'un conducteur.
- **Observatoire** : Visualisation des flux de demande (Heatmap) et des trajets récurrents.
- **Intelligence IA** : Rapports Gemini sur les opportunités de revenus et les conversions.

### 2. Centre Éditorial (`/editorial`)
*Focus : Production, Planification, Engagement.*
- **Social Media** : Création unifiée de posts TikTok, Instagram, LinkedIn, X et catégorie Autre.
- **Messagerie Directe** : Gestion des messages (Email & WhatsApp) avec suggestions IA ciblées.
- **Calendrier** : Planning global des publications et envois.

## Key Features & UI Standards

### Dual-Column Interface (Desktop)
L'espace de travail est divisé en deux zones à défilement indépendant :
- **Sidebar (320px)** : Liste des messages/posts verrouillée à gauche. Les cellules sont fixées à 110px de hauteur avec troncature du texte pour une lisibilité parfaite.
- **Espace de Production** : Zone de droite occupant tout l'espace restant, dédiée à la lecture et à l'édition.

### AI-Driven Workflow
La génération IA a été centralisée pour plus d'efficacité :
1.  **Nouveau Post** : Un clic sur "Nouveau Post" ouvre une interface de choix.
2.  **Génération Flash** : Saisissez un sujet simple, et l'IA rédige instantanément le titre, le contenu, les hashtags et suggère un visuel.
3.  **Magic Refine** : Dans l'éditeur, un bouton permet d'améliorer un texte existant par IA en un clic.

### LinkedIn & "Autre" Categories
Le Dash supporte désormais nativement LinkedIn avec des styles visuels adaptés et une catégorie "Autre" pour les communications hors-réseaux classiques.

## IA Data Hub & Automatisation
Une page dédiée (`/ia`) permet à des agents IA externes de :
- Interroger les données de trajets en temps réel.
- Injecter des captures d'écran Facebook via un pont Base64 robuste.
- Préparer des propositions directement dans le Centre Éditorial sans intervention humaine.

## Technical Structure (SOLID)
Les composants sont situés dans `src/features/marketing/components/tabs/` :
- `communication/` : PostList, PostSidebar, PostViewer, PostCompose, CommunicationMobile.
- `messaging/` : MessageSidebar, MessageList, MessageViewer, MessageCompose.
- `shared/` : InsightDetailModal, FlowMap.

## Data Statuses
- **DRAFT** : Nouveau contenu, modifiable.
- **PUBLISHED / SENT** : Contenu finalisé.
- **TRASH** : Contenu supprimé (récupérable ou suppression définitive).
