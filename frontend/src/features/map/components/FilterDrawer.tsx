"use client";

import { X, Filter } from "lucide-react";
import { MapFilters } from "@/components/map/map-filters";

interface FilterDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  filters: any;
  drivers: any[];
  onFilterChange: (filters: any) => void;
}

export function FilterDrawer({
  isOpen,
  onClose,
  filters,
  drivers,
  onFilterChange
}: FilterDrawerProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[2000] flex justify-end">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
        onClick={onClose}
      />
      <div className="relative h-full w-full sm:w-[400px] bg-card border-l border-border/40 shadow-2xl animate-in slide-in-from-right duration-500 flex flex-col text-left">
        <div className="p-6 border-b border-border/40 flex justify-between items-center bg-muted/30">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-klando-gold/10 rounded-xl">
              <Filter className="w-5 h-5 text-klando-gold" />
            </div>
            <h3 className="text-xl font-black uppercase tracking-tight text-foreground">Configuration de l&apos;affichage</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-muted-foreground hover:text-white transition-colors rounded-xl hover:bg-secondary"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar">
          <div className="space-y-8">
            <MapFilters
              filters={filters}
              drivers={drivers}
              onFilterChange={onFilterChange}
            />
          </div>
        </div>

        <div className="p-6 border-t border-border/40 bg-muted/20">
          <button
            onClick={onClose}
            className="w-full py-4 bg-klando-gold text-klando-dark font-black uppercase tracking-[0.2em] rounded-2xl shadow-lg hover:shadow-klando-gold/20 transition-all"
          >
            Appliquer les filtres
          </button>
        </div>
      </div>
    </div>
  );
}
