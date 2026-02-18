"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Target, History } from "lucide-react";
import { RecommendationCard } from "@/features/site-requests/components/ai/RecommendationCard";
import { AIRecommendation } from "../../types";

interface StrategyTabProps {
  recommendations: AIRecommendation[];
  strategyTab: string;
  onStrategyTabChange: (value: string) => void;
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
  const pending = recommendations.filter(r => r.status === 'PENDING');
  const treated = recommendations
    .filter(r => r.status === 'APPLIED')
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <Tabs value={strategyTab} onValueChange={onStrategyTabChange} className="space-y-6">
      <div className="flex items-center justify-between px-2">
        <TabsList className="bg-white/5 border border-white/10 p-1 h-10 rounded-xl">
          <TabsTrigger value="to-treat" className="rounded-lg px-4 py-1.5 data-[state=active]:bg-green-600 data-[state=active]:text-white font-bold text-[10px] uppercase tracking-wider">
            À Valider ({pending.length})
          </TabsTrigger>
          <TabsTrigger value="treated" className="rounded-lg px-4 py-1.5 data-[state=active]:bg-white/10 data-[state=active]:text-white font-bold text-[10px] uppercase tracking-wider">
            Déjà Validées ({treated.length})
          </TabsTrigger>
        </TabsList>
      </div>

      <TabsContent value="to-treat" className="outline-none">
        <div className="grid md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
          {pending.length > 0 ? (
            pending.map((reco) => (
              <RecommendationCard 
                key={reco.id} 
                reco={reco} 
                onApply={onApply}
                onDismiss={onDismiss}
              />
            ))
          ) : (
            <div className="col-span-3 flex flex-col items-center justify-center py-20 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
              <div className="p-4 bg-white/5 rounded-full"><Target className="w-8 h-8 text-muted-foreground/20" /></div>
              <p className="text-sm font-bold text-white uppercase">Aucune nouvelle opportunité</p>
              <Button onClick={onGlobalScan} variant="outline" size="sm" className="rounded-xl border-white/10 text-[10px] font-black uppercase">
                Relancer un scan
              </Button>
            </div>
          )}
        </div>
      </TabsContent>

      <TabsContent value="treated" className="outline-none">
        <div className="grid md:grid-cols-3 gap-6 opacity-60 grayscale-[0.5] hover:grayscale-0 hover:opacity-100 transition-all duration-500 animate-in fade-in slide-in-from-bottom-2">
          {treated.length > 0 ? (
            treated.map((reco) => (
              <RecommendationCard 
                key={reco.id} 
                reco={reco} 
                onApply={() => {}} 
                onDismiss={onDismiss}
              />
            ))
          ) : (
            <div className="col-span-3 flex flex-col items-center justify-center py-20 text-center opacity-20">
              <History className="w-12 h-12 mb-4" />
              <p className="text-[10px] font-black uppercase tracking-widest">Aucun historique récent</p>
            </div>
          )}
        </div>
      </TabsContent>
    </Tabs>
  );
}
