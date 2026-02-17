"use client";

import { useState, useEffect } from "react";
import { runGlobalScanAction, getStoredRecommendationsAction, updateRecommendationStatusAction } from "./actions";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, RefreshCw, Zap, Info, ShieldAlert, Target, TrendingUp, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { RecommendationCard, AIRecommendation } from "@/features/site-requests/components/ai/RecommendationCard";
import { cn } from "@/lib/utils";

export function KlandoAIClient() {
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchRecommendations = async () => {
    setIsLoading(true);
    const res = await getStoredRecommendationsAction();
    if (res.success) {
      setRecommendations(res.data as AIRecommendation[]);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    const res = await runGlobalScanAction();
    if (res.success) {
      toast.success(`${res.count} nouvelles recommandations générées.`);
      fetchRecommendations();
    } else {
      toast.error("Échec du scan global.");
    }
    setIsRefreshing(false);
  };

  const handleApply = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'APPLIED');
    if (res.success) {
      toast.success("Action enregistrée !");
      setRecommendations(prev => prev.filter(r => r.id !== id));
    }
  };

  const handleDismiss = async (id: string) => {
    const res = await updateRecommendationStatusAction(id, 'DISMISSED');
    if (res.success) {
      setRecommendations(prev => prev.filter(r => r.id !== id));
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-20">
      {/* Header Info avec CTA de scan */}
      <div className="grid md:grid-cols-12 gap-6 items-center bg-gradient-to-br from-klando-dark to-slate-900 p-8 rounded-[2.5rem] border border-white/5 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5"><Sparkles className="w-48 h-48 text-klando-gold" /></div>
        
        <div className="md:col-span-8 space-y-4 relative z-10">
          <div className="inline-flex items-center gap-2 bg-klando-gold/10 px-3 py-1 rounded-full border border-klando-gold/20">
            <Zap className="w-3 h-3 text-klando-gold" />
            <span className="text-[10px] font-black uppercase tracking-widest text-klando-gold">Système prédictif actif</span>
          </div>
          <h2 className="text-2xl font-black text-white uppercase tracking-tight leading-tight">
            Yobé Operational Intelligence
          </h2>
          <p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
            Yobé analyse en continu les demandes clients, les trajets en attente et l&apos;activité des chauffeurs pour vous suggérer les meilleures actions opérationnelles.
          </p>
        </div>

        <div className="md:col-span-4 flex justify-end relative z-10">
          <Button 
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="bg-klando-gold hover:bg-klando-gold/90 text-klando-dark font-black px-8 h-14 rounded-2xl shadow-xl shadow-klando-gold/10 group transition-all"
          >
            {isRefreshing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-3" />
                Analyse en cours...
              </>
            ) : (
              <>
                <RefreshCw className="w-5 h-5 mr-3 group-hover:rotate-180 transition-transform duration-500" />
                Lancer un scan global
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Grid de Recommandations */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Actions Suggérées</h3>
            <span className="bg-white/5 text-muted-foreground text-[10px] font-bold px-2 py-0.5 rounded-full">
              {recommendations.length} en attente
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className="grid md:grid-cols-3 gap-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-64 rounded-3xl bg-white/[0.02] border border-white/5 animate-pulse flex items-center justify-center">
                <Loader2 className="w-6 h-6 text-muted-foreground/20 animate-spin" />
              </div>
            ))}
          </div>
        ) : recommendations.length > 0 ? (
          <div className="grid md:grid-cols-3 gap-6 animate-in fade-in duration-700">
            {recommendations.map((reco) => (
              <RecommendationCard 
                key={reco.id} 
                reco={reco} 
                onApply={handleApply}
                onDismiss={handleDismiss}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 bg-white/[0.02] rounded-[3rem] border border-dashed border-white/5 text-center space-y-4">
            <div className="p-4 bg-white/5 rounded-full"><Target className="w-8 h-8 text-muted-foreground/20" /></div>
            <div>
              <p className="text-sm font-bold text-white uppercase">Aucune action urgente détectée</p>
              <p className="text-xs text-muted-foreground mt-1 max-w-xs mx-auto">Tout est sous contrôle. Relancez un scan pour rafraîchir l&apos;intelligence opérationnelle.</p>
            </div>
          </div>
        )}
      </div>

      {/* Guide des modules */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-700">
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col items-center gap-2 text-center">
          <Target className="w-4 h-4 text-green-500" />
          <span className="text-[9px] font-black uppercase tracking-widest text-white">Traction</span>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col items-center gap-2 text-center">
          <Zap className="w-4 h-4 text-klando-gold" />
          <span className="text-[9px] font-black uppercase tracking-widest text-white">Engagement</span>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col items-center gap-2 text-center">
          <TrendingUp className="w-4 h-4 text-blue-500" />
          <span className="text-[9px] font-black uppercase tracking-widest text-white">Stratégie</span>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl border border-white/5 flex flex-col items-center gap-2 text-center">
          <ShieldAlert className="w-4 h-4 text-red-500" />
          <span className="text-[9px] font-black uppercase tracking-widest text-white">Qualité</span>
        </div>
      </div>
    </div>
  );
}
