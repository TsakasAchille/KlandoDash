// Type complet depuis Supabase
export interface TripRow {
  trip_id: string;
  driver_id: string | null;
  departure_name: string | null;
  departure_description: string | null;
  departure_latitude: number | null;
  departure_longitude: number | null;
  destination_name: string | null;
  destination_description: string | null;
  destination_latitude: number | null;
  destination_longitude: number | null;
  departure_date: string | null;
  departure_schedule: string | null;
  distance: number | null;
  polyline: string | null;
  seats_published: number | null;
  seats_available: number | null;
  seats_booked: number | null;
  passenger_price: number | null;
  driver_price: number | null;
  status: string | null;
  auto_confirmation: boolean | null;
  precision: string | null;
  created_at: string;
  updated_at: string | null;
}

// Type pour la liste (colonnes minimales)
export interface TripListItem {
  trip_id: string;
  departure_name: string | null;
  destination_name: string | null;
  departure_schedule: string | null;
  distance: number | null;
  seats_available: number | null;
  seats_published: number | null;
  passenger_price: number | null;
  status: string | null;
  driver_id: string | null;
}

// Type pour les détails avec infos conducteur
export interface TripDetail extends TripListItem {
  departure_description: string | null;
  departure_latitude: number | null;
  departure_longitude: number | null;
  destination_description: string | null;
  destination_latitude: number | null;
  destination_longitude: number | null;
  polyline: string | null;
  seats_booked: number | null;
  driver_price: number | null;
  auto_confirmation: boolean | null;
  created_at: string | null;
  // Driver info (joined)
  driver_name: string | null;
  driver_photo: string | null;
  driver_phone: string | null;
  driver_rating: number | null;
  driver_rating_count: number | null;
  driver_verified: boolean | null;
  // Passengers info (joined from bookings)
  passengers: Array<{
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  }>;
}

// Type pour les stats dashboard
export interface TripStats {
  total_trips: number;
  active_trips: number;
  completed_trips: number;
  total_distance: number;
  total_seats_booked: number;
}

// Statuts possibles
export type TripStatus = "PENDING" | "ACTIVE" | "COMPLETED" | "CANCELLED" | "ARCHIVED";

// Type pour la carte (page Map)
export interface TripMapItem {
  trip_id: string;
  departure_name: string | null;
  destination_name: string | null;
  departure_latitude: number | null;
  departure_longitude: number | null;
  destination_latitude: number | null;
  destination_longitude: number | null;
  polyline: string;
  status: string | null;
  departure_schedule: string | null;
  passenger_price: number | null;
  seats_available: number | null;
  seats_published: number | null;
  distance: number | null;
  driver: {
    uid: string;
    display_name: string | null;
    photo_url: string | null;
    rating: number | null;
  } | null;
  passengers: Array<{
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  }>;
}

// Filtres pour la carte
export interface MapFilters {
  status: TripStatus | "ALL";
  dateFrom: string | null;
  dateTo: string | null;
  driverId: string | null;
}

// Type legacy pour compatibilité avec mock data
export interface Trip {
  trip_id: string;
  departure_city: string;
  departure_address: string;
  departure_lat: number;
  departure_lon: number;
  destination_city: string;
  destination_address: string;
  destination_lat: number;
  destination_lon: number;
  trip_distance: number;
  departure_schedule: string;
  price_per_seat: number;
  available_seats: number;
  total_seats: number;
  passengers: string[];
  driver_id: string;
  driver_name: string;
  status: string;
  trip_polyline?: string;
  created_at: string;
  viator_income?: number;
}

// Convertir TripDetail vers Trip (legacy)
export function toTrip(detail: TripDetail): Trip {
  return {
    trip_id: detail.trip_id,
    departure_city: detail.departure_name || "",
    departure_address: detail.departure_description || "",
    departure_lat: detail.departure_latitude || 0,
    departure_lon: detail.departure_longitude || 0,
    destination_city: detail.destination_name || "",
    destination_address: detail.destination_description || "",
    destination_lat: detail.destination_latitude || 0,
    destination_lon: detail.destination_longitude || 0,
    trip_distance: detail.distance || 0,
    departure_schedule: detail.departure_schedule || "",
    price_per_seat: detail.passenger_price || 0,
    available_seats: detail.seats_available || 0,
    total_seats: detail.seats_published || 0,
    passengers: detail.passengers ? detail.passengers.map((p) => p.uid) : [], // Utiliser les vrais IDs passagers
    driver_id: detail.driver_id || "",
    driver_name: detail.driver_name || "",
    status: detail.status || "",
    trip_polyline: detail.polyline || undefined,
    created_at: detail.created_at || "",
    viator_income: detail.driver_price || 0,
  };
}
