# App Directory (`/src/app`)

Ce dossier contient les pages et les routes API de l'application KlandoDash, utilisant le **Next.js App Router**.

## Structure des Pages

- `/` : Tableau de bord principal (Home) avec KPIs globaux.
- `/trips` : Gestion des trajets (Liste, détails, passagers).
- `/users` : Annuaire des utilisateurs et profils détaillés.
- `/map` : Carte interactive temps réel (Trajets & Demandes).
- `/site-requests` : Intentions de voyage collectées sur le site vitrine.
- `/transactions` : Historique financier et cash flow.
- `/stats` : Statistiques avancées et graphiques.
- `/support` : Centre d'assistance et tickets.
- `/admin` : Gestion des accès dashboard et validation des documents conducteurs.
- `/login` : Authentification Google OAuth.

## Routes API (`/api`)

- `/api/admin` : Opérations réservées aux administrateurs.
- `/api/support` : Gestion des tickets et commentaires.
- `/api/trips` : Données dynamiques sur les trajets (ex: passagers).
- `/api/users` : Informations spécifiques aux utilisateurs.

## Conventions

- **Server Components** : Utilisés par défaut pour le fetch de données initiales.
- **Client Components** : Utilisés pour l'interactivité (suffixe `-client.tsx`).
- **Dynamic Routes** : Utilisation de `force-dynamic` pour garantir la fraîcheur des données administratives.
