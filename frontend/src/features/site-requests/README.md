# Site Requests Feature (SOLID Architecture)

Ce module gère l'intention de voyage des clients et leur mise en relation intelligente.

## Architecture & Services

Le module est structuré pour isoler la logique métier complexe du rendu React :

### 1. Services (Services métier)
- **`GeocodingService`** : Géocodage (Nominatim), Itinéraires (OSRM), décodage de polylines et calcul de distances Haversine (km).
- **`TripService`** : Accès Admin aux trajets. Implémente une recherche par préfixe (`ILIKE 'TRIP-XXXX%'`) pour gérer les mentions partielles par l'IA.
- **`AIMatchingService`** : Orchestre la préparation du contexte pour Gemini, incluant le calcul des km de jonction pour chaque match potentiel.
- **`prompts.ts`** : Centralise les instructions de Gemini. Définit le ton (Vouvoiement), les seuils de distance honnêtes, et le template visuel WhatsApp (🚗/🏁).

### 2. Components (UI)
- **`maps/ComparisonMap`** : Composant Leaflet pur. Affiche les polylines, les flèches directionnelles de fin de path, et les traits de jonction stylisés.
- **Auto-Direction** : Détecte et inverse dynamiquement les tracés inversés en base de données.

### 3. Workflow
1. L'admin déclenche le matching.
2. `AIMatchingService` calcule les km client <-> chauffeur.
3. Gemini génère un message WhatsApp formaté selon le template officiel.
4. `MatchingDialog` affiche les distances calculées via des badges visuels.

## Maintenance
- Pour changer les seuils de distance ou le ton : `services/prompts.ts`.
- Pour corriger une erreur de recherche d'ID : `services/trip.service.ts`.
- Pour ajuster le calcul des km : `services/geocoding.service.ts`.
