const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

async function checkOrphans() {
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

    console.log("--- Statut actuel ---");
    const { count } = await supabase.from('site_trip_requests').select('*', { count: 'exact', head: true });
    console.log("Demandes restantes :", count);

    const { data: matches } = await supabase.from('site_trip_request_matches').select('request_id');
    const { data: requests } = await supabase.from('site_trip_requests').select('id');
    
    const requestIds = new Set(requests.map(r => r.id));
    const orphans = (matches || []).filter(m => !requestIds.has(m.request_id));
    
    console.log("Matches orphelins trouvés (traces de demandes disparues) :", orphans.length);
    if (orphans.length > 0) {
        console.log("IDs des demandes disparues :");
        console.log([...new Set(orphans.map(o => o.request_id))]);
    }
  } catch (e) {
    console.error(e);
  }
}

checkOrphans();
