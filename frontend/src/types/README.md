# Types Directory (`/src/types`)

Ce dossier centralise les interfaces et types TypeScript utilisés dans toute l'application pour garantir une cohérence des données (Source of Truth).

## Principaux Types

- `trip.ts` : Modèles pour les trajets (Trip, TripDetail, TripStats).
- `user.ts` : Modèles pour les utilisateurs (UserListItem, UserDetail).
- `site-request.ts` : Modèles pour les intentions de voyage capturées sur le site.
- `transaction.ts` : Modèles pour les flux financiers.
- `support.ts` : Modèles pour les tickets support et commentaires.

## Bonnes Pratiques

- **Partage** : Toujours importer les types depuis ce dossier plutôt que de les redéfinir localement.
- **Synchronisation** : Ces types doivent refléter fidèlement la structure de la base de données Supabase définie dans `database/schema.sql`.
- **Zod (Optionnel)** : Pour les Server Actions, des schémas de validation peuvent être ajoutés pour sécuriser les inputs.
