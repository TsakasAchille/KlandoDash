import { createServerClient } from "../../supabase";

export interface TopDriver {
  uid: string;
  display_name: string;
  photo_url: string;
  phone_number: string;
  trip_count: number;
  rating: number;
}

export interface TopRoute {
  origin_city: string;
  destination_city: string;
  request_count: number;
}

/**
 * Récupère les 10 meilleurs conducteurs (par nombre de trajets)
 */
export async function getTopDrivers(): Promise<TopDriver[]> {
  const supabase = createServerClient();

  // On compte les trajets par driver_id dans la table trips
  const { data, error } = await supabase
    .from("trips")
    .select("driver_id, driver:users!fk_driver(display_name, photo_url, phone_number, rating)")
    .not("driver_id", "is", null);

  if (error) {
    console.error("getTopDrivers error:", error);
    return [];
  }

  // Agrégation manuelle (Supabase JS ne supporte pas bien le GROUP BY complexe sans RPC)
  const counts: Record<string, { count: number; user: any }> = {};
  data.forEach((item: any) => {
    if (!item.driver_id) return;
    if (!counts[item.driver_id]) {
      counts[item.driver_id] = { count: 0, user: item.driver };
    }
    counts[item.driver_id].count++;
  });

  return Object.entries(counts)
    .map(([uid, info]) => ({
      uid,
      display_name: info.user?.display_name || "Inconnu",
      photo_url: info.user?.photo_url || "",
      phone_number: info.user?.phone_number || "",
      trip_count: info.count,
      rating: info.user?.rating || 0,
    }))
    .sort((a, b) => b.trip_count - a.trip_count)
    .slice(0, 10);
}

/**
 * Récupère les 10 trajets les plus demandés (par les passagers)
 */
export async function getTopRequestedRoutes(): Promise<TopRoute[]> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("site_trip_requests")
    .select("origin_city, destination_city");

  if (error) {
    console.error("getTopRequestedRoutes error:", error);
    return [];
  }

  const routes: Record<string, number> = {};
  data.forEach((item: any) => {
    const key = `${item.origin_city.trim()} -> ${item.destination_city.trim()}`;
    routes[key] = (routes[key] || 0) + 1;
  });

  return Object.entries(routes)
    .map(([route, count]) => {
      const [origin, destination] = route.split(" -> ");
      return {
        origin_city: origin,
        destination_city: destination,
        request_count: count,
      };
    })
    .sort((a, b) => b.request_count - a.request_count)
    .slice(0, 10);
}
