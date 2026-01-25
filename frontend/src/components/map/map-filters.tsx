"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MapFilters as MapFiltersType } from "@/types/trip";

interface MapFiltersProps {
  filters: MapFiltersType;
  drivers: Array<{ uid: string; display_name: string | null }>;
  onFilterChange: (filters: Partial<MapFiltersType>) => void;
}

export function MapFilters({ filters, drivers, onFilterChange }: MapFiltersProps) {
  return (
    <Card className="bg-klando-dark border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm text-klando-gold">Filtres</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Statut */}
        <div className="space-y-1">
          <label className="text-xs text-white">Statut</label>
          <Select
            value={filters.status}
            onValueChange={(value) =>
              onFilterChange({ status: value as MapFiltersType["status"] })
            }
          >
            <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 border-gray-600">
              <SelectItem value="ALL">Tous</SelectItem>
              <SelectItem value="ACTIVE">Actifs</SelectItem>
              <SelectItem value="COMPLETED">Terminés</SelectItem>
              <SelectItem value="PENDING">En attente</SelectItem>
              <SelectItem value="CANCELLED">Annulés</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Conducteur */}
        <div className="space-y-1">
          <label className="text-xs text-white">Conducteur</label>
          <Select
            value={filters.driverId || "ALL"}
            onValueChange={(value) =>
              onFilterChange({ driverId: value === "ALL" ? null : value })
            }
          >
            <SelectTrigger className="bg-gray-800 border-gray-600 text-white">
              <SelectValue placeholder="Tous les conducteurs" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 border-gray-600">
              <SelectItem value="ALL">Tous</SelectItem>
              {drivers.map((d) => (
                <SelectItem key={d.uid} value={d.uid}>
                  {d.display_name || "Sans nom"}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Date de début */}
        <div className="space-y-1">
          <label className="text-xs text-white">Date début</label>
          <input
            type="date"
            value={filters.dateFrom || ""}
            onChange={(e) => onFilterChange({ dateFrom: e.target.value || null })}
            className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-klando-gold"
          />
        </div>

        {/* Date de fin */}
        <div className="space-y-1">
          <label className="text-xs text-white">Date fin</label>
          <input
            type="date"
            value={filters.dateTo || ""}
            onChange={(e) => onFilterChange({ dateTo: e.target.value || null })}
            className="w-full px-3 py-2 text-sm bg-gray-800 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-1 focus:ring-klando-gold"
          />
        </div>
      </CardContent>
    </Card>
  );
}
