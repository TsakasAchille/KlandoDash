# Système de Matching IA & Géographique (Klando)

Ce document détaille le fonctionnement technique du système de mise en relation des intentions clients avec les offres des conducteurs.

## Flux de Données Opérationnel

### 1. Collecte & Géocodage
- Les demandes sont insérées dans `site_trip_requests`.
- Un processus de géocodage serveur transforme les noms de villes en coordonnées GPS (`origin_lat`, `destination_lat`).
- Si Nominatim échoue, une étape d'affinage via Gemini est déclenchée pour isoler les quartiers/villes au Sénégal.

### 2. Analyse & Matching (SOLID Services)
- **Calcul de Proximité** : Le `GeocodingService` calcule les distances Haversine réelles entre le client et chaque trajet conducteur potentiel.
- **Orchestration IA** : Le `AIMatchingService` prépare un contexte riche incluant ces distances (en km) pour Gemini.
- **Stratégie de Rédaction** : Gemini utilise des prompts centralisés (`prompts.ts`) pour adapter son ton à la distance réelle (ex: "Tout proche" vs "Option solide bien que plus éloignée").

### 3. Extraction & Chargement
- **Extraction Robuste** : Le système extrait l'ID technique (`TRIP-XXXX`) du texte de l'IA, même s'il est partiel ou mal formaté.
- **TripService (Admin)** : Utilise le client admin pour charger les détails complets (polyline, places) via une recherche par préfixe insensible à la casse.

## Visualisation (Comparison Map)

La visualisation utilise une architecture "Dumb Component" pour une stabilité maximale :
- **Ligne Bleue (Pointillés)** : Itinéraire théorique du client calculé à la volée.
- **Ligne Jaune (Pleine)** : Itinéraire réel du conducteur (Polyline DB).
- **Flèches Directionnelles** : Une flèche stylisée à la fin de chaque tracé indique le sens de circulation.
- **Auto-Correction** : Le système inverse automatiquement les polylines si elles sont enregistrées en sens inverse par rapport aux points de départ/arrivée officiels.
- **Lignes de Jonction** : Relient le client au chauffeur (Vert pour le départ, Rouge pour l'arrivée).

## Sécurité & Performance
- **Bypass RLS** : Utilisation du `service_role` pour garantir que l'IA voit les trajets nécessaires.
- **Stabilité Leaflet** : Utilisation de `invalidateSize` et suppression des animations sur `fitBounds` pour éviter les erreurs de positionnement DOM (`_leaflet_pos`).
