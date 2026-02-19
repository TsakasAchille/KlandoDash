"use client";

import { AIRecommendation } from "@/app/marketing/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Zap, Sparkles, MapPin, Car
} from "lucide-react";
import { format } from "date-fns";
import { fr as frLocale } from "date-fns/locale";
import { cn } from "@/lib/utils";

interface StrategyTabProps {
  recommendations: AIRecommendation[];
  strategyTab: string;
  onStrategyTabChange: (tab: string) => void;
  onApply: (id: string) => void;
  onDismiss: (id: string) => void;
  onGlobalScan: () => void;
}

export function StrategyTab({
  recommendations,
  strategyTab,
  onStrategyTabChange,
  onApply,
  onDismiss,
  onGlobalScan
}: StrategyTabProps) {
  // Filtrer les recommandations selon l'onglet (To Treat vs History)
  const filteredRecommendations = recommendations.filter(reco => {
    if (strategyTab === "to-treat") return reco.status === 'PENDING';
    return reco.status === 'APPLIED' || reco.status === 'DISMISSED';
  });

  const renderContent = (reco: AIRecommendation) => {
    if (typeof reco.content === 'string') {
      return <p className="text-[11px] text-muted-foreground leading-relaxed text-left">{reco.content}</p>;
    }

    if (reco.type === 'TRACTION' && reco.content?.request) {
      const { request, matches_count } = reco.content;
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-2 bg-white/5 p-2.5 rounded-xl border border-white/5">
            <div className="flex flex-col items-center gap-1">
              <MapPin className="w-3 h-3 text-klando-gold" />
              <div className="w-px h-3 bg-white/10" />
              <MapPin className="w-3 h-3 text-klando-burgundy" />
            </div>
            <div className="flex flex-col gap-1.5 flex-1">
              <span className="text-[10px] font-black uppercase tracking-tight truncate">{request.origin}</span>
              <span className="text-[10px] font-black uppercase tracking-tight text-muted-foreground truncate">{request.destination || "Destination libre"}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 px-1">
            <Car className="w-3.5 h-3.5 text-green-400" />
            <span className="text-[10px] font-black text-green-400 uppercase tracking-widest">
              {matches_count} trajet{matches_count > 1 ? 's' : ''} à proximité
            </span>
          </div>
        </div>
      );
    }

    return (
      <p className="text-[11px] text-muted-foreground leading-relaxed text-left">
        {reco.content?.message || "Données analytiques non disponibles"}
      </p>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-klando-gold/10 rounded-xl">
            <Zap className="w-5 h-5 text-klando-gold" />
          </div>
          <div className="text-left">
            <h3 className="font-black uppercase tracking-tight text-lg text-white">Opportunités de Croissance</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Actions recommandées par le radar analytique</p>
          </div>
        </div>

        <div className="flex bg-white/5 p-1 rounded-xl border border-white/5 self-start sm:self-auto">
          <button
            onClick={() => onStrategyTabChange("to-treat")}
            className={cn(
              "px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
              strategyTab === "to-treat" ? "bg-klando-gold text-klando-dark shadow-lg shadow-klando-gold/10" : "text-muted-foreground hover:text-white"
            )}
          >
            À Traiter
          </button>
          <button
            onClick={() => onStrategyTabChange("history")}
            className={cn(
              "px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all",
              strategyTab === "history" ? "bg-white/10 text-white" : "text-muted-foreground hover:text-white"
            )}
          >
            Archives
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRecommendations.length > 0 ? (
          filteredRecommendations.map((reco) => (
            <Card key={reco.id} className={cn(
              "bg-card/40 backdrop-blur-md border-white/5 hover:border-klando-gold/30 transition-all duration-500 group overflow-hidden",
              reco.status !== 'PENDING' && "opacity-60"
            )}>
              <div className="p-6 space-y-4">
                <div className="flex justify-between items-start">
                  <Badge className={cn(
                    "font-black uppercase text-[8px] tracking-widest px-2 py-0.5",
                    reco.type === 'TRACTION' ? "bg-green-500/20 text-green-400" : "bg-blue-500/20 text-blue-400"
                  )}>
                    {reco.type}
                  </Badge>
                  <div className="flex flex-col items-end">
                    <span className="text-[9px] font-bold text-muted-foreground/40">{format(new Date(reco.created_at), 'dd MMM, HH:mm', { locale: frLocale })}</span>
                    {reco.status !== 'PENDING' && (
                      <span className="text-[8px] font-black uppercase text-klando-gold/60">{reco.status === 'APPLIED' ? 'Validé' : 'Ignoré'}</span>
                    )}
                  </div>
                </div>

                <h4 className="font-black text-white uppercase tracking-tight group-hover:text-klando-gold transition-colors text-left truncate" title={reco.title}>{reco.title}</h4>
                
                <div className="min-h-[60px] flex flex-col justify-center">
                  {renderContent(reco)}
                </div>

                {reco.status === 'PENDING' && (
                  <div className="pt-4 flex gap-2">
                    <Button 
                      onClick={() => onApply(reco.id)}
                      className="flex-1 rounded-xl bg-klando-gold hover:bg-klando-gold/80 text-klando-dark font-black text-[10px] uppercase tracking-widest h-10 shadow-lg shadow-klando-gold/10"
                    >
                      Valider
                    </Button>
                    <Button 
                      onClick={() => onDismiss(reco.id)}
                      variant="ghost"
                      className="rounded-xl hover:bg-white/5 text-muted-foreground font-black text-[10px] uppercase tracking-widest h-10"
                    >
                      Ignorer
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-20 bg-white/[0.02] border border-dashed border-white/5 rounded-[3rem] flex flex-col items-center justify-center space-y-4 opacity-30">
            <Sparkles className="w-12 h-12 text-muted-foreground" />
            <p className="text-xs font-black uppercase tracking-[0.3em] text-muted-foreground italic">
              {strategyTab === "to-treat" ? "Aucune opportunité à traiter" : "Historique vide"}
            </p>
            {strategyTab === "to-treat" && (
              <Button 
                onClick={onGlobalScan}
                variant="outline" 
                className="mt-4 border-white/10 hover:bg-white/5 text-[10px] font-black uppercase tracking-widest rounded-xl"
              >
                Scanner maintenant
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
