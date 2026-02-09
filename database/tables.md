# Tables Supabase - Klando

> Dernière mise à jour: 2026-02-09
> Projet: `zzxeimcchndnrildeefl` (West EU - Paris)

## Statistiques actuelles

| Table | Lignes | Notes |
|-------|--------|-------|
| `trips` | 37 | 100% ARCHIVED |
| `users` | ~50 | Avec ratings |
| `bookings` | 21 | Réservations |

---

## Tables métier principales

### `users`
Profils utilisateurs de l'application Klando.

| Colonne | Type | Description |
|---------|------|-------------|
| `uid` | text | **PK** - ID utilisateur (Firebase UID) |
| `display_name` | text | Nom affiché |
| `email` | text | Email |
| `first_name` | text | Prénom |
| `name` | text | Nom |
| `phone_number` | text | Téléphone |
| `birth` | date | Date de naissance |
| `photo_url` | text | URL photo de profil |
| `bio` | text | Biographie |
| `gender` | text | Genre |
| `rating` | numeric(3,2) | Note moyenne (ex: 4.50) |
| `rating_count` | integer | Nombre d'avis |
| `role` | text | Rôle utilisateur |
| `driver_license_url` | text | URL permis de conduire |
| `id_card_url` | text | URL carte d'identité |
| `is_driver_doc_validated` | boolean | Documents conducteur validés |
| `created_at` | timestamptz | Date création |
| `updated_at` | timestamptz | Date mise à jour |

---

### `trips`
Trajets proposés par les conducteurs.

| Colonne | Type | Description |
|---------|------|-------------|
| `trip_id` | text | **PK** - ID du trajet (ex: TRIP-1768837...) |
| `driver_id` | text | **FK → users.uid** - Conducteur |
| `departure_name` | text | Nom lieu de départ (GPS complet) |
| `departure_description` | text | Description départ (par conducteur) |
| `departure_latitude` | float | Latitude départ |
| `departure_longitude` | float | Longitude départ |
| `destination_name` | text | Nom destination (GPS) |
| `destination_description` | text | Description destination |
| `destination_latitude` | float | Latitude destination |
| `destination_longitude` | float | Longitude destination |
| `departure_date` | timestamptz | Date de départ |
| `departure_schedule` | timestamptz | Horaire de départ |
| `distance` | float | Distance en km |
| `polyline` | text | Polyline Google Maps encodé |
| `seats_published` | bigint | Places mises en ligne |
| `seats_available` | bigint | Places disponibles |
| `seats_booked` | bigint | Places réservées |
| `passenger_price` | bigint | Prix passager affiché (XOF) |
| `driver_price` | bigint | Prix conducteur reçu (XOF) |
| `status` | text | Statut: PENDING, ACTIVE, COMPLETED, ARCHIVED, CANCELLED |
| `auto_confirmation` | boolean | Confirmation auto des réservations |
| `precision` | text | Précision localisation |
| `created_at` | timestamptz | Date création |
| `updated_at` | timestamptz | Date mise à jour |

**Index créés:**
- `idx_trips_status` - Filtre par statut
- `idx_trips_departure_schedule` - Tri par date DESC
- `idx_trips_driver_id` - Jointure users
- `idx_trips_status_departure` - Combo statut + date
- `idx_trips_created_at` - Tri par création DESC

---

### `bookings`
Réservations de places sur les trajets.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | text | **PK** - ID réservation |
| `user_id` | text | **FK → users.uid** - Passager |
| `trip_id` | text | **FK → trips.trip_id** - Trajet |
| `seats` | integer | Nombre de places réservées |
| `status` | text | Statut réservation |
| `created_at` | timestamptz | Date création |
| `updated_at` | timestamptz | Date mise à jour |

---

### `chats`
Messages de conversation (liés aux trajets).

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | varchar | **PK** - ID message |
| `trip_id` | varchar | ID trajet associé |
| `sender_id` | varchar | ID expéditeur |
| `message` | varchar | Contenu du message |
| `timestamp` | timestamp | Date envoi |
| `updated_at` | timestamp | Date mise à jour |

---

### `transactions`
Transactions de paiement.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | text | **PK** - ID transaction |
| `user_id` | text | **FK → users.uid** - Utilisateur |
| `external_id` | text | ID externe (provider paiement) |
| `amount` | integer | Montant (XOF) |
| `status` | text | Statut paiement |
| `phone` | text | Téléphone |
| `service_code` | text | Code service paiement |
| `sender` | text | Expéditeur |
| `msg` | text | Message |
| `error_message` | text | Message d'erreur |
| `has_transactions` | boolean | A des transactions |
| `metadata` | jsonb | Métadonnées JSON |
| `created_at` | timestamp | Date création |
| `updated_at` | timestamp | Date mise à jour |

---

## Tables support

### `support_tickets`
| Colonne | Type | Description |
|---------|------|-------------|
| `ticket_id` | uuid | **PK** |
| `user_id` | text | **FK → users.uid** |
| `subject` | text | Sujet |
| `message` | text | Message |
| `status` | text | open, closed |
| `contact_preference` | text | mail/phone/aucun |

### `support_comments`
| Colonne | Type | Description |
|---------|------|-------------|
| `comment_id` | uuid | **PK** |
| `ticket_id` | uuid | **FK → support_tickets** |
| `user_id` | text | Auteur |
| `comment_text` | text | Texte |

---

## Tables Site Vitrine (Landing Page)

### `site_trip_requests`
Demandes d'intentions de voyage collectées via le site vitrine.

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** - `gen_random_uuid()` |
| `origin_city` | text | Ville de départ |
| `destination_city` | text | Ville d'arrivée |
| `desired_date` | timestamptz | Date souhaitée |
| `contact_info` | text | Email ou Téléphone |
| `status` | text | `NEW`, `REVIEWED`, `CONTACTED`, `IGNORED` |
| `created_at` | timestamptz | Date création |
| `notes` | text | Notes internes pour les admins |

**Index créés:**
- `idx_site_trip_requests_status`
- `idx_site_trip_requests_created_at`

---

## Vues SQL

### `public_pending_trips`
Vue sécurisée pour l'affichage des trajets `PENDING` disponibles sur le site vitrine.

| Colonne | Type | Source | Description |
|---------|------|--------|-------------|
| `id` | text | `trips.trip_id` | ID du trajet |
| `departure_city` | text | `trips.departure_name` | Ville départ |
| `arrival_city` | text | `trips.destination_name` | Ville arrivée |
| `departure_time` | timestamptz | `trips.departure_schedule` | Heure départ |
| `seats_available` | bigint | `trips.seats_available` | Places dispo |

### `public_completed_trips`
Vue sécurisée pour l'affichage des 10 derniers trajets `COMPLETED` (preuve sociale).

| Colonne | Type | Source | Description |
|---------|------|--------|-------------|
| `id` | text | `trips.trip_id` | ID du trajet |
| `departure_city` | text | `trips.departure_name` | Ville départ |
| `arrival_city` | text | `trips.destination_name` | Ville arrivée |
| `departure_time` | timestamptz | `trips.departure_schedule` | Heure départ |

---

## Tables dashboard

### `dash_authorized_users`
Utilisateurs autorisés à accéder au dashboard admin.

| Colonne | Type | Description |
|---------|------|-------------|
| `email` | varchar(255) | **PK** - Email |
| `active` | boolean | Actif |
| `role` | varchar(50) | admin, user, support |
| `display_name` | text | Nom affiché (depuis Google) |
| `avatar_url` | text | URL photo (depuis Google) |
| `added_at` | timestamp | Date d'ajout |
| `added_by` | varchar(255) | Ajouté par |
| `notes` | text | Notes |

---

## Tables IA/Embeddings

### `trip_embeddings`
Embeddings vectoriels pour recherche sémantique (pgvector).

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | uuid | **PK** |
| `trip_id` | text | **FK → trips** |
| `content` | text | Contenu textuel |
| `embedding` | vector(1536) | Vecteur OpenAI |

---

## Diagramme des relations

```
┌─────────┐
│  users  │
│   uid   │◄─────────────────────────────────┐
└────┬────┘                                  │
     │                                       │
     │ driver_id                    user_id  │
     ▼                                       │
┌─────────┐         ┌──────────┐            │
│  trips  │────────►│ bookings │────────────┘
│ trip_id │         │    id    │
└────┬────┘         └──────────┘
     │
     │ trip_id
     ▼
┌─────────┐
│  chats  │
└─────────┘
```

---

## Requêtes optimisées

### Liste trips (dashboard)
```sql
SELECT
    trip_id,
    departure_name,
    destination_name,
    departure_schedule,
    distance,
    seats_available,
    seats_published,
    passenger_price,
    status,
    driver_id
FROM trips
WHERE status = 'ACTIVE'
ORDER BY departure_schedule DESC
LIMIT 50;
```

### Trip avec conducteur
```sql
SELECT
    t.*,
    u.display_name AS driver_name,
    u.rating AS driver_rating,
    u.photo_url AS driver_photo
FROM trips t
LEFT JOIN users u ON t.driver_id = u.uid
WHERE t.trip_id = 'xxx';
```

### Stats globales
```sql
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'ACTIVE') AS active,
    SUM(distance) AS total_km,
    SUM(seats_booked) AS total_passengers
FROM trips;
```
