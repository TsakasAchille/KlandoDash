# Module : Site Requests (Demandes Site)

## Description
Ce module permet de gérer les intentions de voyage soumises par les visiteurs sur le site vitrine (Landing Page). Il fait le pont entre le trafic public "non authentifié" et la modération métier du Dashboard.

## Composants Clés
- `page.tsx` : Composant serveur récupérant les données et les stats.
- `site-requests-client.tsx` : Gère les interactions client (mises à jour de statut).
- `site-request-table.tsx` : Affichage tabulaire des demandes avec filtrage par statut.
- `site-requests-info.tsx` : Popover d'aide expliquant le flux de travail.

## Flux de données
1. Le site vitrine insère une ligne dans `site_trip_requests`.
2. L'administrateur voit la demande dans ce module (statut `NEW`).
3. L'administrateur contacte le client et change le statut en `CONTACTED` ou `REVIEWED`.
4. Si un trajet est créé suite à cet échange, il est géré dans le module standard `/trips`.

## Sécurité
- Les données proviennent de la table `site_trip_requests`.
- L'insertion est publique (rôle `anon`) mais la lecture est strictement réservée aux utilisateurs authentifiés du dashboard.
