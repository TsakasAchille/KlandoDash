"use client";

import { MapPin, Zap } from "lucide-react";
import { formatDateShort, cn } from "@/lib/utils";
import { SiteTripRequest } from "@/types/site-request";

interface IAListsClientProps {
  topRoutes: any[];
  newRequests: SiteTripRequest[];
  reviewedRequests: SiteTripRequest[];
}

export function IAListsClient({ topRoutes, newRequests, reviewedRequests }: IAListsClientProps) {
  
  const handleRadarClick = (origin: string, dest: string, contact?: string) => {
    const originInput = document.getElementById('ia-search-origin') as HTMLInputElement;
    const destInput = document.getElementById('ia-search-dest') as HTMLInputElement;
    const targetInput = document.getElementById('ia-contact-target') as HTMLInputElement;
    const searchBtn = document.getElementById('ia-search-button') as HTMLButtonElement;
    
    if (originInput) originInput.value = origin;
    if (destInput) destInput.value = dest;
    if (contact && targetInput) targetInput.value = contact;
    
    // Trigger events for React state sync
    originInput?.dispatchEvent(new Event('input', { bubbles: true }));
    destInput?.dispatchEvent(new Event('input', { bubbles: true }));
    if (contact) targetInput?.dispatchEvent(new Event('input', { bubbles: true }));
    
    if (searchBtn) searchBtn.click();
    
    // Scroll up to see the search results
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* ANALYSE: TOP CONDUCTEURS (Reste statique ou géré ici si besoin) */}
        {/* Note: Je laisse le parent gérer les Top Drivers car ils n'ont pas d'action interactive complexe */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mt-12">
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
                      onClick={() => handleRadarClick(route.origin_city, route.destination_city)}
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

      {/* DEMANDES PASSAGERS (NEW/REVIEWED) */}
      <div className="mt-16">
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
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        "text-[8px] font-black px-1 rounded uppercase",
                        req.source === 'FACEBOOK' ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"
                      )}>
                        {req.source || "SITE"}
                      </span>
                      <span className={cn(
                        "text-[8px] font-black px-1 rounded uppercase",
                        req.request_type === 'DRIVER' ? "bg-orange-100 text-orange-700" : "bg-purple-100 text-purple-700"
                      )}>
                        {req.request_type === 'DRIVER' ? "Conducteur" : "Passager"}
                      </span>
                    </div>
                    <div className="truncate">
                      {req.origin_city} → {req.destination_city}
                    </div>
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
                    onClick={() => handleRadarClick(req.origin_city, req.destination_city, req.contact_info)}
                  >
                    <Zap className="w-2.5 h-2.5" /> Lancer Radar
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
