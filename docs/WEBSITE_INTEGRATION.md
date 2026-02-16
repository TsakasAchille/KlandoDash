# Guide d'Intégration Site Vitrine

Ce document décrit comment le site vitrine doit interagir avec le Dashboard pour transmettre les intentions de voyage des utilisateurs.

## 1. Soumission d'une Demande (Intent)

Lorsqu'un utilisateur effectue une recherche sur le site sans trouver de trajet, ou souhaite être alerté, le site doit insérer une demande dans la table `site_trip_requests` via Supabase.

### Table : `public.site_trip_requests`

La table est ouverte en écriture aux utilisateurs anonymes (clé publique `ANON_KEY`).

| Colonne | Type | Requis | Description |
|---|---|---|---|
| `origin_city` | text | OUI | Ville de départ (ex: "Dakar") |
| `destination_city` | text | OUI | Ville d'arrivée (ex: "Touba") |
| `desired_date` | timestamp | NON | Date/Heure souhaitée. `NULL` = "Dès que possible" |
| `contact_info` | text | OUI | Email ou Numéro de téléphone pour le recontact |
| `origin_lat` | float | **RECOMMANDÉ** | Latitude du point de départ (pour le matching géo) |
| `origin_lng` | float | **RECOMMANDÉ** | Longitude du point de départ |
| `destination_lat` | float | NON | Latitude du point d'arrivée |
| `destination_lng` | float | NON | Longitude du point d'arrivée |

### Exemple de Code (Javascript / Supabase Client)

```javascript
const { data, error } = await supabase
  .from('site_trip_requests')
  .insert([
    {
      origin_city: 'Dakar',
      destination_city: 'Mbour',
      desired_date: '2024-05-20T10:00:00Z', // ou null
      contact_info: '77 000 00 00',
      // Coordonnées pour le matching intelligent (via Google Places ou autre)
      origin_lat: 14.7167,
      origin_lng: -17.4677,
      destination_lat: 14.4167,
      destination_lng: -16.9667
    },
  ]);
```

> **Note Importante** : L'envoi des coordonnées (`lat`/`lng`) est essentiel pour activer le matching géographique de haute précision (2km, 5km, etc.) dans le dashboard. Sans elles, le matching se fera uniquement sur le nom des villes ou via une position approximative par défaut.

## 2. Affichage des Trajets "En Direct"

Pour afficher les trajets disponibles (ex: "Départs imminents"), utilisez la vue sécurisée `public_pending_trips`.

### Vue : `public.public_pending_trips`

Cette vue expose uniquement les données non sensibles des trajets en statut `PENDING`.

| Colonne | Description |
|---|---|
| `id` | Identifiant du trajet |
| `departure_city` | Ville de départ |
| `arrival_city` | Ville d'arrivée |
| `departure_time` | Date/Heure de départ |
| `seats_available` | Nombre de places restantes |
| `polyline` | Tracé encodé du trajet (pour affichage carte) |

### Exemple de requête

```javascript
const { data: trips } = await supabase
  .from('public_pending_trips')
  .select('*')
  .order('departure_time', { ascending: true })
  .limit(5);
```

## 3. Preuve Sociale (Trajets Terminés)

Pour afficher l'activité récente et rassurer les visiteurs, utilisez la vue `public_completed_trips`.

### Vue : `public.public_completed_trips`

Affiche les 10 derniers trajets terminés avec succès.

## Philosophie "Intention vs Action"

- **Le Site (Vitrine)** : Capture l'intention ("Je veux aller à..."). Il est passif sur la création de trajet mais actif sur la collecte de leads.
- **Le Dashboard (Admin)** : Analyse l'intention, utilise l'IA pour matcher avec des trajets existants (proximité géographique) ou décide d'ouvrir une nouvelle ligne si la demande est forte.
