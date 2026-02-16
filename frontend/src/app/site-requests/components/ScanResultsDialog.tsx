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
      hasCoords: boolean;
      origin: string;
      destination: string;
      totalPending: number;
      radiusUsed: number;
    };
  } | null;
  onRetry: () => void;
}

export function ScanResultsDialog({ isOpen, onClose, results, onRetry }: ScanResultsDialogProps) {
  if (!results) return null;

  const { count, diagnostics } = results;
  const noMatches = count === 0;

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
              Rayon de recherche : {diagnostics?.radiusUsed} km
            </p>
          </div>
        </div>

        <div className="p-8 space-y-6">
          {noMatches && (
            <div className="space-y-4">
              <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                <div className="space-y-1">
                  <p className="text-sm font-black text-amber-900 uppercase">Pourquoi 0 résultat ?</p>
                  <p className="text-xs text-amber-800/70 font-medium leading-relaxed">
                    Le scanner cherche des trajets dont le départ ET l&apos;arrivée sont à moins de {diagnostics?.radiusUsed}km de la demande client.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-3">
                <div className="bg-white border border-slate-200 rounded-2xl p-4 flex items-center justify-between shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-100 rounded-lg"><MapPin className="w-4 h-4 text-slate-500" /></div>
                    <span className="text-[10px] font-black uppercase text-slate-500">Coordonnées GPS</span>
                  </div>
                  <Badge status={diagnostics?.hasCoords ? "OK" : "MISSING"} />
                </div>

                <div className="bg-white border border-slate-200 rounded-2xl p-4 flex items-center justify-between shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-100 rounded-lg"><Search className="w-4 h-4 text-slate-500" /></div>
                    <span className="text-[10px] font-black uppercase text-slate-500">Trajets analysés</span>
                  </div>
                  <span className="text-sm font-black text-slate-700">{diagnostics?.totalPending} en attente</span>
                </div>
              </div>
            </div>
          )}

          {!noMatches && (
            <div className="text-center space-y-2 py-4">
              <p className="text-slate-600 text-sm font-medium">
                Les trajets correspondants ont été enregistrés et sont maintenant visibles sur la carte live.
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button variant="outline" onClick={onClose} className="flex-1 h-12 rounded-2xl font-black uppercase tracking-widest text-[10px] border-slate-200">
              Fermer
            </Button>
            {noMatches && (
              <Button onClick={onRetry} className="flex-1 h-12 rounded-2xl font-black uppercase tracking-widest text-[10px] bg-amber-600 hover:bg-amber-700 text-white shadow-lg shadow-amber-600/20">
                Réessayer (15km)
              </Button>
            )}
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
