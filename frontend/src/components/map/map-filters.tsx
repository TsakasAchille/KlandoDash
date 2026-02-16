import { MapFilters as MapFiltersType } from "@/types/trip";
import { Users, Calendar, ShieldCheck, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface MapFiltersProps {
  filters: MapFiltersType & { showRequests: boolean };
  drivers: Array<{ uid: string; display_name: string | null }>;
  onFilterChange: (filters: Partial<MapFiltersType & { showRequests: boolean }>) => void;
}

export function MapFilters({ filters, drivers, onFilterChange }: MapFiltersProps) {
  return (
    <div className="space-y-8">
      {/* Section Statut */}
      <div className="space-y-4">
        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold flex items-center gap-2">
          <ShieldCheck className="w-3 h-3" /> État des Trajets
        </h4>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: "ALL", label: "Tous" },
            { id: "ACTIVE", label: "Actifs" },
            { id: "PENDING", label: "En attente" },
            { id: "COMPLETED", label: "Terminés" }
          ].map((s) => (
            <button
              key={s.id}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              onClick={() => onFilterChange({ status: s.id as any })}
              className={cn(
                "py-3 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all",
                filters.status === s.id 
                  ? "bg-klando-gold text-klando-dark border-klando-gold shadow-lg shadow-klando-gold/20" 
                  : "bg-secondary/50 text-muted-foreground border-border/40 hover:border-klando-gold/30"
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Section Conducteur */}
      <div className="space-y-4">
        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold flex items-center gap-2">
          <User className="w-3 h-3" /> Filtrer par Conducteur
        </h4>
        <div className="relative">
          <select
            value={filters.driverId || "ALL"}
            onChange={(e) => onFilterChange({ driverId: e.target.value === "ALL" ? null : e.target.value })}
            className="w-full h-12 bg-secondary/50 border border-border/40 rounded-2xl px-4 text-xs font-bold appearance-none focus:outline-none focus:border-klando-gold/50 transition-all text-foreground"
          >
            <option value="ALL">Tous les conducteurs</option>
            {drivers.map((d) => (
              <option key={d.uid} value={d.uid} className="text-black">
                {d.display_name || "Sans nom"}
              </option>
            ))}
          </select>
          <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none opacity-40">
            <Users className="w-4 h-4 text-foreground" />
          </div>
        </div>
      </div>

      {/* Section Période */}
      <div className="space-y-4">
        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-klando-gold flex items-center gap-2">
          <Calendar className="w-3 h-3" /> Période de départ
        </h4>
        <div className="grid grid-cols-1 gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground ml-2">Du</label>
            <input
              type="date"
              value={filters.dateFrom || ""}
              onChange={(e) => onFilterChange({ dateFrom: e.target.value || null })}
              className="w-full h-12 bg-secondary/50 border border-border/40 rounded-2xl px-4 text-xs font-bold focus:outline-none focus:border-klando-gold/50 transition-all text-foreground"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-[9px] font-black uppercase tracking-widest text-muted-foreground ml-2">Au</label>
            <input
              type="date"
              value={filters.dateTo || ""}
              onChange={(e) => onFilterChange({ dateTo: e.target.value || null })}
              className="w-full h-12 bg-secondary/50 border border-border/40 rounded-2xl px-4 text-xs font-bold focus:outline-none focus:border-klando-gold/50 transition-all text-foreground"
            />
          </div>
        </div>
      </div>

      {/* Boutons d'action */}
      <div className="pt-4">
        <button
          onClick={() => onFilterChange({ status: "PENDING", driverId: null, dateFrom: null, dateTo: null, showRequests: false })}
          className="w-full py-4 rounded-2xl border border-dashed border-border/60 text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground hover:text-klando-gold hover:border-klando-gold/40 transition-all"
        >
          Réinitialiser tous les filtres
        </button>
      </div>
    </div>
  );
}
