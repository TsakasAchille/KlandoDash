"use client";

import { MarketingInsight } from "@/app/marketing/types";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, ChevronRight, Sparkles, Loader2
} from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

interface IntelligenceTabProps {
  insights: MarketingInsight[];
  isScanning: boolean;
  onScan: () => void;
  onSelect: (insight: MarketingInsight) => void;
}

export function IntelligenceTab({
  insights,
  isScanning,
  onScan,
  onSelect
}: IntelligenceTabProps) {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between px-2 text-left">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-xl">
            <BarChart3 className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-left">
            <h3 className="font-black uppercase tracking-tight text-lg text-white">Analyses Stratégiques</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Rapports IA générés périodiquement</p>
          </div>
        </div>
        
        <Button 
          onClick={onScan} 
          disabled={isScanning}
          className="rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-[10px] uppercase tracking-widest gap-2 shadow-lg shadow-blue-500/20"
        >
          {isScanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          Lancer Analyse IA
        </Button>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {insights.length > 0 ? (
          insights.map((insight) => (
            <Card 
              key={insight.id} 
              onClick={() => onSelect(insight)}
              className="bg-card/40 backdrop-blur-md border-white/5 hover:border-blue-500/30 transition-all duration-500 group overflow-hidden cursor-pointer flex flex-col h-[300px]"
            >
              <div className="p-6 flex-1 flex flex-col space-y-4">
                <div className="flex justify-between items-start">
                  <div className="px-2 py-0.5 bg-blue-500/20 rounded text-[8px] font-black text-blue-400 uppercase tracking-widest border border-blue-500/20">
                    {insight.category}
                  </div>
                  <span className="text-[9px] font-bold text-muted-foreground/40 italic">
                    {format(new Date(insight.created_at), 'dd MMMM yyyy', { locale: fr })}
                  </span>
                </div>

                <h4 className="font-black text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors text-left line-clamp-2">
                  {insight.title}
                </h4>
                
                <p className="text-[11px] text-muted-foreground leading-relaxed italic text-left line-clamp-4">
                  &quot;{insight.summary}&quot;
                </p>

                <div className="mt-auto pt-4 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                    <span className="text-[8px] font-black uppercase text-blue-400">Rapport Complet</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground/20 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full py-20 bg-white/[0.02] border border-dashed border-white/5 rounded-[3rem] flex flex-col items-center justify-center space-y-4 opacity-30">
            <BarChart3 className="w-12 h-12 text-muted-foreground" />
            <p className="text-xs font-black uppercase tracking-[0.3em] text-muted-foreground italic">Aucune analyse disponible. Cliquez sur &quot;Lancer Analyse IA&quot;</p>
          </div>
        )}
      </div>
    </div>
  );
}
