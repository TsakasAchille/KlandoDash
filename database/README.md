# Database - KlandoDash

Configuration et documentation de la base Supabase.

## Structure

```
database/
├── schema.sql              # Schema complet (dump Supabase)
├── tables.md               # Documentation des tables
├── migrations/
│   └── 001_trips_indexes.sql   # Index optimisés
├── queries/
│   ├── trips_queries.sql   # Fonctions SQL
│   └── views.sql           # Vues pré-jointes
└── tests/
    └── test.js             # Tests des requêtes
```

## Connexion

**Projet Supabase:** `zzxeimcchndnrildeefl` (West EU - Paris)

```bash
# Lier le projet
npx supabase link --project-ref zzxeimcchndnrildeefl

# Pousser les migrations
npx supabase db push

# Dump le schema
npx supabase db dump --schema public -f schema.sql
```

## Tests

```bash
cd tests
SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co \
SUPABASE_SERVICE_ROLE_KEY=xxx \
node test.js
```

## Tables principales

| Table | Rows | Description |
|-------|------|-------------|
| `users` | ~50 | Profils utilisateurs |
| `trips` | 37 | Trajets |
| `bookings` | 21 | Réservations |
| `transactions` | - | Paiements |

## Index créés (trips)

- `idx_trips_status`
- `idx_trips_departure_schedule`
- `idx_trips_driver_id`
- `idx_trips_status_departure`
- `idx_trips_created_at`

## RLS

Actuellement **désactivé** sur `trips` - le dashboard utilise `service_role` key.
