import { createServerClient } from "../../supabase";
import { UserDetail } from "@/types/user";

/**
 * Détail d'un utilisateur avec stats
 */
export async function getUserById(uid: string): Promise<UserDetail | null> {
  const supabase = createServerClient();

  // Fetch user details
  const { data: user, error: userError } = await supabase
    .from("users")
    .select(`
      uid,
      display_name,
      email,
      first_name,
      name,
      phone_number,
      birth,
      photo_url,
      bio,
      gender,
      rating,
      rating_count,
      role,
      driver_license_url,
      id_card_url,
      is_driver_doc_validated,
      created_at,
      updated_at
    `)
    .eq("uid", uid)
    .single();

  if (userError) {
    console.error("getUserById error:", userError);
    return null;
  }

  // Count trips as driver
  const { count: driverCount } = await supabase
    .from("trips")
    .select("*", { count: "exact", head: true })
    .eq("driver_id", uid);

  // Count trips as passenger (via bookings)
  const { count: passengerCount } = await supabase
    .from("bookings")
    .select("*", { count: "exact", head: true })
    .eq("user_id", uid);

  return {
    ...user,
    trips_as_driver: driverCount || 0,
    trips_as_passenger: passengerCount || 0,
  } as UserDetail;
}
