# Site Requests Dashboard

Cette page est le centre névralgique pour traiter les intentions de voyage capturées sur le site vitrine.

## Organisation de la Page

La page est divisée en 3 onglets principaux :
1. **Demandes Clients** : Tableau de gestion avec filtres de statut et actions rapides (Scan, IA).
2. **Carte Interactive** : Visualisation globale (`SiteRequestsMap`) permettant de voir les zones de forte demande.
3. **Aperçu Public** : Vue miroir de ce que le client voit sur le site public pour valider la cohérence.

## Gestion de l'État (Deep Linking)

L'état de la page est persisté dans l'URL pour permettre le partage direct de cas clients :
- `tab` : Gère l'onglet actif.
- `id` : Gère la demande client sélectionnée (déclenche le Focus Map ou l'ouverture du Matching IA).

## Hooks & Server Actions
- **`useSiteRequestAI`** : Gère le cycle de vie de la génération IA (chargement, parsing des balises structured, fallback TRIP-ID).
- **`actions.ts`** : Contient les Server Actions pour les mutations (Update status, Save geometry, Trigger AI).

## Composants Clés
- `MatchingDialog` : Fenêtre de recommandation IA utilisant le composant SOLID `ComparisonMap`.
- `CompactRequestsList` : Liste simplifiée utilisée dans la vue Carte pour une navigation fluide.
