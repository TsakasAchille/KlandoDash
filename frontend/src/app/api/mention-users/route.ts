import { auth } from "@/lib/auth";
import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";
import { unstable_noStore as noStore } from "next/cache";


// Initialize Supabase Admin Client
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

/**
 * @route GET /api/mention-users
 * @description Fetches a list of users who can be mentioned (admins and support roles).
 * Returns a list of users with `id` (email) and `display` (name or email prefix).
 */
export async function GET(request: Request) {
  noStore(); // Ensure fresh data on every request
  
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ message: "Non autorisé" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const query = searchParams.get("q");

  const supabaseQuery = supabaseAdmin
    .from("dash_authorized_users")
    .select("email, display_name")
    .in("role", ["admin", "support"]);

  if (query) {
    // Search in display_name or email for a partial match
    supabaseQuery.or(`display_name.ilike.%${query}%,email.ilike.%${query}%`);
  }

  const { data, error } = await supabaseQuery;

  if (error) {
    console.error("Error fetching mention users:", error);
    return NextResponse.json(
      { message: "Erreur lors de la récupération des utilisateurs" },
      { status: 500 }
    );
  }

  // Format the data for the frontend autocomplete component
  const users = data.map((user) => ({
    // The `id` is what will be inserted in the textarea (e.g., @JohnDoe)
    id: user.display_name?.replace(/\s+/g, '') || user.email.split('@')[0],
    // The `display` is what the user sees in the autocomplete list
    display: `${user.display_name || user.email.split('@')[0]} (${user.email})`,
    email: user.email,
  }));

  return NextResponse.json(users);
}

