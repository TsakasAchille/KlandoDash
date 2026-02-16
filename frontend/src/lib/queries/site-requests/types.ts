export interface PublicTrip {
  id: string;
  departure_city: string;
  arrival_city: string;
  departure_time: string;
  seats_available?: number;
  polyline?: string | null;
  destination_latitude?: number | null;
  destination_longitude?: number | null;
}
