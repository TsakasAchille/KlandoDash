const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

async function checkIds() {
  try {
    // Lecture manuelle du .env.local
    const env = fs.readFileSync('.env.local', 'utf8');
    const getVar = (name) => env.split('\n').find(l => l.startsWith(name)).split('=')[1].trim();

    const supabase = createClient(
      getVar('NEXT_PUBLIC_SUPABASE_URL'),
      getVar('SUPABASE_SERVICE_ROLE_KEY')
    );

    console.log("--- IDs dans la table 'trips' ---");
    const { data: trips } = await supabase.from('trips').select('trip_id').limit(5);
    console.log(JSON.stringify(trips, null, 2));

    console.log("\n--- IDs dans la vue 'public_pending_trips' ---");
    const { data: publicTrips } = await supabase.from('public_pending_trips').select('id').limit(5);
    console.log(JSON.stringify(publicTrips, null, 2));
  } catch (e) {
    console.error(e);
  }
}

checkIds();
