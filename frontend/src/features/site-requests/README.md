# Site Requests Feature (SOLID Architecture)

Ce module gère l'intention de voyage des clients collectée via le site vitrine et leur mise en relation (matching) avec les trajets existants.

## Architecture

Le module suit les principes **SOLID** pour garantir la robustesse en production :

### 1. Services (Logique Métier Pure)
- **`GeocodingService`** : Isolate toutes les interactions avec les APIs externes (Nominatim pour le géocodage, OSRM pour le calcul d'itinéraires). Gère également le décodage des polylines et le calcul des vecteurs directionnels (flèches).
- **`TripService`** : Service d'accès aux données des trajets. Utilise le client `admin` pour bypasser les RLS lors des opérations de matching et implémente une logique de recherche d'ID robuste (insensibilité à la casse, gestion des préfixes `TRIP-`).

### 2. Components (UI)
- **`maps/ComparisonMap`** : Composant de visualisation "pur". Il ne contient aucune logique de fetch. Il reçoit des coordonnées et des polylines déjà prêtes et s'occupe uniquement du rendu Leaflet.
- **Auto-Correction de Sens** : Le composant détecte automatiquement si une polyline est inversée par rapport aux points de départ/arrivée officiels et corrige le tracé avant affichage.

### 3. Workflow de Matching
1. **Extraction** : L'IA Gemini identifie un trajet potentiel.
2. **Action Serveur** : `getAIMatchingAction` extrait l'ID et utilise `TripService` pour récupérer la géométrie complète.
3. **Visualisation** : `MatchingDialog` calcule l'itinéraire client et passe l'ensemble à la `ComparisonMap`.

## Maintenance
- Pour modifier la logique de calcul d'itinéraire : `services/geocoding.service.ts`.
- Pour ajuster le rendu de la carte : `components/maps/ComparisonMap.tsx`.
