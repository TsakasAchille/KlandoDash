# KlandoDash Data Flow & UI Mapping

This document details the relationship between the database (Tables/Views) and the Frontend (Pages/Queries).

## 1. Database Entities vs UI Modules

| Database Entity | Type | UI Module | Frontend Path | Description |
| :--- | :--- | :--- | :--- | :--- |
| `trips` | Table | **Trajets** | `/trips` | Full management (Admin). Shows all statuses. |
| `public_pending_trips` | View | **Site Requests** | `/site-requests` | Used by AI Matching & Landing Page. Only `PENDING` with seats. |
| `site_trip_requests` | Table | **Site Requests** | `/site-requests` | Intentions collected from the landing page. |
| `site_trip_request_matches`| Table | **Site Requests** | `/site-requests` | Persistent results from the proximity scanner. |
| `users` | Table | **Utilisateurs** | `/users` | User profiles and driver documentation. |
| `support_tickets` | Table | **Support** | `/support` | Chat-like interface for user issues. |
| `transactions` | Table | **Transactions**| `/transactions` | Financial flows (Integrapay). |

## 2. File Structure & Responsibilities

```text
frontend/src/
├── app/
│   ├── site-requests/          # Uses public_pending_trips for matching
│   │   ├── actions.ts          # Server actions for AI Matching (Gemini)
│   │   ├── site-requests-client.tsx # Main dashboard for intentions
│   │   └── components/
│   │       ├── MatchingDialog.tsx  # Logic for AI recommendation (Popup principal)
│   │       ├── SiteRequestsMap.tsx # Visualizes matches on Leaflet (Grande carte)
│   │       └── MatchedTripsList.tsx # List of found trips for a request
├── components/
│   ├── site-requests/
│   │   └── comparison-map.tsx  # Mini-carte de comparaison (Demande vs Offre) dans le MatchingDialog
│   └── map/
│       └── trip-map.tsx        # Composant carte partagé (Leaflet)
├── lib/
│   └── queries/
│       ├── site-requests.ts    # getPublicPendingTrips() -> View: public_pending_trips
│       └── trips/              # getTrips() -> Table: trips
```

## 3. The "Site Requests" Logic Flow

1. **Collection**: Landing page inserts into `site_trip_requests`.
2. **Analysis**: Admin opens `/site-requests`.
3. **Geocoding**: `actions.ts -> calculateAndSaveRequestRouteAction` (uses Nominatim + AI refinement).
4. **Scanning**: `actions.ts -> scanRequestMatchesAction` (uses SQL RPC to find proximity in `public_pending_trips`).
5. **AI Recommendation**: `actions.ts -> getAIMatchingAction` (uses Gemini to compare the request with `public_pending_trips`).
6. **Comparison UI**: `MatchingDialog` uses `ComparisonMap` to show the distance between the customer's wish and the driver's actual route.

---
*Note: Always use the `public_pending_trips` view for any customer-facing or "traction" logic to ensure we only propose bookable trips.*
