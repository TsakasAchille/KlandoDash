# Spécifications de la Page Carte (Live Map)

## Vue d'ensemble
La page Carte (`/map`) est un outil de pilotage stratégique permettant de visualiser simultanément l'offre (trajets conducteurs) et la demande (intentions de voyage clients) en temps réel. Elle offre une interface immersive et interactive pour faciliter le matching et le suivi de la flotte.

## Fonctionnalités Clés

### 1. Visualisation Interactive
- **Fond de carte "Voyager"** : Utilisation du style CartoDB Voyager pour une esthétique moderne et épurée (mode clair).
- **Trajets Conducteurs** : 
  - Affichage des polylines décodées.
  - Code couleur cyclique pour distinguer les itinéraires superposés.
  - Marqueurs de départ (vert) et d'arrivée (rouge) sur le trajet sélectionné.
- **Demandes Clients** :
  - Marqueurs violets en forme de losange pour les intentions de voyage.
  - **Système de repli** : Si les coordonnées GPS sont absentes, les demandes sont positionnées approximativement autour de Dakar avec un avertissement "Position approximative".

### 2. Filtrage Avancé (Tiroir Latéral)
Un panneau de filtres escamotable (Slide-over) permet de configurer l'affichage :
- **Toggle "Demandes Clients"** : Afficher/Masquer les intentions de voyage (Activé par défaut).
- **Statut du trajet** : Filtrer par état (Actif, En attente, Terminé, Annulé).
- **Conducteur** : Sélectionner un conducteur spécifique.
- **Période** : Filtrer les trajets par plage de dates de départ.

### 3. Interface Responsive & Hybride
- **Mobile First** : 
  - Système d'onglets "Carte" / "Activité" pour basculer entre la vue map et la liste.
  - Panneau de détails overlay en bas d'écran.
- **Desktop** : 
  - Layout double panneau : Liste d'activité à gauche (fixe), Carte à droite (fluide).
  - Contrôles flottants pour maximiser l'espace cartographique.

### 4. Liste d'Activité (Recent Trips)
- Affiche les 15 derniers trajets correspondants aux filtres.
- **Switcher de Visibilité** : "Afficher Tout" (tous les trajets filtrés) vs "Dernier Seul" (focus sur le plus récent).
- **Interactions** :
  - Survol : Met en évidence le trajet sur la carte.
  - Clic : Centre la carte sur le trajet et ouvre les détails.
  - Toggle (Oeil) : Masquer/Afficher un trajet individuel.

## Architecture Technique

### Composants
- `MapPage` (Server) : Charge les données initiales (Trips, Stats, Drivers, SiteRequests).
- `MapClient` (Client) : Orchestrateur principal, gère l'état global et les routes.
- `TripMap` (Client) : Rendu Leaflet, gestion des layers et des événements map.
- `TripMapPopup` (Client) : Carte d'information détaillée pour un trajet sélectionné.
- `MapFilters` (Client) : Formulaire de filtres dans le tiroir latéral.
- `RecentTripsTable` (Client) : Liste latérale interactive.

### Hooks Personnalisés (SOLID)
Pour maintenir `MapClient` propre et maintenable, la logique est découpée :
- `useMapFilters` : Gestion des critères de filtrage et du filtrage des données brutes.
- `useMapSelection` : Gestion de la sélection active et de la synchronisation URL.
- `useMapUI` : Gestion des états d'interface (tabs, sidebar, hover, visibility).

### Performance
- **Dynamic Imports** : Leaflet est chargé dynamiquement (`ssr: false`) pour éviter les erreurs de build.
- **Optimisation des Requêtes** : Chargement des passagers à la demande avec déduplication (ref `lastFetchedPassengersId`) pour éviter les boucles infinies.
- **Forced Dynamic** : Les routes API sont forcées en mode dynamique pour garantir la fraîcheur des données.

## Prochaines Étapes
- Intégrer les coordonnées réelles pour les demandes clients (via mise à jour site vitrine).
- Ajouter un filtrage par zone géographique (bounding box).
- Implanter le clustering pour les marqueurs de demandes si leur nombre devient important.
