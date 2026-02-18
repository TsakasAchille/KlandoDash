# Tables Supabase - Klando

> Dernière mise à jour: 2026-02-16
> Projet: `zzxeimcchndnrildeefl` (West EU - Paris)

## Statistiques de production (Constatées)

| Table | Lignes | Notes |
|-------|--------|-------|
| `users` | 676 | Profils Firebase migrés |
| `trips` | 37 | Historique des trajets |
| `bookings` | 21 | Réservations confirmées |
| `transactions` | 4 | Flux financiers Integrapay |

---

## Tables métier principales

### `users`
Profils utilisateurs synchronisés depuis Firebase.

| Colonne | Type | Description |
|---------|------|-------------|
| `uid` | text | **PK** - ID unique Firebase |
| `display_name` | text | Nom d'affichage complet |
| `email` | text | Adresse email |
| `phone_number` | text | Numéro de téléphone international |
| `birth` | date | Date de naissance (pour profil type) |
| `gender` | text | Genre: `man`, `woman`, `unknown` |
| `photo_url` | text | URL de l'image de profil (Storage/Google) |
| `bio` | text | Biographie courte |
| `role` | text | `user` ou `driver` |
| `rating` | numeric | Note moyenne (ex: 4.81) |
| `rating_count` | integer | Nombre total d'avis reçus |
| `is_driver_doc_validated` | boolean | Statut de validation admin des documents |
| `driver_license_url` | text | Scan du permis de conduire |
| `id_card_url` | text | Scan de la carte d'identité |
| `created_at` | timestamptz | Date d'inscription |
| `updated_at` | timestamptz | Dernière modification |

---

### `trips`
Trajets de covoiturage.

| Colonne | Type | Description |
|---------|------|-------------|
| `trip_id` | text | **PK** - Format `TRIP-XXXXXX` |
| `driver_id` | text | **FK → users.uid** |
| `status` | text | `PENDING`, `ACTIVE`, `STARTED`, `COMPLETED`, `CANCELLED`, `ARCHIVED` |
| `departure_name` | text | Ville/Lieu de départ (ex: "Dakar, Sénégal") |
| `destination_name` | text | Ville/Lieu d'arrivée |
| `departure_schedule` | timestamptz | Date et heure de départ prévues |
| `distance` | float | Distance calculée en km |
| `polyline` | text | Tracé de l'itinéraire (Encoded Polyline) |
| `seats_published` | bigint | Capacité totale du véhicule |
| `seats_available` | bigint | Places restant à vendre |
| `seats_booked` | bigint | Places déjà réservées |
| `passenger_price` | bigint | Prix payé par le passager (XOF) |
| `driver_price` | bigint | Somme perçue par le conducteur (XOF) |
| `auto_confirmation` | boolean | Acceptation auto des passagers |
| `departure_latitude` | float | Coordonnées GPS départ |
| `departure_longitude` | float | |
| `destination_latitude` | float | Coordonnées GPS arrivée |
| `destination_longitude` | float | |
| `created_at` | timestamptz | Date de publication |

---

### `bookings`
Lien entre passagers et trajets.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | text | **PK** - ID réservation |
| `user_id` | text | **FK → users.uid** (Passager) |
| `trip_id` | text | **FK → trips.trip_id** |
| `transaction_id` | text | **FK → transactions.id** (Optionnel) |
| `seats` | integer | Nombre de places prises |
| `status` | text | `CONFIRMED`, `COMPLETED`, `CANCELLED` |
| `created_at` | timestamptz | Date de réservation |

---

### `transactions`
Suivi des paiements Integrapay.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | text | **PK** - ID unique Klando |
| `user_id` | text | **FK → users.uid** |
| `intech_transaction_id` | text | ID retourné par Integrapay |
| `amount` | integer | Montant total en XOF |
| `status` | text | `SUCCESS`, `FAILED`, `PENDING` |
| `type` | text | `TRIP_PAYMENT`, `DRIVER_PAYMENT` |
| `code_service` | text | **Vérifié** : Type de flux (`XXXXX_CASH_IN` / `XXXXX_CASH_OUT`) |
| `phone` | text | Téléphone utilisé pour le paiement |
| `msg` | text | Message de retour provider |
| `created_at` | timestamp | Date de transaction |

---

### `site_trip_requests`
Demandes d'intentions collectées sur le site vitrine.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** - `gen_random_uuid()` |
| `origin_city` | text | Ville de départ saisie |
| `destination_city` | text | Ville d'arrivée saisie |
| `desired_date` | timestamptz | Date souhaitée par le client |
| `contact_info` | text | Téléphone ou WhatsApp |
| `status` | text | `NEW`, `REVIEWED`, `CONTACTED`, `IGNORED` |
| `ai_recommendation` | text | Analyse et matching générés par Gemini |
| `origin_lat` | float | Latitude départ (Géocodée auto) |
| `origin_lng` | float | |
| `destination_lat` | float | Latitude arrivée (Géocodée auto) |
| `destination_lng` | float | |
| `polyline` | text | Tracé théorique pour affichage carte |

---

## Tables Marketing & Éditorial

### `dash_marketing_communications`
Publications sociales et idées de contenu.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** |
| `type` | comm_type | `IDEA` ou `POST` |
| `platform` | platform | `TIKTOK`, `INSTAGRAM`, `X`, `GENERAL` |
| `title` | text | Titre du post ou de l'idée |
| `content` | text | Corps du texte (Markdown) |
| `hashtags` | text[] | Liste de hashtags suggérés |
| `visual_suggestion`| text | Description du visuel idéal |
| `status` | text | `NEW`, `DRAFT`, `PUBLISHED`, `TRASH` |
| `scheduled_at` | timestamptz | Date de planification calendrier |
| `image_url` | text | Lien vers le visuel final (Storage) |
| `created_at` | timestamptz | |

### `dash_marketing_emails`
Brouillons et historique du mailing direct.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** |
| `recipient_email` | text | Email de la cible |
| `subject` | text | Sujet du mail |
| `content` | text | Corps du mail (HTML/Markdown) |
| `status` | text | `DRAFT`, `SENT`, `FAILED` |
| `image_url` | text | Capture de carte intégrée |
| `sent_at` | timestamptz | |

### `dash_marketing_comments`
Discussion interne entre dashboard users.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** |
| `comm_id` | uuid | **FK → dash_marketing_communications** |
| `email_id` | uuid | **FK → dash_marketing_emails** |
| `user_email` | text | **FK → dash_authorized_users.email** |
| `content` | text | Texte du commentaire |
| `created_at` | timestamptz | |

---

## Fonctions RPC (Calculs Optimisés)

### `get_klando_stats_final()`
- **Utilité** : Calcule TOUTES les stats du dashboard en 1 seule requête (RAM Friendly).
- **Sécurité** : `SECURITY DEFINER` (Ignore RLS pour les totaux globaux).
- **Structure de retour** : JSON structuré (Trips, Users, Bookings, Transactions, Revenue, Cashflow).

---

## Vues SQL (Interface Site Vitrine)

### `public_pending_trips`
Expose les trajets `PENDING` futurs avec places disponibles. Utilisée par l'agent IA du site pour répondre aux clients.

### `public_completed_trips`
Expose les 10 derniers trajets terminés pour la "Preuve Sociale" sur la landing page.
