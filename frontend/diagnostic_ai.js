const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

async function diagnostic() {
  try {
    const env = fs.readFileSync('.env.local', 'utf8');
    const getVar = (name) => {
        const line = env.split('\n').find(l => l.startsWith(name));
        return line ? line.split('=')[1].trim() : null;
    };

    const supabase = createClient(
      getVar('NEXT_PUBLIC_SUPABASE_URL'),
      getVar('SUPABASE_SERVICE_ROLE_KEY')
    );

    console.log("--- Diagnostic Action IA ---");
    
    const { count: newRequests } = await supabase.from('site_trip_requests').select('*', { count: 'exact', head: true }).eq('status', 'NEW');
    console.log("Demandes 'NEW' :", newRequests);

    const { count: pendingTrips } = await supabase.from('trips').select('*', { count: 'exact', head: true }).eq('status', 'PENDING');
    console.log("Trajets 'PENDING' :", pendingTrips);

    const { count: validatedDrivers } = await supabase.from('users').select('*', { count: 'exact', head: true }).eq('is_driver_doc_validated', true);
    console.log("Chauffeurs validés :", validatedDrivers);

    const { data: recos } = await supabase.from('dash_ai_recommendations').select('*');
    console.log("Recommandations existantes en base :", recos?.length || 0);

  } catch (e) {
    console.error(e);
  }
}

diagnostic();
