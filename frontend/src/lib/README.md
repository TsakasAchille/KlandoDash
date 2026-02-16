# Lib Directory (`/src/lib`)

Ce dossier contient la logique métier "headless", les configurations de services et les fonctions d'accès aux données.

## Contenu

- `/queries` : **Cœur de l'application**. Contient toutes les fonctions de fetch Supabase organisées par domaine (trips, users, support, etc.).
- `supabase.ts` : Initialisation du client Supabase (Server & Browser).
- `auth.ts` : Configuration de NextAuth.js v5 (callbacks, providers, sessions).
- `gemini.ts` : Intégration de l'IA Google Gemini pour le matching et les insights.
- `utils.ts` : Fonctions utilitaires (formatage de dates, prix, fusion de classes CSS).

## Focus sur `/queries`

Toutes les requêtes sont asynchrones et typées. Elles utilisent le client Supabase avec la clé `SERVICE_ROLE` côté serveur pour bypasser les RLS administratifs si nécessaire.

Exemple d'organisation :
- `trips.ts` : Point d'entrée re-exportant depuis `/trips/index.ts`.
- `/trips/get-trips.ts` : Implémentation isolée pour le principe de responsabilité unique (SOLID).
