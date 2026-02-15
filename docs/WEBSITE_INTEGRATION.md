# Guide d'Intégration : Affichage & Collecte (Site Vitrine)

Ce document détaille comment le site vitrine interagit avec la base de données Klando pour afficher l'activité et collecter les besoins des utilisateurs.

## 1. Affichage de l'activité (Lecture) 🚗

Utilisez la vue `public_pending_trips` pour montrer les trajets en attente. Cette vue inclut désormais la **polyline** pour afficher le tracé sur une carte.

```typescript
// Récupérer les 5 prochains départs avec tracé carte
const { data, error } = await supabase
  .from('public_pending_trips')
  .select('id, departure_city, arrival_city, departure_time, seats_available, polyline')
  .order('departure_time', { ascending: true })
  .limit(5);
```

### Champs disponibles dans la vue
* `id` : Identifiant unique du trajet.
* `departure_city` : Ville de départ.
* `arrival_city` : Ville d'arrivée.
* `departure_time` : Date et heure du départ.
* `seats_available` : Nombre de places restantes.
* `polyline` : Tracé de l'itinéraire (format Google Encoded Polyline).
* `destination_latitude` / `destination_longitude` : Coordonnées précises de l'arrivée.

---

## 2. Collecte d'intention (Écriture) ✍️

Lorsqu'un visiteur remplit le formulaire "Vous voulez aller quelque part ?", vous devez insérer les données dans la table `site_trip_requests`. 

Le préfixe `site_` garantit que cette donnée est traitée comme une intention à modérer dans le Dashboard.

### Schéma de données

| Champ | Type | Description |
| :--- | :--- | :--- |
| `origin_city` | `string` | Ville de départ (obligatoire) |
| `destination_city` | `string` | Ville d'arrivée (obligatoire) |
| `contact_info` | `string` | Email ou Téléphone (obligatoire) |
| `desired_date` | `ISO Date` | Date souhaitée (optionnel) |

### Exemple d'implémentation (React)

```typescript
async function submitTripRequest(formData: {
  origin: string;
  destination: string;
  contact: string;
  date?: string;
}) {
  const { error } = await supabase
    .from('site_trip_requests')
    .insert([
      {
        origin_city: formData.origin,
        destination_city: formData.destination,
        contact_info: formData.contact,
        desired_date: formData.date || null,
        status: 'NEW' // Défini par défaut en DB
      }
    ]);

  if (error) {
    throw new Error("Impossible d'envoyer votre demande.");
  }
}
```

### Recommandations UX
1.  **Confirmation** : Affichez un message du type : *"Merci ! Nous avons bien reçu votre demande. Un conducteur vous contactera si un trajet correspond."*
2.  **Validation** : Vérifiez que `contact_info` ressemble à un email ou à un numéro de téléphone valide avant l'envoi.

---

## 🛠 Configuration Supabase

Les accès sont déjà configurés pour la clé anonyme :
*   `SELECT` autorisé sur `public_pending_trips`.
*   `INSERT` autorisé sur `site_trip_requests`.

```env
NEXT_PUBLIC_SUPABASE_URL=https://<votre-project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<votre-anon-key>
```

## 📚 Ressources Techniques Supplémentaires

Pour une inspection détaillée du schéma et des exemples de données réelles, vous pouvez vous référer au fichier de diagnostic suivant dans le dépôt du Dashboard :
`supabase/Supabase Snippet Klando Schema & Data Inspection.csv`

Ce fichier contient un export des structures de tables et des relations pour faciliter le mapping de vos composants.
