# KlandoDash Frontend

Dashboard Next.js pour Klando - Service de covoiturage au Sénégal.

## Stack technique

- **Framework**: Next.js 14 (App Router)
- **UI**: Shadcn/ui + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Language**: TypeScript

## Installation

```bash
npm install
```

## Configuration

Créer `.env.local` :

```env
NEXT_PUBLIC_SUPABASE_URL=https://zzxeimcchndnrildeefl.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role_key>
```

## Développement

```bash
npm run dev
```

Ouvrir http://localhost:3000

## Production

```bash
npm run build
npm run start
```

## Structure

```
src/
├── app/                    # Routes (App Router)
│   ├── layout.tsx         # Layout principal + sidebar
│   ├── page.tsx           # Accueil
│   └── trips/
│       ├── page.tsx       # Server Component (fetch data)
│       └── trips-client.tsx  # Client Component (interactivité)
│
├── components/
│   ├── sidebar.tsx        # Navigation
│   ├── ui/                # Composants Shadcn
│   └── trips/
│       ├── trip-table.tsx    # Tableau des trajets
│       └── trip-details.tsx  # Détails d'un trajet
│
├── lib/
│   ├── supabase.ts        # Client Supabase
│   ├── queries/
│   │   └── trips.ts       # Requêtes optimisées
│   └── utils.ts           # Helpers (formatDate, formatPrice...)
│
└── types/
    └── trip.ts            # Types TypeScript
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Server Component                      │
│  (page.tsx)                                             │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐           │
│  │ getTripsWithDriver │   │ getTripsStats │           │
│  └────────┬────────┘    └────────┬────────┘           │
│           │                      │                     │
│           └──────────┬───────────┘                     │
│                      ▼                                 │
│              Supabase (PostgreSQL)                     │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼ données
┌─────────────────────────────────────────────────────────┐
│                    Client Component                      │
│  (trips-client.tsx)                                     │
│                                                         │
│  ┌──────────────┐         ┌──────────────────┐        │
│  │  TripTable   │ ──────► │   TripDetails    │        │
│  │ (sélection)  │         │  (affichage)     │        │
│  └──────────────┘         └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Requêtes Supabase

Les requêtes sont optimisées (colonnes spécifiques, pas de `SELECT *`) :

```typescript
// Liste des trajets avec conducteur
const trips = await getTripsWithDriver(limit);

// Détail d'un trajet
const trip = await getTripById(tripId);

// Statistiques
const stats = await getTripsStats();
```

## Thème Klando

| Couleur | Hex | Usage |
|---------|-----|-------|
| Gold | `#EBC33F` | Accents, titres |
| Burgundy | `#7B1F2F` | États sélectionnés |
| Dark | `#081C36` | Fonds |

## Pages

| Route | Description | Status |
|-------|-------------|--------|
| `/` | Accueil | ✅ |
| `/trips` | Liste et détails trajets (pagination 5/page, filtre statut) | ✅ |
| `/users` | Liste utilisateurs (pagination 10/page, filtre rôle) | ✅ |
| `/stats` | Dashboard statistiques | ✅ |
| `/chats` | Messages | 🚧 À faire |

## TODO

- [ ] Page messages/chats
