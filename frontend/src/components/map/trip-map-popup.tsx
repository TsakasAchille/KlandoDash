import Link from "next/link";
import Image from "next/image";
import { X, Calendar, Car, ExternalLink, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TripMapItem } from "@/types/trip";
import { formatDate, formatPrice } from "@/lib/utils";
import { cn } from "@/lib/utils";

// Badge de statut
const statusStyles: Record<string, string> = {
  ACTIVE: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  COMPLETED: "bg-green-500/10 text-green-500 border-green-500/20",
  PENDING: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  CANCELLED: "bg-red-500/10 text-red-500 border-red-500/20",
  ARCHIVED: "bg-secondary text-muted-foreground border-border/20",
};

interface TripMapPopupProps {
  trip: TripMapItem;
  onClose: () => void;
}

export function TripMapPopup({ trip, onClose }: TripMapPopupProps) {
  return (
    <Card className="bg-card/95 backdrop-blur-xl border-border/40 shadow-2xl rounded-[2rem] overflow-hidden">
      <div className="relative">
        {/* Top Accent Bar */}
        <div className="h-1.5 w-full bg-gradient-to-r from-klando-gold via-klando-burgundy to-klando-gold" />
        
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 bg-secondary/80 hover:bg-secondary text-muted-foreground hover:text-white rounded-xl transition-all z-10"
        >
          <X className="w-4 h-4" />
        </button>

        <CardContent className="p-6 space-y-6">
          {/* Header: Status & Price */}
          <div className="flex items-center justify-between gap-4">
            <span className={cn(
              "px-3 py-1 text-[10px] font-black uppercase tracking-[0.2em] rounded-full border",
              statusStyles[trip.status || "ACTIVE"]
            )}>
              {trip.status}
            </span>
            <div className="text-right">
              <span className="text-2xl font-black text-klando-gold tracking-tighter">
                {formatPrice(trip.passenger_price || 0)}
              </span>
              <span className="text-[10px] font-bold text-muted-foreground block uppercase tracking-widest">par place</span>
            </div>
          </div>

          {/* Route Section */}
          <div className="space-y-4 bg-secondary/30 p-5 rounded-2xl border border-border/40">
            <div className="flex items-start gap-4">
              <div className="flex flex-col items-center gap-1 pt-1">
                <div className="w-3 h-3 rounded-full border-2 border-klando-gold bg-background" />
                <div className="w-0.5 h-8 bg-dashed border-l border-dashed border-border/60" />
                <div className="w-3 h-3 rounded-full bg-klando-gold" />
              </div>
              <div className="flex flex-col gap-5 flex-1 min-w-0">
                <div className="space-y-0.5">
                  <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Départ</span>
                  <p className="text-sm font-black uppercase tracking-tight truncate text-foreground">{trip.departure_name}</p>
                </div>
                <div className="space-y-0.5">
                  <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Arrivée</span>
                  <p className="text-sm font-black uppercase tracking-tight truncate text-foreground">{trip.destination_name}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Core Info Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-secondary/20 p-3 rounded-xl border border-border/20 flex flex-col gap-1">
              <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Calendar className="w-3 h-3 text-klando-gold" /> Calendrier
              </span>
              <span className="text-[11px] font-bold text-foreground">{formatDate(trip.departure_schedule || "")}</span>
            </div>
            <div className="bg-secondary/20 p-3 rounded-xl border border-border/20 flex flex-col gap-1">
              <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Car className="w-3 h-3 text-klando-gold" /> Occupation
              </span>
              <span className="text-[11px] font-bold text-foreground">{trip.seats_available}/{trip.seats_published} Places</span>
            </div>
          </div>

          {/* Driver & Passengers */}
          <div className="space-y-4">
            {trip.driver && (
              <div className="flex items-center justify-between p-3 rounded-2xl bg-secondary/40 border border-border/40">
                <div className="flex items-center gap-3">
                  <div className="relative w-10 h-10 rounded-xl overflow-hidden border border-border/50">
                    {trip.driver.photo_url ? (
                      <Image src={trip.driver.photo_url} alt="" fill className="object-cover" />
                    ) : (
                      <div className="w-full h-full bg-klando-burgundy flex items-center justify-center text-sm font-black text-white">
                        {trip.driver.display_name?.charAt(0)}
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-black uppercase tracking-tight text-foreground">{trip.driver.display_name}</p>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Star className="w-2.5 h-2.5 text-klando-gold fill-klando-gold" />
                      <span className="text-[10px] font-bold text-klando-gold">{trip.driver.rating?.toFixed(1) || "5.0"}</span>
                    </div>
                  </div>
                </div>
                <Link href={`/users?selected=${trip.driver.uid}`}>
                  <Button variant="ghost" size="sm" className="h-8 rounded-lg text-[10px] font-black uppercase tracking-widest hover:bg-klando-gold hover:text-klando-dark">
                    Profil
                  </Button>
                </Link>
              </div>
            )}

            {trip.passengers.length > 0 && (
              <div className="space-y-2">
                <p className="text-[9px] font-black uppercase tracking-[0.2em] text-muted-foreground px-1">Passagers ({trip.passengers.length})</p>
                <div className="flex flex-wrap gap-2">
                  {trip.passengers.map((p) => (
                    <Link key={p.uid} href={`/users?selected=${p.uid}`} title={p.display_name || ""}>
                      <div className="relative w-8 h-8 rounded-lg overflow-hidden border border-border/40 hover:border-klando-gold transition-all group">
                        {p.photo_url ? (
                          <Image src={p.photo_url} alt="" fill className="object-cover group-hover:scale-110 transition-transform" />
                        ) : (
                          <div className="w-full h-full bg-secondary flex items-center justify-center text-[10px] font-black">
                            {p.display_name?.charAt(0)}
                          </div>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Final Action */}
          <Link href={`/trips?selected=${trip.trip_id}`} className="block">
            <Button className="w-full h-12 bg-klando-burgundy hover:bg-klando-burgundy/90 text-white rounded-2xl font-black uppercase tracking-[0.2em] text-xs shadow-lg shadow-klando-burgundy/20 group">
              Détails Complets <ExternalLink className="ml-2 w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
            </Button>
          </Link>
        </CardContent>
      </div>
    </Card>
  );
}
