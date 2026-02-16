"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Radar, AlertTriangle, CheckCircle2, MapPin, Search, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface ScanResultsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  results: {
    success: boolean;
    count: number;
    message: string;
    diagnostics?: {
      id: string;
      hasCoords: boolean;
      origin: string;
      destination: string;
      totalPending: number;
      radiusUsed: number;
    };
  } | null;
  onRetry: (radius: number) => void;
}

export function ScanResultsDialog({ isOpen, onClose, results, onRetry }: ScanResultsDialogProps) {
  if (!results) return null;

  const { count, diagnostics } = results;
  const noMatches = count === 0;

  const radiusOptions = [5, 15, 30, 50];

  return (
    <Dialog open={isOpen} onOpenChange={(o) => { if(!o) onClose(); }}>
      <DialogContent className="sm:max-w-[450px] bg-slate-50 border-none shadow-2xl p-0 overflow-hidden rounded-3xl">
        <DialogHeader className="sr-only">
          <DialogTitle>{noMatches ? "Aucun trajet trouvé" : "Scan terminé"}</DialogTitle>
        </DialogHeader>

        <div className={cn(
          "p-8 text-white flex flex-col items-center text-center space-y-4",
          noMatches ? "bg-amber-500" : "bg-green-600"
        )}>
          <div className="p-4 bg-white/20 rounded-full backdrop-blur-md">
            {noMatches ? <Radar className="w-10 h-10 animate-pulse" /> : <CheckCircle2 className="w-10 h-10" />}
          </div>
          <div>
            <h2 className="text-2xl font-black uppercase tracking-tight">
              {noMatches ? "Aucun trajet trouvé" : `${count} trajet(s) trouvé(s)`}
            </h2>
            <p className="text-white/80 text-xs font-bold uppercase tracking-widest mt-1">
              Rayon actuel : {diagnostics?.radiusUsed} km
            </p>
          </div>
        </div>

        <div className="p-8 space-y-6">
          <div className="space-y-4">
            <h4 className="text-[10px] font-black uppercase tracking-widest text-slate-400">Modifier le rayon de recherche</h4>
            <div className="grid grid-cols-4 gap-2">
              {radiusOptions.map((r) => (
                <button
                  key={r}
                  onClick={() => onRetry(r)}
                  className={cn(
                    "py-2 rounded-xl text-xs font-black transition-all border",
                    diagnostics?.radiusUsed === r
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-white text-slate-600 border-slate-200 hover:border-klando-gold"
                  )}
                >
                  {r}km
                </button>
              ))}
            </div>
          </div>

          {noMatches && (
            <div className="space-y-4">
              <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="space-y-1">
                  <p className="text-sm font-black text-amber-900 uppercase">Analyse</p>
                  <p className="text-xs text-amber-800/70 font-medium leading-relaxed">
                    Essayez d&apos;élargir le rayon (ex: 30km) pour trouver des trajets passant dans la région.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button variant="outline" onClick={onClose} className="flex-1 h-12 rounded-2xl font-black uppercase tracking-widest text-[10px] border-slate-200">
              Fermer
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Badge({ status }: { status: "OK" | "MISSING" }) {
  return (
    <div className={cn(
      "px-2 py-1 rounded-md text-[9px] font-black uppercase",
      status === "OK" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
    )}>
      {status === "OK" ? "Présentes" : "Manquantes"}
    </div>
  );
}
