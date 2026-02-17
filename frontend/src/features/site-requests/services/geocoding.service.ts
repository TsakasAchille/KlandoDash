import * as polyline from "@mapbox/polyline";

export interface GeoPoint {
  lat: number;
  lng: number;
}

export interface RouteData {
  polyline: string; // Encoded polyline
  coordinates: GeoPoint[]; // Decoded coordinates
  distance?: number;
  duration?: number;
}

const NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search";
const OSRM_BASE = "https://router.project-osrm.org/route/v1/driving";

export const GeocodingService = {
  /**
   * Trouve les coordonnées GPS d'une ville/adresse
   */
  async getCoordinates(query: string): Promise<GeoPoint | null> {
    try {
      const url = `${NOMINATIM_BASE}?format=json&q=${encodeURIComponent(query + ", Senegal")}&limit=1`;
      const res = await fetch(url, {
        headers: { 'User-Agent': 'KlandoDash-Admin' }
      });
      const data = await res.json();
      
      if (data && data[0]) {
        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon)
        };
      }
      return null;
    } catch (error) {
      console.error("[GeocodingService] Error fetching coords for:", query, error);
      return null;
    }
  },

  /**
   * Calcule un itinéraire routier entre deux points
   */
  async getRoute(start: GeoPoint, end: GeoPoint): Promise<RouteData | null> {
    try {
      const url = `${OSRM_BASE}/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.routes && data.routes[0]) {
        return {
          polyline: data.routes[0].geometry,
          coordinates: polyline.decode(data.routes[0].geometry).map(([lat, lng]) => ({ lat, lng })),
          distance: data.routes[0].distance,
          duration: data.routes[0].duration
        };
      }
      return null;
    } catch (error) {
      console.error("[GeocodingService] Error fetching route:", error);
      return null;
    }
  },

  /**
   * Décode une polyline existante
   */
  decodePolyline(encoded: string): GeoPoint[] {
    try {
      return polyline.decode(encoded).map(([lat, lng]) => ({ lat, lng }));
    } catch (error) {
      console.error("[GeocodingService] Decode error:", error);
      return [];
    }
  }
};
