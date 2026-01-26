# Architecture du Module Support Technique

## 1. Vue d'ensemble

Le module de support technique de KlandoDash fournit une interface complète pour la gestion des tickets de support client. Il permet aux administrateurs de consulter les tickets, de mettre à jour leur statut et d'interagir avec les utilisateurs via un système de commentaires de type chat.

## 2. Modèle de Données

Les données du module de support sont stockées dans Supabase (PostgreSQL) et impliquent principalement les tables suivantes :

### `support_tickets`
Représente un ticket de support créé par un utilisateur de l'application.
-   `ticket_id` (PK): Identifiant unique du ticket.
-   `user_id` (FK vers `users.uid`): L'utilisateur de l'application ayant créé le ticket.
-   `subject`, `message`: Sujet et contenu initial du ticket.
-   `status`: Statut actuel du ticket (`OPEN`, `CLOSED`, `PENDING`).
-   `contact_preference`, `phone`, `mail`: Préférences et informations de contact de l'utilisateur.
-   `created_at`, `updated_at`: Horodatages.

### `support_comments`
Contient les commentaires échangés sur un ticket.
-   `comment_id` (PK): Identifiant unique du commentaire.
-   `ticket_id` (FK vers `support_tickets.ticket_id`): Le ticket auquel le commentaire est rattaché.
-   `user_id`: Identifiant de l'auteur du commentaire (e-mail de l'admin).
-   `comment_text`: Contenu du commentaire.
-   `comment_source`: Indique l'origine du commentaire (`admin`).
-   `created_at`: Horodatage.

### `dash_authorized_users`
Gère les utilisateurs autorisés à accéder au dashboard KlandoDash (administrateurs).
-   `email` (PK): E-mail de l'administrateur (utilisé comme identifiant).
-   `active`, `role`: État d'activation et rôle de l'administrateur.
-   **`display_name`**: Nom d'affichage de l'administrateur (enrichi via Google OAuth).
-   **`avatar_url`**: URL de l'avatar de l'administrateur (enrichi via Google OAuth).

### `users`
Contient les profils des utilisateurs de l'application mobile Klando.
-   `uid` (PK): Identifiant unique de l'utilisateur.
-   `display_name`, `photo_url`: Nom d'affichage et URL de la photo de profil.

## 3. Flux de Données - Récupération des Détails d'un Ticket

La récupération des détails d'un ticket, y compris ses commentaires enrichis, est gérée par une fonction RPC PostgreSQL optimisée.

```mermaid
graph TD
    A[Frontend: support-client.tsx] --> B(Appelle getTicketDetail(ticketId))
    B --> C[lib/queries/support.ts]
    C --> D(Appelle Supabase RPC: get_ticket_detail(p_ticket_id))
    D --> E{Base de données PostgreSQL}
    E --> F[Fonction get_ticket_detail]
    F -- Jointure sur support_tickets.user_id = users.uid --> G[Récupère les détails du ticket et du créateur du ticket]
    F -- Sous-requête avec jointure sur support_comments.user_id = dash_authorized_users.email --> H[Récupère les commentaires avec nom/avatar de l'admin]
    H --> I[Retourne les détails du ticket + commentaires en JSONB]
    I --> J[Frontend: Reçoit TicketDetail]
    J --> K[Composant TicketDetails: affiche tout]
```

**Points Clés :**
-   La fonction `get_ticket_detail` est la source unique pour les détails du ticket et tous ses commentaires.
-   Elle utilise une CTE (`ticket_comments`) pour agréger les commentaires.
-   Pour chaque commentaire, l'auteur (admin) est joint à `dash_authorized_users` via l'e-mail (`c.user_id = admin_user.email`) pour récupérer `display_name` et `avatar_url`.
-   Le créateur du ticket (utilisateur de l'application) est joint à la table `users`.

## 4. Flux de Données - Mise à Jour du Statut d'un Ticket

La mise à jour du statut d'un ticket est gérée via une **Next.js Server Action**.

```mermaid
graph TD
    A[Frontend: TicketDetails.tsx (client component)] --> B(Appelle updateTicketStatusAction(ticketId, newStatus))
    B --> C[Server Action: frontend/src/app/support/actions.ts]
    C --> D[lib/queries/support.ts: updateTicketStatus(ticketId, newStatus)]
    D --> E(Appelle Supabase RPC: update_ticket_status(p_ticket_id, p_status))
    E --> F{Base de données PostgreSQL}
    F --> G[Met à jour support_tickets.status et updated_at]
    G --> H[Retourne succès/échec]
    H --> C
    C -- revalidatePath('/support') --> I[Next.js: invalide le cache de la page /support]
    I --> J[Frontend: Re-fetch des données et re-rendu automatique]
```

**Points Clés :**
-   Utilisation des Server Actions pour une mutation directe côté serveur.
-   La logique de revalidation de cache (`revalidatePath`) assure que l'interface utilisateur se met à jour automatiquement après une modification.
-   La validation du statut est effectuée dans la fonction RPC `update_ticket_status` côté base de données.

## 5. Flux de Données - Ajout de Commentaires

L'ajout d'un nouveau commentaire est également géré via une fonction RPC.

```mermaid
graph TD
    A[Frontend: CommentForm.tsx (client component)] --> B(Appelle onAddComment(commentText))
    B --> C[support-client.tsx (client component)]
    C --> D[lib/queries/support.ts: addComment(ticketId, adminEmail, commentText)]
    D --> E(Appelle Supabase RPC: add_support_comment(p_ticket_id, p_user_id, p_comment_text, 'admin'))
    E --> F{Base de données PostgreSQL}
    F --> G[Insère le nouveau commentaire dans support_comments]
    G --> H[Met à jour support_tickets.updated_at]
    H --> I[Retourne l'ID du nouveau commentaire]
    I --> J[Frontend: Reçoit le nouveau commentaire]
    J --> K[support-client.tsx: met à jour l'état local du ticket pour afficher le nouveau commentaire (optimistic update)]
```

**Points Clés :**
-   Le `user_id` envoyé à `add_support_comment` est l'e-mail de l'administrateur connecté.
-   Le `comment_source` est toujours `admin` pour les commentaires du dashboard.
-   Une mise à jour optimiste côté client améliore l'expérience utilisateur.

## 6. Composants d'Interface Utilisateur (UI) Clés

-   `frontend/src/app/support/page.tsx`: Composant serveur initial qui orchestre la récupération des données pour la page support.
-   `frontend/src/app/support/support-client.tsx`: Composant client qui gère l'état de la page, la sélection des tickets, la soumission des commentaires et l'affichage des listes/détails.
-   `frontend/src/components/support/ticket-details.tsx`: Affiche les informations détaillées d'un ticket, y compris ses actions de statut et son fil de commentaires. Intègre la Server Action pour le changement de statut.
-   `frontend/src/components/support/comment-thread.tsx`: Affiche les commentaires dans un format de "chat" avec bulles et avatars d'administrateurs.
-   `frontend/src/components/support/comment-form.tsx`: Formulaire pour ajouter de nouveaux commentaires à un ticket.
-   `frontend/src/components/support/ticket-table.tsx`: Affiche la liste des tickets de support.
-   `frontend/src/components/support/ticket-status-badge.tsx`: Composant de badge pour afficher le statut d'un ticket.

## 7. Authentification et Autorisation

Les administrateurs se connectent via Google OAuth, géré par NextAuth.js.
-   Les utilisateurs autorisés sont listés dans `dash_authorized_users`.
-   Lors de la connexion, les champs `display_name` et `avatar_url` de `dash_authorized_users` sont automatiquement mis à jour à partir du profil Google.
-   Les requêtes backend utilisent `SUPABASE_SERVICE_ROLE_KEY` pour interagir avec la base de données sans restrictions RLS (Row Level Security).

## 8. Fichiers Clés

-   `database/migrations/003_support_indexes_and_functions.sql`: Fonctions RPC (`get_ticket_detail`, `update_ticket_status`, `add_support_comment`).
-   `database/migrations/004_add_profile_to_dash_authorized_users.sql`: Ajout des champs `display_name` et `avatar_url` à `dash_authorized_users`.
-   `frontend/src/lib/auth.ts`: Configuration NextAuth.js, mise à jour des profils admin.
-   `frontend/src/lib/queries/support.ts`: Fonctions pour interagir avec les RPC Supabase.
-   `frontend/src/app/support/actions.ts`: Server Actions pour les mutations du module support.
-   `frontend/src/types/support.ts`: Types TypeScript pour les entités du module support.
-   `frontend/next.config.mjs`: Configuration pour les images externes (Google avatars).