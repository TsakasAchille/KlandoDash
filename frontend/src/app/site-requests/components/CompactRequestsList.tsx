"use client";

import { SiteTripRequest } from "@/types/site-request";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Users, Radar, Sparkles, Loader2, Eye, EyeOff } from "lucide-react";

interface CompactRequestsListProps {
  requests: SiteTripRequest[];
  selectedId: string | null;
  hiddenIds: Set<string>;
  onSelect: (id: string) => void;
  onToggleVisibility: (id: string) => void;
  onShowAll: () => void;
  onHideAll: () => void;
  onScan: (id: string) => void;
  scanningId: string | null;
}

export function CompactRequestsList({ 
  requests, 
  selectedId, 
  hiddenIds,
  onSelect, 
  onToggleVisibility,
  onShowAll,
  onHideAll,
  onScan, 
  scanningId 
}: CompactRequestsListProps) {
  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="px-2 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-purple-500/10 rounded-lg text-purple-600">
              <Users className="w-4 h-4" />
            </div>
            <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Demandes Clients</h4>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={onShowAll}
              className="text-[9px] font-black uppercase text-purple-500 hover:underline flex items-center gap-1"
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
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-2 custom-scrollbar">
        {requests.map((req) => {
          const isSelected = selectedId === req.id;
          const isHidden = hiddenIds.has(req.id);
          const hasMatches = req.matches && req.matches.length > 0;
          const isScanning = scanningId === req.id;

          return (
            <div
              key={req.id}
              onClick={() => onSelect(req.id)}
              className={cn(
                "p-3 rounded-2xl border cursor-pointer transition-all duration-300 relative",
                isSelected 
                  ? "bg-purple-500/10 border-purple-500/50 shadow-lg shadow-purple-500/5 scale-[1.02]" 
                  : "bg-card/40 border-border/40 hover:border-purple-500/30 hover:bg-purple-500/5",
                isHidden && "opacity-40 grayscale-[0.5]"
              )}
            >
              <div className="flex justify-between items-start mb-1.5">
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleVisibility(req.id);
                    }}
                    className={cn(
                      "p-1 rounded-md border transition-all flex-shrink-0",
                      isHidden 
                        ? "bg-secondary text-muted-foreground border-border/40" 
                        : "bg-purple-500/10 text-purple-600 border-purple-200 hover:bg-purple-500/20"
                    )}
                  >
                    {isHidden ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                  </button>
                  <span className="text-[9px] font-black uppercase text-purple-500 truncate">
                    {req.contact_info}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {hasMatches && (
                    <div className="flex items-center gap-1 text-[8px] font-black text-green-500 uppercase bg-green-500/10 px-1.5 py-0.5 rounded-full">
                      <Sparkles className="w-2 h-2" />
                      {req.matches?.length}
                    </div>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onScan(req.id);
                    }}
                    className={cn(
                      "p-1 rounded-md transition-colors",
                      isScanning ? "text-blue-500 animate-spin" : "text-muted-foreground hover:text-blue-500"
                    )}
                  >
                    <Radar className="w-3 h-3" />
                  </button>
                </div>
              </div>
              <div className="text-[10px] font-black uppercase tracking-tight text-foreground truncate pl-1">
                {req.origin_city} ➜ {req.destination_city}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
