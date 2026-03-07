import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getDashboardStats } from "@/lib/queries/stats/get-dashboard-stats";
import { getTripsWithDriver } from "@/lib/queries/trips/get-trips";
import { getSiteTripRequests } from "@/lib/queries/site-requests/get-requests";
import { getTopDrivers, getTopRequestedRoutes } from "@/lib/queries/stats/get-ai-analytics";
import { RefreshButton } from "./refresh-button";
import { IAToolsClient } from "./ia-tools-client";
import { formatDateShort } from "@/lib/utils";
import { User, MapPin, Phone, Zap } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function IAPage() {
  const session = await auth();
  if (!session) {
    redirect("/login");
  }

  const userRole = session.user.role;
  if (userRole !== "admin" && userRole !== "ia") {
    redirect("/"); // Redirige vers l'accueil si pas les droits
  }

  // Fetching data for AI snapshot with full contact details
  const [
    stats, 
    pendingTripsData, 
    activeTripsData, 
    newRequests, 
    reviewedRequests, 
    topDrivers, 
    topRoutes
  ] = await Promise.all([
    getDashboardStats(),
    getTripsWithDriver({ status: 'PENDING', pageSize: 100 }),
    getTripsWithDriver({ status: 'ACTIVE', pageSize: 50 }),
    getSiteTripRequests({ status: 'NEW', limit: 100 }),
    getSiteTripRequests({ status: 'REVIEWED', limit: 100 }),
    getTopDrivers(),
    getTopRequestedRoutes(),
  ]);

  const pendingTrips = pendingTripsData.trips;
  const activeTrips = activeTripsData.trips;

  const now = new Date().toLocaleString('fr-FR');

  // Structured data for JS Bridge
  const rawDataPayload = {
    timestamp: new Date().toISOString(),
    stats,
    trips: {
      pending: pendingTrips,
      active: activeTrips
    },
    requests: {
      new: newRequests,
      reviewed: reviewedRequests
    },
    analytics: {
      topDrivers,
      topRoutes
    }
  };

  return (
    <div className="bg-slate-50 min-h-screen font-mono text-sm p-8 max-w-6xl mx-auto border-x border-slate-200 shadow-sm">
      {/* JSON BRIDGE FOR IA AGENTS / SCRIPTS */}
      <script
        id="ia-raw-data"
        type="application/json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(rawDataPayload) }}
      />

      <header className="flex justify-between items-center mb-10 border-b border-slate-300 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
            <span className="bg-klando-burgundy text-white px-3 py-1 rounded text-lg tracking-normal">IA</span>
            <span>HUB DE DONNÉES BRUTES</span>
          </h1>
          <p className="text-slate-500 mt-1">Snapshot du {now} • Klando Sn Dashboard</p>
        </div>
        <RefreshButton />
      </header>

      <section className="space-y-16">
        {/* STATS GLOBALES */}
        <div>
          <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-klando-burgundy pl-3">Stats Globales</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 border border-slate-200 rounded shadow-sm">
              <p className="text-xs text-slate-500 uppercase">Trajets (Total)</p>
              <p className="text-xl font-bold">{stats.trips.total}</p>
            </div>
            <div className="bg-white p-4 border border-slate-200 rounded shadow-sm">
              <p className="text-xs text-slate-500 uppercase">Utilisateurs</p>
              <p className="text-xl font-bold">{stats.users.total}</p>
            </div>
            <div className="bg-white p-4 border border-slate-200 rounded shadow-sm">
              <p className="text-xs text-slate-500 uppercase">Dist. Totale (km)</p>
              <p className="text-xl font-bold">{Math.round(stats.trips.totalDistance || 0).toLocaleString()}</p>
            </div>
            <div className="bg-white p-4 border border-slate-200 rounded shadow-sm">
              <p className="text-xs text-slate-500 uppercase">Sièges Réservés</p>
              <p className="text-xl font-bold">{stats.trips.totalSeatsBooked}</p>
            </div>
          </div>
        </div>

        {/* OUTILS INTERACTIFS (SEARCH & CONTACT) */}
        <div>
          <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-slate-900 pl-3">Outils Community Manager</h2>
          <IAToolsClient />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* ANALYSE: TOP CONDUCTEURS */}
          <div>
            <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-emerald-500 pl-3">Analyse: Top Conducteurs</h2>
            <div className="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
              <div className="p-2 bg-slate-100 border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase flex">
                <div className="w-1/2">Nom</div>
                <div className="w-1/4 text-center">Trajets</div>
                <div className="w-1/4 text-right">Contact</div>
              </div>
              <div className="divide-y divide-slate-100">
                {topDrivers.map((driver, i) => (
                  <div key={driver.uid} className="p-2 flex items-center hover:bg-slate-50">
                    <div className="w-1/2 flex items-center gap-2 font-medium">
                      <span className="text-[10px] text-slate-400 w-4">{i + 1}.</span>
                      <span className="truncate">{driver.display_name}</span>
                    </div>
                    <div className="w-1/4 font-bold text-center">{driver.trip_count}</div>
                    <div className="w-1/4 text-right">
                      <span className="text-[10px] font-bold text-slate-400 tabular-nums">{driver.phone_number}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ANALYSE: TRAJETS LES PLUS DEMANDÉS */}
          <div>
            <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-blue-500 pl-3">Analyse: Top Demandes Passagers</h2>
            <div className="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
              <div className="p-2 bg-slate-100 border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase flex">
                <div className="w-2/3">Itinéraire</div>
                <div className="w-1/6 text-center">Requêtes</div>
                <div className="w-1/6 text-right">Action</div>
              </div>
              <div id="ia-top-routes-list" className="divide-y divide-slate-100">
                {topRoutes.map((route, i) => (
                  <div 
                    key={i} 
                    className="ia-top-route-item p-2 flex items-center hover:bg-slate-50 transition-colors"
                    data-origin={route.origin_city}
                    data-dest={route.destination_city}
                  >
                    <div className="w-2/3 flex items-center gap-2 font-medium">
                      <MapPin className="w-3 h-3 text-blue-500 opacity-50" />
                      <span className="truncate">{route.origin_city} → {route.destination_city}</span>
                    </div>
                    <div className="w-1/6 text-center font-black text-blue-600">{route.request_count}</div>
                    <div className="w-1/6 text-right">
                      <button 
                        className="ia-action-radar-btn text-[9px] font-black uppercase text-indigo-600 hover:underline flex items-center gap-1 ml-auto"
                        onClick={`(function(){ document.getElementById('ia-search-origin').value='${route.origin_city}'; document.getElementById('ia-search-dest').value='${route.destination_city}'; document.getElementById('ia-search-button').click(); })()`}
                      >
                        <Zap className="w-2.5 h-2.5" /> Radar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* TRAJETS CONDUCTEURS (PENDING/ACTIVE) */}
        <div>
          <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-emerald-500 pl-3">Trajets Actifs & En attente (Drivers)</h2>
          <div className="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
            <div className="p-2 bg-slate-100 border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase flex">
              <div className="w-1/6">Date</div>
              <div className="w-1/4">Origine -&gt; Destination</div>
              <div className="w-1/4">Conducteur</div>
              <div className="w-1/6 text-center">Passagers</div>
              <div className="w-1/12 text-right">Status</div>
            </div>
            <div className="divide-y divide-slate-100">
              {[...activeTrips, ...pendingTrips].map((trip) => (
                <div key={trip.trip_id} className="p-2 flex items-center hover:bg-slate-50">
                  <div className="w-1/6 truncate text-slate-500">{formatDateShort(trip.departure_schedule || "")}</div>
                  <div className="w-1/4 truncate font-medium">
                    {trip.departure_name?.split(',')[0]} → {trip.destination_name?.split(',')[0]}
                  </div>
                  <div className="w-1/4 truncate text-[10px]">
                    <span className="font-bold">{trip.driver_name}</span>
                    <br />
                    <span className="text-slate-400">{trip.driver_phone}</span>
                  </div>
                  <div className="w-1/6 text-center text-[9px] font-bold text-indigo-600">
                    {trip.passengers.length > 0 ? (
                      <span title={trip.passengers.map(p => `${p.display_name} (${p.phone_number})`).join(', ')}>
                        {trip.passengers.length} passagers
                      </span>
                    ) : "-"}
                  </div>
                  <div className="w-1/12 text-right">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${trip.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                      {trip.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* DEMANDES PASSAGERS (NEW/REVIEWED) */}
        <div>
          <h2 className="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest border-l-4 border-amber-500 pl-3">Intentions Voyageurs (Passengers)</h2>
          <div className="bg-white border border-slate-200 rounded shadow-sm overflow-hidden">
             <div className="p-2 bg-slate-100 border-b border-slate-200 text-[10px] font-bold text-slate-500 uppercase flex">
              <div className="w-1/6">Créé le</div>
              <div className="w-1/4">Origine -&gt; Destination</div>
              <div className="w-1/4">Contact / Date</div>
              <div className="w-1/12 text-center">Status</div>
              <div className="w-1/6 text-right">Action Radar</div>
            </div>
            <div id="ia-passenger-intentions-list" className="divide-y divide-slate-100">
              {[...newRequests, ...reviewedRequests].map((req) => (
                <div 
                  key={req.id} 
                  className="ia-passenger-request-item p-2 flex items-center hover:bg-slate-50 transition-colors"
                  data-origin={req.origin_city}
                  data-dest={req.destination_city}
                  data-contact={req.contact_info}
                  data-source={req.source || "SITE"}
                >
                  <div className="w-1/6 truncate text-slate-500">{formatDateShort(req.created_at)}</div>
                  <div className="w-1/4 truncate font-medium">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "text-[8px] font-black px-1 rounded uppercase",
                        req.source === 'FACEBOOK' ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"
                      )}>
                        {req.source || "SITE"}
                      </span>
                      {req.origin_city} → {req.destination_city}
                    </div>
                  </div>
                  <div className="w-1/4 truncate text-slate-600">
                    {req.contact_info} ({req.desired_date || "Dès que possible"})
                  </div>
                  <div className="w-1/12 text-center">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] ${req.status === 'NEW' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                      {req.status}
                    </span>
                  </div>
                  <div className="w-1/6 text-right">
                    <button 
                      className="ia-radar-fill-btn bg-indigo-600 text-white px-2 py-1 rounded text-[9px] font-black uppercase hover:bg-indigo-700 transition-colors flex items-center gap-1 ml-auto"
                      onClick={`(function(){ document.getElementById('ia-search-origin').value='${req.origin_city}'; document.getElementById('ia-search-dest').value='${req.destination_city}'; document.getElementById('ia-contact-target').value='${req.contact_info}'; document.getElementById('ia-search-button').click(); })()`}
                    >
                      <Zap className="w-2.5 h-2.5" /> Lancer Radar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI SNIPPET - CONTEXTE CONCIS */}
        <div className="bg-klando-dark text-white p-6 rounded-lg shadow-xl border border-slate-800">
          <h2 className="text-xs font-black uppercase text-klando-burgundy mb-4 tracking-widest border-l-4 border-klando-burgundy pl-3">Contexte pour l'IA</h2>
          <pre className="text-[11px] leading-relaxed overflow-auto whitespace-pre-wrap font-mono opacity-90">
{`--- RÉSUMÉ SYSTÈME ---
- Dashboard actif: ${now}
- Statut Klando: En production (Sénégal)
- Volume: ${stats.trips.total} trajets, ${stats.users.total} utilisateurs
- Demande: ${newRequests.length} nouvelles intentions non traitées
- Offre: ${activeTrips.length + pendingTrips.length} trajets conducteurs à venir

--- DIRECTIVE DE MATCHING ---
Priorité: Connecter les "${newRequests.length} intentions voyageurs" aux "${pendingTrips.length} trajets conducteurs".
Focus sur les axes majeurs: Dakar, Thiès, Mbour, Touba, Saint-Louis.
`}
          </pre>
        </div>
      </section>

      <footer className="mt-20 pt-8 border-t border-slate-200 text-center text-slate-400 text-[10px] uppercase tracking-widest">
        Accès restreint • Usage IA & Administration • Klando SN 2026
      </footer>
    </div>
  );
}
