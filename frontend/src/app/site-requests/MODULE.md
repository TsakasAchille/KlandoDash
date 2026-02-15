# Module : Site Requests (Demandes Site)

## Description
Ce module permet de gérer les intentions de voyage soumises par les visiteurs sur le site vitrine (Landing Page). Il fait le pont entre le trafic public "non authentifié" et la modération métier du Dashboard.

## Composants Clés
- `page.tsx` : Composant serveur récupérant les données et les stats.
- `site-requests-client.tsx` : Gère les interactions client et l'état global (pagination, filtres).
- `site-request-table.tsx` : Affichage tabulaire des demandes avec filtrage stable et intégration IA.
- `site-requests-info.tsx` : Popover d'aide expliquant le flux de travail.

## Aide IA au Matching
Le module intègre un assistant IA (Gemini) pour aider à convertir les demandes clients en trajets réels.
- **Fonctionnement** : Compare la demande client avec les trajets actifs/en attente en base de données.
- **Réponse Structurée** : L'IA sépare sa réponse en deux sections :
    1. `[COMMENTAIRE]` : Analyse interne pour l'administrateur (choix des chauffeurs, pertinence).
    2. `[MESSAGE]` : Texte WhatsApp prêt à l'emploi pour le client.
- **Persistance** : Les recommandations sont stockées dans les colonnes `ai_recommendation` et `ai_updated_at` de la table `site_trip_requests`.

## Flux de données
1. Le site vitrine insère une ligne dans `site_trip_requests`.
2. L'administrateur voit la demande dans ce module (statut `NEW`).
3. L'administrateur utilise l'**Aide IA** pour trouver des correspondances.
4. L'administrateur contacte le client via le message généré et change le statut en `CONTACTED` ou `REVIEWED`.

## Sécurité & Performance
- **RLS** : L'insertion est publique (rôle `anon`) mais la lecture/mise à jour est réservée aux administrateurs.
- **Stabilité** : Utilisation de `useTransition` pour les appels IA afin d'éviter les re-montages de composants et garantir la stabilité du pop-up.
- **Pagination** : Gérée côté client avec un tri stable (Date + ID) pour éviter les sauts de lignes lors des mises à jour.
