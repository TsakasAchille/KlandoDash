# Interconnexion Trips ↔ Users

Guide d'implémentation pour lier les pages Trips et Users de manière interactive et optimisée.

## Objectif

```
┌─────────────────────────────────────────────────────────────────┐
│  /trips                                                         │
│  ┌──────────────┐    ┌────────────────────────────────────┐   │
│  │ Trip Table   │    │ Trip Details                        │   │
│  │              │    │                                      │   │
│  │ [Selected]───┼───►│ Conducteur: John Doe               │   │
│  │              │    │ [Voir profil] ──────────────────────┼───┼──► /users?selected=xxx
│  └──────────────┘    └────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  /users                                                         │
│  ┌──────────────┐    ┌────────────────────────────────────┐   │
│  │ User Table   │    │ User Details                        │   │
│  │              │    │                                      │   │
│  │ [Selected]───┼───►│ Trajets (5)                         │   │
│  │              │    │ ┌────────────────────────────────┐  │   │
│  │              │    │ │ Mini Trip Table (paginated)    │  │   │
│  │              │    │ │ [Voir trajet] ─────────────────┼──┼───┼──► /trips?selected=xxx
│  │              │    │ └────────────────────────────────┘  │   │
│  └──────────────┘    └────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Architecture

### 1. URL State Management

Utiliser les **URL Search Params** avec convention unifiée `?selected=` :
- Pré-sélectionner un élément au chargement
- Permettre le partage de liens directs
- Garder l'historique de navigation (avec `router.replace` pour éviter pollution)

```
/trips?selected=TRIP-123456     → Pré-sélectionne le trajet
/users?selected=abc123          → Pré-sélectionne l'utilisateur
```

### 2. Queries Supabase Optimisées

#### Nouvelle query : Trajets d'un utilisateur (single query)

```typescript
// lib/queries/trips.ts

/**
 * Trajets d'un conducteur (pour profil utilisateur)
 * Optimisation: count + data en une seule requête
 */
export async function getTripsByDriver(
  driverId: string,
  options: { limit?: number; offset?: number } = {}
): Promise<{ trips: TripListItem[]; total: number }> {
  const { limit = 5, offset = 0 } = options;
  const supabase = createServerClient();

  // Single query avec count intégré
  const { data, count, error } = await supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      departure_schedule,
      distance,
      seats_available,
      seats_published,
      passenger_price,
      status
    `, { count: "exact" })
    .eq("driver_id", driverId)
    .order("departure_schedule", { ascending: false })
    .range(offset, offset + limit - 1);

  if (error) {
    console.error("getTripsByDriver error:", error);
    return { trips: [], total: 0 };
  }

  return {
    trips: data as TripListItem[],
    total: count || 0,
  };
}
```

#### Index recommandé (déjà créé)
```sql
-- Déjà existant : idx_trips_driver_id
CREATE INDEX idx_trips_driver_id ON trips(driver_id);
```

### 3. Composants à Modifier/Créer

#### A. Trip Details - Ajouter lien vers profil

```typescript
// components/trips/trip-details.tsx

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";

// Dans le composant, section conducteur :
<div className="flex items-center justify-between">
  <div className="flex items-center gap-3">
    <Avatar />
    <div>
      <p className="font-medium">{trip.driver_name}</p>
      <p className="text-sm text-muted-foreground">
        {trip.driver_rating}★ ({trip.driver_rating_count} avis)
      </p>
    </div>
  </div>
  <Link href={`/users?selected=${trip.driver_id}`}>
    <Button variant="outline" size="sm">
      <ExternalLink className="w-4 h-4 mr-2" />
      Voir profil
    </Button>
  </Link>
</div>
```

#### B. User Trips Table (nouveau composant)

```typescript
// components/users/user-trips-table.tsx

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { TripListItem } from "@/types/trip";
import { formatDate, formatPrice } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";
import { ChevronLeft, ChevronRight, ExternalLink, Car } from "lucide-react";

interface UserTripsTableProps {
  userId: string;
}

export function UserTripsTable({ userId }: UserTripsTableProps) {
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const limit = 5;

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}/trips?page=${page}&limit=${limit}`)
      .then(res => res.json())
      .then(data => {
        setTrips(data.trips);
        setTotal(data.total);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [userId, page]);

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-10 bg-secondary rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Car className="w-5 h-5 text-klando-gold" />
          Trajets ({total})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {trips.length === 0 ? (
          <p className="text-muted-foreground text-sm">Aucun trajet</p>
        ) : (
          <>
            <Table>
              <TableBody>
                {trips.map(trip => (
                  <TableRow key={trip.trip_id}>
                    <TableCell className="py-2">
                      <div className="text-sm">
                        <span className="font-medium">{trip.departure_name}</span>
                        <span className="text-muted-foreground"> → </span>
                        <span className="font-medium">{trip.destination_name}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatDate(trip.departure_schedule)} · {formatPrice(trip.passenger_price)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right py-2">
                      <Link href={`/trips?selected=${trip.trip_id}`}>
                        <Button variant="ghost" size="sm">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => p - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="text-sm text-muted-foreground">
                  {page} / {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
```

#### C. API Route pour fetch client-side

```typescript
// app/api/users/[uid]/trips/route.ts

import { NextRequest, NextResponse } from "next/server";
import { getTripsByDriver } from "@/lib/queries/trips";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ uid: string }> }
) {
  const { uid } = await params;
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "5");
  const offset = (page - 1) * limit;

  const { trips, total } = await getTripsByDriver(uid, { limit, offset });

  return NextResponse.json({
    trips,
    total,
    page,
    totalPages: Math.ceil(total / limit),
  });
}
```

### 4. Page Components avec URL Params

#### Trips Page (Server Component)

```typescript
// app/trips/page.tsx

import { getTripsWithDriver, getTripById, getTripsStats } from "@/lib/queries/trips";
import { toTrip } from "@/types/trip";
import { TripsPageClient } from "./trips-client";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function TripsPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  const [tripsData, stats, selectedTripData] = await Promise.all([
    getTripsWithDriver(100),
    getTripsStats(),
    selected ? getTripById(selected) : null,
  ]);

  const trips = tripsData.map(toTrip);
  const initialSelectedTrip = selectedTripData ? toTrip(selectedTripData) : null;

  return (
    <TripsPageClient
      trips={trips}
      stats={stats}
      initialSelectedId={selected || null}
      initialSelectedTrip={initialSelectedTrip}
    />
  );
}
```

#### Trips Client Component

```typescript
// app/trips/trips-client.tsx

"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Trip } from "@/types/trip";
import { TripTable } from "@/components/trips/trip-table";
import { TripDetails } from "@/components/trips/trip-details";

interface Props {
  trips: Trip[];
  stats: TripStats;
  initialSelectedId: string | null;
  initialSelectedTrip: Trip | null;
}

// Abstraction pour scroll (future-proof pour virtualisation)
function scrollToRow(id: string, prefix: string = "trip") {
  const element = document.querySelector(`[data-${prefix}-id="${id}"]`);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    // Highlight temporaire
    element.classList.add("ring-2", "ring-klando-gold");
    setTimeout(() => {
      element.classList.remove("ring-2", "ring-klando-gold");
    }, 2000);
  }
}

export function TripsPageClient({
  trips,
  stats,
  initialSelectedId,
  initialSelectedTrip,
}: Props) {
  const router = useRouter();
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(initialSelectedTrip);

  // Sync URL on selection change (replace pour éviter pollution historique)
  const handleSelectTrip = useCallback((trip: Trip) => {
    setSelectedTrip(trip);
    router.replace(`/trips?selected=${trip.trip_id}`, { scroll: false });
  }, [router]);

  // Scroll to selected row on mount
  useEffect(() => {
    if (initialSelectedId) {
      // Petit délai pour laisser le DOM se rendre
      setTimeout(() => scrollToRow(initialSelectedId, "trip"), 100);
    }
  }, [initialSelectedId]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1">
        <TripTable
          trips={trips}
          selectedTripId={selectedTrip?.trip_id || null}
          onSelectTrip={handleSelectTrip}
        />
      </div>
      <div className="lg:col-span-2">
        {selectedTrip ? (
          <TripDetails trip={selectedTrip} />
        ) : (
          <div className="flex items-center justify-center h-64 rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">
              Sélectionnez un trajet pour voir les détails
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
```

### 5. Flow Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVIGATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User sur /trips                                             │
│     └─► Sélectionne trajet T1                                   │
│         └─► URL devient /trips?selected=T1 (replace)            │
│             └─► Détails affichent conducteur U1                 │
│                 └─► Clic "Voir profil"                          │
│                     └─► Navigation vers /users?selected=U1      │
│                                                                  │
│  2. User sur /users?selected=U1                                 │
│     └─► Table pré-sélectionne U1                                │
│         └─► Scroll automatique + highlight vers U1              │
│             └─► Détails chargent trajets de U1                  │
│                 └─► Clic "Voir trajet" sur T2                   │
│                     └─► Navigation vers /trips?selected=T2      │
│                                                                  │
│  3. User sur /trips?selected=T2                                 │
│     └─► Table pré-sélectionne T2                                │
│         └─► Scroll automatique + highlight vers T2              │
│             └─► Détails affichent T2                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6. Optimisations

| Aspect | Implémentation |
|--------|----------------|
| **Single Query** | count + data en une requête Supabase |
| **URL State** | `router.replace` au lieu de `push` (pas de pollution historique) |
| **Scroll** | Abstraction `scrollToRow()` avec highlight temporaire |
| **Pagination** | Server-side avec `range()` |
| **Indexes** | `idx_trips_driver_id` pour filtrer par conducteur |
| **Pre-fetch** | Charger selectedTrip côté serveur si ID dans URL |

### 7. Fichiers à Créer/Modifier

```
src/
├── app/
│   ├── trips/
│   │   ├── page.tsx              # Modifier: searchParams + pre-fetch
│   │   └── trips-client.tsx      # Modifier: URL sync + scrollToRow
│   ├── users/
│   │   ├── page.tsx              # Modifier: searchParams + pre-fetch
│   │   └── users-client.tsx      # Modifier: URL sync + scrollToRow
│   └── api/
│       └── users/
│           └── [uid]/
│               └── trips/
│                   └── route.ts  # NOUVEAU: API endpoint
├── components/
│   ├── trips/
│   │   └── trip-details.tsx      # Modifier: bouton profil
│   └── users/
│       ├── user-details.tsx      # Modifier: section trajets
│       └── user-trips-table.tsx  # NOUVEAU: mini table
└── lib/
    └── queries/
        └── trips.ts              # Modifier: getTripsByDriver
```
