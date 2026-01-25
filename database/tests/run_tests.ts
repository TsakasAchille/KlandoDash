/**
 * Script de test des requêtes trips
 * Usage: npx ts-node run_tests.ts
 */

import { createClient } from "@supabase/supabase-js";

// Config - remplace avec tes clés
const SUPABASE_URL = process.env.SUPABASE_URL || "https://zzxeimcchndnrildeefl.supabase.co";
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || "";

if (!SUPABASE_KEY) {
  console.error("❌ SUPABASE_SERVICE_ROLE_KEY ou SUPABASE_ANON_KEY requis");
  console.log("Usage: SUPABASE_SERVICE_ROLE_KEY=xxx npx ts-node run_tests.ts");
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function runTests() {
  console.log("🚀 Démarrage des tests trips...\n");

  // TEST 1: Comptage total
  console.log("═══════════════════════════════════════");
  console.log("TEST 1: Comptage total des trips");
  console.log("═══════════════════════════════════════");
  const { count: totalCount } = await supabase
    .from("trips")
    .select("*", { count: "exact", head: true });
  console.log(`Total trips: ${totalCount}\n`);

  // TEST 2: Répartition par statut
  console.log("═══════════════════════════════════════");
  console.log("TEST 2: Répartition par statut");
  console.log("═══════════════════════════════════════");
  const { data: statusData } = await supabase
    .from("trips")
    .select("status");

  const statusCounts: Record<string, number> = {};
  statusData?.forEach((t) => {
    const s = t.status || "NULL";
    statusCounts[s] = (statusCounts[s] || 0) + 1;
  });
  console.table(statusCounts);
  console.log("");

  // TEST 3: Liste trips (colonnes frontend)
  console.log("═══════════════════════════════════════");
  console.log("TEST 3: Sample data (colonnes frontend)");
  console.log("═══════════════════════════════════════");
  const { data: sampleTrips, error: sampleError } = await supabase
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
      status,
      driver_id
    `)
    .order("departure_schedule", { ascending: false })
    .limit(5);

  if (sampleError) {
    console.error("❌ Erreur:", sampleError.message);
  } else {
    console.table(sampleTrips?.map(t => ({
      id: t.trip_id?.substring(0, 8) + "...",
      depart: t.departure_name?.substring(0, 20),
      dest: t.destination_name?.substring(0, 20),
      date: t.departure_schedule?.substring(0, 10),
      km: t.distance,
      places: `${t.seats_available}/${t.seats_published}`,
      prix: t.passenger_price,
      status: t.status
    })));
  }
  console.log("");

  // TEST 4: Détail trip avec jointure driver
  console.log("═══════════════════════════════════════");
  console.log("TEST 4: Trip avec infos conducteur");
  console.log("═══════════════════════════════════════");
  const { data: tripWithDriver, error: driverError } = await supabase
    .from("trips")
    .select(`
      trip_id,
      departure_name,
      destination_name,
      driver_id,
      driver:users!fk_driver (
        uid,
        display_name,
        phone_number,
        rating
      )
    `)
    .not("driver_id", "is", null)
    .limit(3);

  if (driverError) {
    console.error("❌ Erreur jointure:", driverError.message);
  } else {
    tripWithDriver?.forEach((t) => {
      const driver = t.driver as any;
      console.log(`Trip: ${t.departure_name} → ${t.destination_name}`);
      console.log(`  Driver: ${driver?.display_name || "N/A"} (${driver?.rating || "N/A"}⭐)`);
    });
  }
  console.log("");

  // TEST 5: Stats globales
  console.log("═══════════════════════════════════════");
  console.log("TEST 5: Statistiques globales");
  console.log("═══════════════════════════════════════");
  const { data: allTrips } = await supabase
    .from("trips")
    .select("status, distance, seats_booked, passenger_price");

  const stats = {
    total: allTrips?.length || 0,
    active: allTrips?.filter((t) => t.status === "ACTIVE").length || 0,
    completed: allTrips?.filter((t) => t.status === "COMPLETED").length || 0,
    pending: allTrips?.filter((t) => t.status === "PENDING").length || 0,
    total_distance: allTrips?.reduce((sum, t) => sum + (t.distance || 0), 0).toFixed(1) + " km",
    total_seats_booked: allTrips?.reduce((sum, t) => sum + (t.seats_booked || 0), 0),
    avg_price: Math.round(allTrips?.reduce((sum, t) => sum + (t.passenger_price || 0), 0) / (allTrips?.length || 1)) + " XOF"
  };
  console.table([stats]);
  console.log("");

  // TEST 6: Données manquantes
  console.log("═══════════════════════════════════════");
  console.log("TEST 6: Données manquantes");
  console.log("═══════════════════════════════════════");
  const { data: nullCheck } = await supabase
    .from("trips")
    .select("departure_name, destination_name, departure_schedule, distance, passenger_price, driver_id, status");

  const missing = {
    departure_name: nullCheck?.filter((t) => !t.departure_name).length || 0,
    destination_name: nullCheck?.filter((t) => !t.destination_name).length || 0,
    departure_schedule: nullCheck?.filter((t) => !t.departure_schedule).length || 0,
    distance: nullCheck?.filter((t) => !t.distance).length || 0,
    passenger_price: nullCheck?.filter((t) => !t.passenger_price).length || 0,
    driver_id: nullCheck?.filter((t) => !t.driver_id).length || 0,
    status: nullCheck?.filter((t) => !t.status).length || 0,
  };
  console.table([missing]);
  console.log("");

  // TEST 7: Top routes
  console.log("═══════════════════════════════════════");
  console.log("TEST 7: Top 5 routes");
  console.log("═══════════════════════════════════════");
  const routeCounts: Record<string, number> = {};
  allTrips?.forEach((t: any) => {
    if (t.departure_name && t.destination_name) {
      // Récupérer depuis nullCheck qui a ces colonnes
    }
  });

  const { data: routeData } = await supabase
    .from("trips")
    .select("departure_name, destination_name");

  routeData?.forEach((t: any) => {
    if (t.departure_name && t.destination_name) {
      const route = `${String(t.departure_name).substring(0, 15)} → ${String(t.destination_name).substring(0, 15)}`;
      routeCounts[route] = (routeCounts[route] || 0) + 1;
    }
  });

  const topRoutes = Object.entries(routeCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  console.table(topRoutes.map(([route, count]) => ({ route, count })));
  console.log("");

  // TEST 8: Bookings
  console.log("═══════════════════════════════════════");
  console.log("TEST 8: Bookings");
  console.log("═══════════════════════════════════════");
  const { count: bookingCount } = await supabase
    .from("bookings")
    .select("*", { count: "exact", head: true });
  console.log(`Total bookings: ${bookingCount}\n`);

  const { data: bookingSample } = await supabase
    .from("bookings")
    .select(`
      id,
      seats,
      status,
      user_id,
      trip_id
    `)
    .limit(5);

  if (bookingSample && bookingSample.length > 0) {
    console.table(bookingSample);
  } else {
    console.log("Aucune réservation trouvée");
  }

  console.log("\n✅ Tests terminés!");
}

runTests().catch(console.error);
