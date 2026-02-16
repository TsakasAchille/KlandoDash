import { TripMapItem } from "@/types/trip";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Eye, EyeOff, User, MapPin } from "lucide-react";

// Badge de statut
const statusStyles: Record<string, string> = {
  ACTIVE: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  COMPLETED: "bg-green-500/10 text-green-500 border-green-500/20",
  PENDING: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  CANCELLED: "bg-red-500/10 text-red-500 border-red-500/20",
  ARCHIVED: "bg-secondary text-muted-foreground border-border/20",
};

// Couleurs des polylines (même palette que trip-map)
const POLYLINE_COLORS = [
  "#EBC33F", "#3B82F6", "#22C55E", "#EF4444", "#A855F7",
  "#F97316", "#06B6D4", "#EC4899", "#84CC16", "#6366F1",
  "#14B8A6", "#F59E0B",
];

interface RecentTripsTableProps {
  trips: TripMapItem[];
  selectedTripId: string | undefined;
  hiddenTripIds: Set<string>;
  onSelectTrip: (trip: TripMapItem) => void;
  onHoverTrip: (tripId: string | null) => void;
  onToggleVisibility: (tripId: string) => void;
}

export function RecentTripsTable({
  trips,
  selectedTripId,
  hiddenTripIds,
  onSelectTrip,
  onHoverTrip,
  onToggleVisibility,
}: RecentTripsTableProps) {
  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-border hover:scrollbar-thumb-klando-gold/30">
        <div className="space-y-3">
          {trips.length === 0 ? (
            <div className="py-20 text-center flex flex-col items-center gap-3 opacity-40">
              <MapPin className="w-10 h-10" />
              <p className="text-[10px] font-black uppercase tracking-widest">Aucun trajet trouvé</p>
            </div>
          ) : (
            trips.map((trip, index) => {
              const isHidden = hiddenTripIds.has(trip.trip_id);
              const isSelected = selectedTripId === trip.trip_id;
              const polylineColor = isSelected ? "#EBC33F" : POLYLINE_COLORS[index % POLYLINE_COLORS.length];

              return (
                <div
                  key={trip.trip_id}
                  className={cn(
                    "group relative p-4 rounded-2xl border transition-all duration-300 cursor-pointer",
                    isSelected 
                      ? "bg-card border-klando-gold shadow-lg shadow-klando-gold/5 scale-[1.02]" 
                      : "bg-card/40 border-border/40 hover:border-klando-gold/30 hover:bg-card/60",
                    isHidden && "opacity-40 grayscale-[0.5]"
                  )}
                  onMouseEnter={() => onHoverTrip(trip.trip_id)}
                  onMouseLeave={() => onHoverTrip(null)}
                  onClick={() => onSelectTrip(trip)}
                >
                  {/* Indicateur de couleur */}
                  <div 
                    className="absolute top-0 left-0 bottom-0 w-1 rounded-l-2xl transition-all"
                    style={{ backgroundColor: polylineColor }}
                  />

                  <div className="flex flex-col gap-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex flex-col min-w-0">
                        <div className="flex items-center gap-2">
                          <div className="p-1.5 rounded-lg bg-secondary/80 border border-border/50">
                            <User className="w-3 h-3 text-klando-gold" />
                          </div>
                          <span className="text-xs font-black uppercase tracking-tight truncate text-foreground">
                            {trip.driver?.display_name || 'Inconnu'}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onToggleVisibility(trip.trip_id);
                          }}
                          className={cn(
                            "p-1.5 rounded-lg border transition-all",
                            isHidden 
                              ? "bg-secondary text-muted-foreground border-border/40" 
                              : "bg-klando-gold/10 text-klando-gold border-klando-gold/20"
                          )}
                        >
                          {isHidden ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                        <span className={cn(
                          "px-2 py-1 text-[8px] font-black uppercase tracking-widest rounded-lg border whitespace-nowrap",
                          statusStyles[trip.status || "ACTIVE"]
                        )}>
                          {trip.status}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex flex-col">
                        <span className="text-[10px] font-black uppercase tracking-tighter text-foreground/90">
                          {trip.departure_name?.split(',')[0]} ➜ {trip.destination_name?.split(',')[0]}
                        </span>
                        <span className="text-[9px] font-bold text-muted-foreground mt-0.5">
                          {formatDate(trip.departure_schedule || "")}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] font-black text-klando-gold block uppercase">
                          {trip.passenger_price || 0} XOF
                        </span>
                        <span className="text-[9px] font-bold text-muted-foreground">
                          {trip.seats_available} places libres
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
