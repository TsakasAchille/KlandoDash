# Components Directory (`/src/components`)

Ce dossier regroupe tous les composants React réutilisables, organisés par module ou par type.

## Organisation

- `/ui` : Composants atomiques de base issus de **Shadcn/ui** (Button, Card, Input, Table, etc.).
- `/home` : Widgets spécifiques à la page d'accueil (KPICard, RecentSection).
- `/map` : Éléments de la carte interactive (TripMap, Popups, Filtres).
- `/trips` : Composants liés à la gestion des trajets.
- `/users` : Éléments d'affichage des listes et profils utilisateurs.
- `/support` : Interface du chat support et gestion des tickets.
- `/site-requests` : Éléments spécifiques aux demandes du site vitrine.
- `/emails` : Templates d'emails (React Email).

## Layout & Navigation

- `sidebar.tsx` : Barre de navigation principale.
- `user-menu.tsx` : Menu de profil utilisateur (avatar, rôle, déconnexion).
- `providers.tsx` : Wrappers de contextes (Auth, Theme).
- `refresh-button.tsx` : Contrôle global de revalidation des données.

## Principes

- **Style** : Utilisation de **Tailwind CSS**.
- **Icons** : Bibliothèque **Lucide React**.
- **Standard** : Respect des principes du "Clean Code" et de la séparation des responsabilités.
