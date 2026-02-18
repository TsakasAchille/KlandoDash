"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  BarChart3, Sparkles, Loader2, TrendingUp, ArrowRightCircle 
} from "lucide-react";
import { MarketingInsight } from "../../types";
import { cn } from "@/lib/utils";

interface IntelligenceTabProps {
  insights: MarketingInsight[];
  isScanning: boolean;
  onScan: () => void;
  onSelectInsight: (insight: MarketingInsight) => void;
}

export function IntelligenceTab({ 
  insights, 
  isScanning, 
  onScan, 
  onSelectInsight 
}: IntelligenceTabProps) {
  return (
    <div className="grid md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {insights.length > 0 ? (
        insights.map((insight) => (
          <Card 
            key={insight.id} 
            className="bg-card/40 backdrop-blur-md border-white/5 hover:border-blue-500/30 transition-all duration-500 group relative overflow-hidden flex flex-col h-full"
          >
            <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
              <TrendingUp className="w-12 h-12 text-blue-500" />
            </div>
            <CardContent className="p-6 space-y-4 flex flex-col h-full">
              <div className="flex justify-between items-start">
                <span className={cn(
                  "text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border",
                  insight.category === 'REVENUE' ? "bg-green-500/10 text-green-500 border-green-500/20" :
                  insight.category === 'CONVERSION' ? "bg-purple-500/10 text-purple-500 border-purple-500/20" :
                  "bg-blue-500/10 text-blue-500 border-blue-500/20"
                )}>
                  {insight.category}
                </span>
                <span className="text-[9px] font-bold text-muted-foreground/40 uppercase tabular-nums">
                  {new Date(insight.created_at).toLocaleDateString('fr-FR')}
                </span>
              </div>
              <div>
                <h4 className="font-black text-sm text-white uppercase tracking-tight group-hover:text-blue-400 transition-colors">
                  {insight.title}
                </h4>
                <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed line-clamp-3 italic">
                  {insight.summary}
                </p>
              </div>
              <div className="mt-auto pt-4">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={() => onSelectInsight(insight)}
                  className="w-full rounded-xl bg-blue-500/10 text-blue-500 hover:bg-blue-600 hover:text-white border border-blue-500/20 font-black text-[10px] uppercase tracking-widest h-9 transition-all"
                >
                  Lire le rapport <ArrowRightCircle className="w-3.5 h-3.5 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))
      ) : (
        <div className="col-span-3 flex flex-col items-center justify-center py-24 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
          <div className="p-4 bg-white/5 rounded-full"><BarChart3 className="w-10 h-10 text-muted-foreground/20" /></div>
          <div className="space-y-1">
            <p className="text-sm font-bold text-white uppercase tracking-widest">Aucune analyse disponible</p>
            <p className="text-[10px] text-muted-foreground font-medium max-w-xs mx-auto">
              Lancez un Scan IA Stratégique pour générer des rapports d&apos;aide à la décision.
            </p>
          </div>
          <Button 
            onClick={onScan} 
            disabled={isScanning}
            className="bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl px-8 h-12 shadow-xl shadow-blue-500/20 mt-4"
          >
            {isScanning ? <Loader2 className="w-5 h-5 animate-spin mr-3" /> : <Sparkles className="w-5 h-5 mr-3" />}
            Générer les rapports
          </Button>
        </div>
      )}
    </div>
  );
}
