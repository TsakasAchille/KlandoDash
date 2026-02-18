"use client";

import { X, Sparkles, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SiteTripRequest } from "@/types/site-request";

interface MapFocusHeaderProps {
  selectedRequest: SiteTripRequest | null;
  onClear: () => void;
}

export function MapFocusHeader({ selectedRequest, onClear }: MapFocusHeaderProps) {
  if (!selectedRequest) return null;

  const matchCount = selectedRequest.matches?.length || 0;

  return (
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] w-[90%] max-w-lg">
      <div className="bg-klando-dark/95 backdrop-blur-md border border-green-500/30 rounded-2xl p-4 shadow-2xl flex items-center justify-between gap-4 animate-in slide-in-from-top-4 duration-500">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/20 rounded-xl">
            <Sparkles className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <p className="text-[10px] font-black text-green-500 uppercase tracking-widest leading-none mb-1">Mode Analyse Business</p>
            <h4 className="text-sm font-black text-white uppercase truncate max-w-[200px]">
              {selectedRequest.origin_city} ➜ {selectedRequest.destination_city}
            </h4>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block border-l border-white/10 pl-4">
            <p className="text-[9px] font-bold text-white/40 uppercase">Trajets filtrés</p>
            <p className="text-xs font-black text-white">{matchCount} match{matchCount > 1 ? 'es' : ''}</p>
          </div>
          <Button 
            onClick={onClear}
            size="sm"
            className="bg-white hover:bg-white/90 text-klando-dark font-black uppercase text-[10px] rounded-xl h-10 px-4"
          >
            <X className="w-3.5 h-3.5 mr-2" /> Quitter
          </Button>
        </div>
      </div>
    </div>
  );
}
