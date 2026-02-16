"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { TripDetail } from "@/types/trip";
import { formatDate, formatDistance, formatPrice, cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Banknote, Car, Leaf, ExternalLink, Map, ShieldCheck, Star } from "lucide-react";
import Image from "next/image";

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const TripRouteMap = dynamic(
  () => import("./trip-route-map").then((mod) => mod.TripRouteMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[200px] rounded-lg bg-secondary/50 flex items-center justify-center">
        <span className="text-muted-foreground text-xs font-black uppercase tracking-widest animate-pulse">Chargement de la carte...</span>
      </div>
    ),
  }
);

interface TripDetailsProps {
  trip: TripDetail;
}

export function TripDetails({ trip }: TripDetailsProps) {
  const co2Saved = ((trip.distance || 0) * 0.12 * trip.passengers.length).toFixed(1);

  return (
    <div className="space-y-4 sticky top-6">
      {/* Route & Header */}
      <Card className="border-klando-gold/20 overflow-hidden">
        <div className="bg-gradient-to-r from-klando-burgundy/10 to-transparent p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-klando-gold/10">
                <Car className="w-4 h-4 text-klando-gold" />
              </div>
              <h2 className="text-sm font-black uppercase tracking-tight">Trajet #{trip.trip_id.substring(0, 8)}</h2>
            </div>
            <span className={cn(
              "px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest border",
              trip.status === "ACTIVE" ? "bg-blue-500/10 text-blue-500 border-blue-500/20" :
              trip.status === "COMPLETED" ? "bg-green-500/10 text-green-500 border-green-500/20" :
              "bg-secondary text-muted-foreground border-border/50"
            )}>
              {trip.status}
            </span>
          </div>

          <div className="grid grid-cols-[1fr,auto,1fr] items-center gap-3">
            <div className="min-w-0">
              <p className="text-[10px] text-muted-foreground uppercase font-black tracking-widest mb-1">Départ</p>
              <p className="font-bold text-xs truncate leading-tight">{trip.departure_name}</p>
              <p className="text-[9px] text-muted-foreground truncate italic">{trip.departure_description}</p>
            </div>
            <div className="text-klando-gold font-black">→</div>
            <div className="min-w-0">
              <p className="text-[10px] text-muted-foreground uppercase font-black tracking-widest mb-1 text-right">Arrivée</p>
              <p className="font-bold text-xs truncate leading-tight text-right">{trip.destination_name}</p>
              <p className="text-[9px] text-muted-foreground truncate italic text-right">{trip.destination_description}</p>
            </div>
          </div>
        </div>

        <CardContent className="p-4 pt-2">
          {trip.polyline ? (
            <div className="rounded-lg overflow-hidden border border-border/20 mb-4">
              <TripRouteMap
                polylineString={trip.polyline}
                departureName={trip.departure_name || ""}
                destinationName={trip.destination_name || ""}
              />
            </div>
          ) : (
            <div className="w-full h-32 rounded-lg bg-secondary/30 flex items-center justify-center mb-4 border border-dashed border-border/40">
              <div className="text-center">
                <Map className="w-6 h-6 mx-auto mb-1 text-muted-foreground/40" />
                <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest">Tracé non disponible</p>
              </div>
            </div>
          )}

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-2">
            <div className="p-2 rounded-lg bg-secondary/30 border border-border/20 text-center">
              <p className="text-[8px] text-muted-foreground uppercase font-black tracking-widest mb-1">Distance</p>
              <p className="text-xs font-black">{formatDistance(trip.distance || 0)}</p>
            </div>
            <div className="p-2 rounded-lg bg-secondary/30 border border-border/20 text-center">
              <p className="text-[8px] text-muted-foreground uppercase font-black tracking-widest mb-1">Date</p>
              <p className="text-xs font-black truncate">{formatDate(trip.departure_schedule || "")}</p>
            </div>
            <div className="p-2 rounded-lg bg-klando-gold/5 border border-klando-gold/20 text-center">
              <p className="text-[8px] text-klando-gold uppercase font-black tracking-widest mb-1">Prix</p>
              <p className="text-xs font-black text-klando-gold">{formatPrice(trip.passenger_price || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Participants & Impact */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Conducteur */}
        <Card className="border-border/40 overflow-hidden">
          <CardContent className="p-3">
            <div className="flex items-center justify-between mb-3">
              <p className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">Conducteur</p>
              {trip.driver_verified && (
                <div className="flex items-center gap-1 text-blue-500 bg-blue-500/5 px-1.5 py-0.5 rounded border border-blue-500/10">
                  <ShieldCheck className="w-2.5 h-2.5" />
                  <span className="text-[8px] font-black uppercase">Vérifié</span>
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-3">
              {trip.driver_photo ? (
                <div className="relative w-10 h-10 flex-shrink-0">
                  <Image src={trip.driver_photo} alt="" fill className="rounded-lg object-cover border border-border/50" />
                </div>
              ) : (
                <div className="w-10 h-10 rounded-lg bg-klando-burgundy flex items-center justify-center text-white text-sm font-black flex-shrink-0">
                  {(trip.driver_name || "C").charAt(0).toUpperCase()}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="font-bold text-xs truncate uppercase tracking-tight leading-none mb-1">{trip.driver_name}</p>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5 text-klando-gold">
                    <span className="text-[10px] font-black">{trip.driver_rating?.toFixed(1) || "-"}</span>
                    <Star className="w-2.5 h-2.5 fill-current" />
                  </div>
                  <span className="text-[9px] text-muted-foreground font-mono truncate">{trip.driver_phone || "Non renseigné"}</span>
                </div>
              </div>
              {trip.driver_id && (
                <Link href={`/users?selected=${trip.driver_id}`}>
                  <Button variant="ghost" size="icon" className="h-7 w-7 p-0 hover:bg-klando-gold/10 hover:text-klando-gold">
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Passagers & Impact */}
        <Card className="border-border/40">
          <CardContent className="p-3">
            <p className="text-[9px] font-black uppercase tracking-widest text-muted-foreground mb-3">Passagers ({trip.passengers.length}/{trip.seats_published})</p>
            
            <div className="space-y-2 mb-4">
              {trip.passengers.map((p) => (
                <div key={p.uid} className="flex items-center justify-between p-2 rounded-xl bg-secondary/30 border border-border/20 group hover:border-klando-gold/30 transition-all">
                  <div className="flex items-center gap-2 min-w-0">
                    {p.photo_url ? (
                      <div className="relative w-8 h-8 flex-shrink-0">
                        <Image src={p.photo_url} alt="" fill className="rounded-lg object-cover border border-border/50" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground text-[10px] font-black flex-shrink-0 border border-border/50">
                        {(p.display_name || "P").charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className="text-xs font-bold truncate text-foreground group-hover:text-klando-gold transition-colors">{p.display_name || "Passager"}</span>
                  </div>
                  <Link href={`/users?selected=${p.uid}`}>
                    <Button variant="ghost" size="icon" className="h-6 w-6 p-0 hover:bg-klando-gold/10 hover:text-klando-gold">
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </Link>
                </div>
              ))}
              {trip.passengers.length === 0 && (
                <p className="text-[10px] text-muted-foreground italic py-4 text-center">Aucune réservation confirmée</p>
              )}
            </div>
            
            <div className="flex items-center justify-between pt-2 border-t border-border/10">
              <div className="flex items-center gap-1.5 text-green-500">
                <Leaf className="w-3 h-3" />
                <span className="text-[10px] font-bold">{co2Saved} kg CO₂</span>
              </div>
              <div className="flex items-center gap-1.5 text-klando-gold">
                <Banknote className="w-3 h-3" />
                <span className="text-[10px] font-bold">{formatPrice(trip.driver_price || 0)} <span className="text-[8px] opacity-60">NET</span></span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}