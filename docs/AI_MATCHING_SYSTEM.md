# Système de Matching IA & Géographique (Klando)

Ce document détaille le fonctionnement technique du système de mise en relation des intentions clients avec les offres des conducteurs.

## Flux de Données Opérationnel

### 1. Collecte & Géocodage
- Les demandes sont insérées dans `site_trip_requests`.
- Un processus de géocodage serveur (`calculateAndSaveRequestRouteAction`) transforme les noms de villes en coordonnées GPS (`origin_lat`, `destination_lat`).
- Si Nominatim échoue, une étape d'affinage via Gemini est déclenchée pour isoler les quartiers/villes au Sénégal.

### 2. Scanner de Proximité (SQL Haversine)
- Le Scanner (`scanRequestMatchesAction`) utilise la fonction RPC `find_matching_trips` pour calculer les distances sphériques entre les points.
- Il enregistre les résultats persistants dans `site_trip_request_matches` avec un score de proximité.

### 3. Analyse & Message par Gemini (IA)
- Gemini reçoit le contexte de la demande + les résultats du scanner + la liste complète des trajets publics.
- **Mission** : Sélectionner le meilleur match, identifier la récurrence (jours de la semaine) et rédiger un message WhatsApp au vouvoiement.
- **Extraction Robuste** : Le système extrait l'ID technique (`TRIP-XXXX`) du texte généré pour charger les données cartographiques.

## Visualisation (Comparison Map)

La visualisation utilise une architecture stable pour éviter les erreurs Leaflet :
- **Ligne Bleue (Pointillés)** : Itinéraire théorique du client.
- **Ligne Jaune (Pleine)** : Itinéraire réel du conducteur.
- **Flèches Directionnelles** : Indiquent le sens de circulation (calculées dynamiquement sur les deux derniers points du tracé).
- **Lignes de Jonction** : Relient le client au chauffeur (Vert pour le départ, Rouge pour l'arrivée).

## Sécurité
- Utilisation du `service_role` (via `TripService`) pour garantir que l'IA peut "voir" les trajets nécessaires au matching, même si le statut du trajet est restreint par les politiques RLS standards.
