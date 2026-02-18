"use client";

import { AIRecommendation } from "@/app/marketing/types";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Zap, Sparkles
} from "lucide-react";
import { format } from "date-fns";
import { fr as frLocale } from "date-fns/locale";
import { cn } from "@/lib/utils";

interface StrategyTabProps {
  recommendations: AIRecommendation[];
  onApply: (id: string) => void;
  onDismiss: (id: string) => void;
}

export function StrategyTab({
  recommendations,
  onApply,
  onDismiss
}: StrategyTabProps) {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between px-2 text-left">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-klando-gold/10 rounded-xl">
            <Zap className="w-5 h-5 text-klando-gold" />
          </div>
          <div>
            <h3 className="font-black uppercase tracking-tight text-lg text-white">Opportunités de Croissance</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Actions recommandées par l&apos;intelligence Klando</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations.length > 0 ? (
          recommendations.map((reco) => (
            <Card key={reco.id} className="bg-card/40 backdrop-blur-md border-white/5 hover:border-klando-gold/30 transition-all duration-500 group overflow-hidden">
              <div className="p-6 space-y-4">
                <div className="flex justify-between items-start">
                  <Badge className={cn(
                    "font-black uppercase text-[8px] tracking-widest px-2 py-0.5",
                    reco.type === 'TRACTION' ? "bg-green-500/20 text-green-400" : "bg-blue-500/20 text-blue-400"
                  )}>
                    {reco.type}
                  </Badge>
                  <span className="text-[9px] font-bold text-muted-foreground/40">{format(new Date(reco.created_at), 'dd MMM, HH:mm', { locale: frLocale })}</span>
                </div>

                <h4 className="font-black text-white uppercase tracking-tight group-hover:text-klando-gold transition-colors text-left">{reco.title}</h4>
                
                <p className="text-[11px] text-muted-foreground leading-relaxed text-left">
                  {typeof reco.content === 'string' ? reco.content : reco.content?.message || "Analyse en cours..."}
                </p>

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
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-20 bg-white/[0.02] border border-dashed border-white/5 rounded-[3rem] flex flex-col items-center justify-center space-y-4 opacity-30">
            <Sparkles className="w-12 h-12 text-muted-foreground" />
            <p className="text-xs font-black uppercase tracking-[0.3em] text-muted-foreground italic">Aucune opportunité détectée pour le moment</p>
          </div>
        )}
      </div>
    </div>
  );
}
