"use client";

import { X, Users } from "lucide-react";
import { TripMapItem } from "@/types/trip";
import { SiteTripRequest } from "@/types/site-request";
import { TripMapPopup } from "@/components/map/trip-map-popup";
import { useRouter } from "next/navigation";

interface MapDetailsPopupProps {
  selectedTrip: TripMapItem | null;
  selectedRequest: SiteTripRequest | null;
  onClose: () => void;
}

export function MapDetailsPopup({
  selectedTrip,
  selectedRequest,
  onClose
}: MapDetailsPopupProps) {
  const router = useRouter();

  if (!selectedTrip && !selectedRequest) return null;

  return (
    <div className="absolute bottom-6 left-4 right-4 md:left-auto md:right-6 md:w-[400px] z-[1001] animate-in slide-in-from-bottom-4 duration-500 text-left">
      {selectedTrip ? (
        <TripMapPopup trip={selectedTrip} onClose={onClose} />
      ) : (
        <div className="bg-card/95 backdrop-blur-md border border-purple-500/30 rounded-3xl p-6 shadow-2xl relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-500/10 rounded-2xl text-purple-500">
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-black uppercase tracking-tight text-lg">Demande Client</h4>
              <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest">{selectedRequest?.contact_info}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-secondary/30 rounded-2xl border border-border/40">
              <p className="text-[10px] font-black uppercase text-muted-foreground mb-1">Départ</p>
              <p className="font-bold uppercase text-xs">{selectedRequest?.origin_city}</p>
            </div>
            <div className="p-4 bg-secondary/30 rounded-2xl border border-border/40">
              <p className="text-[10px] font-black uppercase text-muted-foreground mb-1">Arrivée</p>
              <p className="font-bold uppercase text-xs">{selectedRequest?.destination_city}</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => router.push(`/site-requests?id=${selectedRequest?.id}`)}
              className="flex-1 py-4 bg-purple-500 text-white font-black uppercase tracking-widest text-[10px] rounded-2xl hover:bg-purple-600 transition-all shadow-lg shadow-purple-500/20"
            >
              Voir dans le gestionnaire
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
