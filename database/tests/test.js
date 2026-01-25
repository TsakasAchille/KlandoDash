const { createClient } = require("@supabase/supabase-js");

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function runTests() {
  console.log("🚀 Tests trips Supabase\n");

  // TEST 1: Total
  console.log("═══════════════════════════════════════");
  console.log("TEST 1: Comptage total");
  console.log("═══════════════════════════════════════");
  const { count } = await supabase.from("trips").select("*", { count: "exact", head: true });
  console.log(`Total trips: ${count}\n`);

  // TEST 2: Par statut
  console.log("═══════════════════════════════════════");
  console.log("TEST 2: Par statut");
  console.log("═══════════════════════════════════════");
  const { data: statusData } = await supabase.from("trips").select("status");
  const statusCounts = {};
  statusData?.forEach((t) => {
    const s = t.status || "NULL";
    statusCounts[s] = (statusCounts[s] || 0) + 1;
  });
  console.table(statusCounts);

  // TEST 3: Sample
  console.log("\n═══════════════════════════════════════");
  console.log("TEST 3: Sample (5 derniers trips)");
  console.log("═══════════════════════════════════════");
  const { data: sample, error } = await supabase
    .from("trips")
    .select("trip_id, departure_name, destination_name, departure_schedule, distance, seats_available, seats_published, passenger_price, status")
    .order("departure_schedule", { ascending: false })
    .limit(5);

  if (error) {
    console.error("❌ Erreur:", error.message);
  } else {
    console.table(sample?.map((t) => ({
      id: t.trip_id?.substring(0, 12) + "...",
      depart: (t.departure_name || "").substring(0, 20),
      dest: (t.destination_name || "").substring(0, 20),
      date: t.departure_schedule?.substring(0, 10),
      km: t.distance?.toFixed(1),
      places: `${t.seats_available}/${t.seats_published}`,
      prix: t.passenger_price,
      status: t.status,
    })));
  }

  // TEST 4: Jointure driver
  console.log("\n═══════════════════════════════════════");
  console.log("TEST 4: Trips avec conducteur");
  console.log("═══════════════════════════════════════");
  const { data: withDriver, error: driverErr } = await supabase
    .from("trips")
    .select(`trip_id, departure_name, destination_name, driver:users!fk_driver(uid, display_name, rating)`)
    .not("driver_id", "is", null)
    .limit(5);

  if (driverErr) {
    console.error("❌ Erreur jointure:", driverErr.message);
  } else {
    withDriver?.forEach((t) => {
      console.log(`${(t.departure_name || "?").substring(0, 15)} → ${(t.destination_name || "?").substring(0, 15)}`);
      console.log(`  Conducteur: ${t.driver?.display_name || "N/A"} (${t.driver?.rating || "?"}⭐)\n`);
    });
  }

  // TEST 5: Stats
  console.log("═══════════════════════════════════════");
  console.log("TEST 5: Statistiques");
  console.log("═══════════════════════════════════════");
  const { data: all } = await supabase.from("trips").select("status, distance, seats_booked, passenger_price");
  console.table({
    total: all?.length || 0,
    active: all?.filter((t) => t.status === "ACTIVE").length || 0,
    completed: all?.filter((t) => t.status === "COMPLETED").length || 0,
    pending: all?.filter((t) => t.status === "PENDING").length || 0,
    distance_totale: (all?.reduce((s, t) => s + (t.distance || 0), 0) || 0).toFixed(0) + " km",
    places_reservees: all?.reduce((s, t) => s + (t.seats_booked || 0), 0) || 0,
    prix_moyen: Math.round((all?.reduce((s, t) => s + (t.passenger_price || 0), 0) || 0) / (all?.length || 1)) + " XOF",
  });

  // TEST 6: Données manquantes
  console.log("\n═══════════════════════════════════════");
  console.log("TEST 6: Données manquantes");
  console.log("═══════════════════════════════════════");
  const { data: nulls } = await supabase.from("trips").select("departure_name, destination_name, departure_schedule, distance, passenger_price, driver_id, status");
  console.table({
    sans_depart: nulls?.filter((t) => !t.departure_name).length || 0,
    sans_destination: nulls?.filter((t) => !t.destination_name).length || 0,
    sans_date: nulls?.filter((t) => !t.departure_schedule).length || 0,
    sans_distance: nulls?.filter((t) => !t.distance).length || 0,
    sans_prix: nulls?.filter((t) => !t.passenger_price).length || 0,
    sans_driver: nulls?.filter((t) => !t.driver_id).length || 0,
    sans_status: nulls?.filter((t) => !t.status).length || 0,
  });

  // TEST 7: Top routes
  console.log("\n═══════════════════════════════════════");
  console.log("TEST 7: Top 5 routes");
  console.log("═══════════════════════════════════════");
  const routes = {};
  nulls?.forEach((t) => {
    if (t.departure_name && t.destination_name) {
      const r = `${t.departure_name.substring(0, 12)} → ${t.destination_name.substring(0, 12)}`;
      routes[r] = (routes[r] || 0) + 1;
    }
  });
  const top = Object.entries(routes).sort((a, b) => b[1] - a[1]).slice(0, 5);
  console.table(top.map(([route, n]) => ({ route, trips: n })));

  // TEST 8: Bookings
  console.log("\n═══════════════════════════════════════");
  console.log("TEST 8: Bookings");
  console.log("═══════════════════════════════════════");
  const { count: bookingCount } = await supabase.from("bookings").select("*", { count: "exact", head: true });
  console.log(`Total bookings: ${bookingCount}`);

  console.log("\n✅ Tests terminés!");
}

runTests().catch(console.error);
