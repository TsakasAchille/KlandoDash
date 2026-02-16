# Module : Site Requests (Demandes Site)

## Description
Ce module permet de gérer les intentions de voyage soumises par les visiteurs sur le site vitrine (Landing Page). Il fait le pont entre le trafic public "non authentifié" et la modération métier du Dashboard.

## Composants Clés
- `page.tsx` : Composant serveur récupérant les données et les stats.
- `site-requests-client.tsx` : Gère les interactions client, l'état global (pagination, filtres) et l'affichage de l'analyse IA (carte + détails).
- `site-request-table.tsx` : Affichage tabulaire des demandes avec filtrage stable et intégration IA.
- `comparison-map.tsx` : Carte interactive comparant le trajet demandé par le client et la proposition de l'IA (Leaflet + OSRM + Polyline).
- `site-requests-info.tsx` : Popover d'aide expliquant le flux de travail.

## Aide IA au Matching (Amélioré)
Le module intègre un assistant IA (Gemini) pour aider à convertir les demandes clients en trajets réels.
- **Fonctionnement** : Compare la demande client avec les trajets disponibles sur le **site public** (via la vue `public_pending_trips`).
- **Réponse Structurée** : L'IA sépare sa réponse en trois sections :
    1. `[COMMENTAIRE]` : Analyse interne pour l'administrateur (choix des chauffeurs, pertinence).
    2. `[TRIP_ID]` : Identifiant technique du trajet correspondant (ex: `TRIP-123...`).
    3. `[MESSAGE]` : Texte WhatsApp prêt à l'emploi pour le client.
- **Visualisation Carte** : Si un `[TRIP_ID]` est détecté (dans la balise ou le texte), le système récupère automatiquement sa **polyline** pour l'afficher sur la carte en doré, superposée au trajet souhaité en pointillés bleus.
- **Persistance** : Les recommandations sont stockées dans les colonnes `ai_recommendation` et `ai_updated_at` de la table `site_trip_requests`.

## Flux de données
1. Le site vitrine insère une ligne dans `site_trip_requests`.
2. L'administrateur voit la demande dans ce module (statut `NEW`).
3. L'administrateur utilise l'**Aide IA** pour trouver des correspondances.
4. L'IA propose un trajet visuel (Carte) et un message pré-rédigé.
5. L'administrateur contacte le client via le message généré et change le statut en `CONTACTED` ou `REVIEWED`.

## Sécurité & Performance
- **RLS** : L'insertion est publique (rôle `anon`) mais la lecture/mise à jour est réservée aux administrateurs.
- **Stabilité** : Utilisation de `useTransition` pour les appels IA afin d'éviter les re-montages de composants et garantir la stabilité du pop-up.
- **Robustesse** : Le parseur d'ID est tolérant aux fautes de frappe et capable de récupérer les détails techniques même si l'IA oublie le formatage strict.
- **Pagination** : Gérée côté client avec un tri stable (Date + ID) pour éviter les sauts de lignes lors des mises à jour.
