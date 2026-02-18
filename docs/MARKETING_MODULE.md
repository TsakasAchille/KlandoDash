# Marketing Module Guide (v1.6 - SOLID Refactor)

## Overview
Le module marketing est divisé en deux domaines distincts pour séparer la réflexion stratégique de la production de contenu.

### 1. Marketing Stratégique (`/marketing`)
*Focus : Analyse, Détection, Intelligence.*
- **Radar de Matching** : Scan PostGIS (max 15km) pour identifier les clients dont le trajet croise celui d'un conducteur.
- **Observatoire** : Visualisation des flux de demande (Heatmap) et des trajets récurrents.
- **Intelligence IA** : Rapports périodiques Gemini sur les opportunités de revenus et les conversions.

### 2. Centre Éditorial (`/editorial`)
*Focus : Production, Planification, Engagement.*
- **Social Media** : Création de posts TikTok, Instagram, X via IA ou manuelle.
  - **Mode Visuel** : Optimisé pour les affiches PNG (texte masqué).
  - **Mode Standard** : Texte optimisé par IA (Magic Fix).
- **Mailing** : Gestion des brouillons automatisés avec capture de carte.
- **Calendrier** : Planning par Drag & Drop des publications.

## Key Features & UI Standards

### Production Focus Interface
L'espace de travail est conçu pour éliminer le scroll :
- **Header Sticky** : Statistiques et navigation toujours visibles.
- **Split View** : Liste à gauche (320px), Travail à droite (Flexible).
- **Fixed Height** : Zone de travail fixée à 750px pour une visibilité totale sans défilement.

### IA Radar Workflow
1.  **Inspiration** : Les 3 meilleurs angles stratégiques s'affichent en haut du générateur.
2.  **Génération** : Un clic sur "Utiliser ce thème" lance la rédaction IA.
3.  **Validation** : Le post est automatiquement ajouté aux brouillons et sélectionné pour prévisualisation.

### Map Capture Excellence
Les captures de trajets envoyées aux clients via mail sont garanties sans décalage (offset fix) grâce à :
- `preferCanvas: true` dans Leaflet.
- Délai de rendu de 300ms avant capture.
- Dimensions de capture alignées sur le conteneur réel.

## Technical Structure (SOLID)
Les composants sont situés dans `src/features/marketing/components/tabs/` :
- `communication/` : PostList, PostEditor, PostPreview, AIGenerator, IdeasGrid.
- `mailing/` : MailSidebar, MailList, MailViewer, MailCompose.
- `shared/` : InsightDetailModal, FlowMap.

## Data Statuses
- **DRAFT** : Nouveau contenu, modifiable.
- **PUBLISHED / SENT** : Contenu finalisé.
- **TRASH** : Contenu supprimé (récupérable ou suppression définitive).
- **NEW** (Legacy) : Automatiquement traité comme DRAFT dans l'interface.
