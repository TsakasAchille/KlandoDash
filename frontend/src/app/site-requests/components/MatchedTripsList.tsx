"use client";

import { TripMapItem } from "@/types/trip";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, Calendar, MapPin, ExternalLink, Eye, EyeOff, Sparkles } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useState, useMemo } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface MatchedTripsListProps {
  trips: (TripMapItem & { origin_distance?: number; destination_distance?: number })[];
  hiddenIds: Set<string>;
  onToggleVisibility: (id: string) => void;
  onShowAll: () => void;
  onHideAll: () => void;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onOpenIA: () => void;
}

export function MatchedTripsList({ 
  trips, 
  hiddenIds, 
  onToggleVisibility, 
  onShowAll, 
  onHideAll, 
  selectedId, 
  onSelect,
  onOpenIA 
}: MatchedTripsListProps) {
  const [radiusTab, setRadiusTab] = useState<string>("10");

  const filteredByRadius = useMemo(() => {
    const radius = parseInt(radiusTab);
    return trips.filter(t => {
      const dist = Math.max(t.origin_distance || 0, t.destination_distance || 0);
      return dist <= radius;
    });
  }, [trips, radiusTab]);

  const counts = useMemo(() => ({
    r5: trips.filter(t => Math.max(t.origin_distance || 0, t.destination_distance || 0) <= 5).length,
    r10: trips.filter(t => Math.max(t.origin_distance || 0, t.destination_distance || 0) <= 10).length,
    r15: trips.filter(t => Math.max(t.origin_distance || 0, t.destination_distance || 0) <= 15).length,
    all: trips.length
  }), [trips]);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="px-2 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-green-500/10 rounded-lg text-green-600">
              <Sparkles className="w-4 h-4" />
            </div>
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Matching par rayon</h4>
          </div>
          
          <div className="flex gap-2">
            {filteredByRadius.length > 0 && (
              <button 
                onClick={onOpenIA}
                className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-green-500 text-white text-[9px] font-black uppercase shadow-sm hover:bg-green-600 transition-all mr-1 animate-in zoom-in"
              >
                <Sparkles className="w-3 h-3" /> IA
              </button>
            )}
            <button 
              onClick={onShowAll}
              className="text-[9px] font-black uppercase text-klando-gold hover:underline flex items-center gap-1"
            >
              <Eye className="w-2.5 h-2.5" /> Tout
            </button>
            <button 
              onClick={onHideAll}
              className="text-[9px] font-black uppercase text-muted-foreground hover:text-foreground flex items-center gap-1"
            >
              <EyeOff className="w-2.5 h-2.5" /> Aucun
            </button>
          </div>
        </div>

        <Tabs value={radiusTab} onValueChange={setRadiusTab} className="w-full">
          <TabsList className="grid grid-cols-3 bg-muted/50 p-1 h-12 rounded-2xl">
            <TabsTrigger value="5" className="rounded-xl text-[9px] font-black flex flex-col gap-0.5">
              5km
              <span className="text-[8px] opacity-50">{counts.r5}</span>
            </TabsTrigger>
            <TabsTrigger value="10" className="rounded-xl text-[9px] font-black flex flex-col gap-0.5">
              10km
              <span className="text-[8px] opacity-50">{counts.r10}</span>
            </TabsTrigger>
            <TabsTrigger value="15" className="rounded-xl text-[9px] font-black flex flex-col gap-0.5">
              15km
              <span className="text-[8px] opacity-50">{counts.r15}</span>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
        {filteredByRadius.length === 0 ? (
          <div className="h-40 flex flex-col items-center justify-center text-center p-6 border-2 border-dashed border-border rounded-3xl opacity-40">
            <MapPin className="w-8 h-8 mb-2" />
            <p className="text-[10px] font-bold uppercase leading-tight">Aucun trajet à<br/>moins de {radiusTab}km</p>
          </div>
        ) : (
          filteredByRadius.map((trip) => {
            const isHidden = hiddenIds.has(trip.trip_id);
            const isSelected = selectedId === trip.trip_id;
            
            // Récupérer les distances depuis l'objet matches du client (injecté via SiteRequestsMap)
            const originDist = typeof trip.origin_distance === 'number' ? trip.origin_distance.toFixed(1) : "?";
            const destDist = typeof trip.destination_distance === 'number' ? trip.destination_distance.toFixed(1) : "?";

            return (
              <Card 
                key={trip.trip_id} 
                onClick={() => onSelect(trip.trip_id)}
                className={cn(
                  "rounded-2xl border-border/40 hover:border-green-500/30 transition-all group overflow-hidden bg-card/50 cursor-pointer",
                  isHidden && "opacity-40 grayscale-[0.5]",
                  isSelected && "border-green-500 bg-green-500/[0.03] shadow-lg scale-[1.02]"
                )}
              >
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center overflow-hidden border border-border/50">
                        {trip.driver?.photo_url ? (
                          <img src={trip.driver.photo_url} alt="" className="w-full h-full object-cover" />
                        ) : (
                          <User className="w-4 h-4 text-muted-foreground" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <p className="text-[10px] font-black uppercase truncate text-klando-dark">{trip.driver?.display_name || "Inconnu"}</p>
                        <div className="flex items-center gap-1">
                          <span className="text-[9px] font-bold text-yellow-600">★ {trip.driver?.rating?.toFixed(1) || "5.0"}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <button 
                        onClick={() => onToggleVisibility(trip.trip_id)}
                        className={cn(
                          "p-1.5 rounded-lg border transition-all",
                          isHidden ? "bg-secondary text-muted-foreground border-border/40" : "bg-green-500/10 text-green-600 border-green-200 hover:bg-green-500/20"
                        )}
                      >
                        {isHidden ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                      </button>
                      <Badge className="bg-blue-500/10 text-blue-600 border-none text-[8px] font-black">{trip.status}</Badge>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-tighter">
                      <span className="truncate">{trip.departure_name?.split(',')[0]}</span>
                      <span className="text-muted-foreground">➜</span>
                      <span className="truncate">{trip.destination_name?.split(',')[0]}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[9px] text-muted-foreground font-bold italic">
                      <Calendar className="w-3 h-3" />
                      {trip.departure_schedule ? format(new Date(trip.departure_schedule), "EEE d MMM 'à' HH:mm", { locale: fr }) : "N/A"}
                    </div>
                  </div>

                  {/* DISTANCES DIAGNOSTIC */}
                  <div className="grid grid-cols-2 gap-2 py-2 border-y border-border/20">
                    <div className="flex flex-col">
                      <span className="text-[8px] font-black text-muted-foreground uppercase">Proximité Départ</span>
                      <span className="text-[10px] font-bold text-green-600">{originDist} km</span>
                    </div>
                    <div className="flex flex-col text-right">
                      <span className="text-[8px] font-black text-muted-foreground uppercase">Proximité Arrivée</span>
                      <span className="text-[10px] font-bold text-red-600">{destDist} km</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] font-black text-klando-gold">{trip.passenger_price} XOF</span>
                    <Link href={`/trips?selected=${trip.trip_id}`} className="p-1.5 rounded-lg bg-secondary hover:bg-klando-gold hover:text-white transition-colors">
                      <ExternalLink className="w-3 h-3" />
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
