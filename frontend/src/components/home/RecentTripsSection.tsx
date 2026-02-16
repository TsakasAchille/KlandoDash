import { cn } from "@/lib/utils";
import { Clock, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Trip } from "@/types/trip";

interface RecentTripsSectionProps {
  trips: Trip[];
}

export function RecentTripsSection({ trips }: RecentTripsSectionProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-black flex items-center gap-2 uppercase tracking-widest">
          <Clock className="w-5 h-5 text-klando-gold" />
          Trajets Récents
        </h2>
        <Link href="/trips" className="text-[10px] font-black hover:text-klando-gold transition-colors tracking-widest text-muted-foreground underline underline-offset-4">TOUT VOIR</Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {trips.map((trip) => (
          <Link key={trip.trip_id} href={`/trips?selected=${trip.trip_id}`}>
            <div className="p-5 rounded-2xl bg-card border border-border/40 hover:border-klando-gold/40 transition-all duration-300 group h-full flex flex-col justify-between shadow-sm hover:shadow-md">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className={cn(
                    "text-[9px] font-black px-2.5 py-1 rounded-lg",
                    trip.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-500' : 'bg-secondary text-muted-foreground'
                  )}>
                    {trip.status}
                  </span>
                  <p className="text-[9px] font-mono text-muted-foreground/60 tracking-tighter">#{trip.trip_id.slice(-6)}</p>
                </div>
                <div className="flex items-center gap-3 mb-6">
                  <div className="flex flex-col flex-1 min-w-0">
                    <p className="font-black text-sm truncate uppercase tracking-tight">{trip.departure_city}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="w-1 h-1 rounded-full bg-klando-gold" />
                      <p className="text-[11px] text-muted-foreground truncate font-medium">{trip.destination_city}</p>
                    </div>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowRight className="w-4 h-4 text-klando-gold" />
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2.5 pt-4 border-t border-border/30">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-secondary to-secondary/30 flex items-center justify-center text-[11px] font-black border border-border/50 text-klando-gold">
                  {trip.driver_name.charAt(0)}
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] font-black text-foreground truncate">{trip.driver_name}</p>
                  <p className="text-[8px] text-muted-foreground font-bold tracking-widest uppercase">Conducteur</p>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
