"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sparkles, RefreshCw, Loader2, Lightbulb, Clock, 
  ThumbsUp, MessageSquare, Save 
} from "lucide-react";
import { 
  generateGlobalStatsInsightAction, 
  getLatestGlobalInsightAction,
  saveInsightFeedbackAction 
} from "@/app/marketing/actions/intelligence";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function StatsAIAssistant() {
  const [insightId, setInsightId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Feedback state
  const [isLiked, setIsLiked] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [savedFeedback, setSavedFeedback] = useState("");
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);

  // Charger la dernière analyse au montage
  useEffect(() => {
    const fetchLatest = async () => {
      const res = await getLatestGlobalInsightAction();
      if (res.success && res.data) {
        setInsightId(res.data.id);
        setAnalysis(res.data.content);
        setLastUpdate(new Date(res.data.created_at).toLocaleString('fr-FR'));
        setIsLiked(res.data.is_liked || false);
        setFeedback(res.data.admin_feedback || "");
        setSavedFeedback(res.data.admin_feedback || "");
      }
    };
    fetchLatest();
  }, []);

  const handleGenerate = async () => {
    setIsLoading(true);
    try {
      const res = await generateGlobalStatsInsightAction();
      if (res.success && res.analysis) {
        setAnalysis(res.analysis);
        setLastUpdate(new Date().toLocaleString('fr-FR'));
        // Re-fetch to get the new ID
        const latest = await getLatestGlobalInsightAction();
        if (latest.success && latest.data) {
          setInsightId(latest.data.id);
          setIsLiked(false);
          setFeedback("");
          setSavedFeedback("");
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveFeedback = async () => {
    if (!insightId) return;
    setIsSavingFeedback(true);
    const res = await saveInsightFeedbackAction(insightId, isLiked, feedback);
    if (res.success) {
      toast.success("Feedback stratégique enregistré.");
      setSavedFeedback(feedback);
    }
    setIsSavingFeedback(false);
  };

  const toggleLike = async () => {
    if (!insightId) return;
    const newLike = !isLiked;
    setIsLiked(newLike);
    await saveInsightFeedbackAction(insightId, newLike, feedback);
  };

  return (
    <Card className="rounded-2xl border-none shadow-sm bg-purple-50/50 border border-purple-100 overflow-hidden relative">
      <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
        <Sparkles className="w-24 h-24 text-purple-500" />
      </div>
      
      <CardHeader className="flex flex-row items-center justify-between border-b border-purple-100/50 pb-4">
        <div className="space-y-1">
          <CardTitle className="flex items-center gap-3 text-sm font-black uppercase tracking-[0.2em] text-purple-600">
            <Lightbulb className="w-5 h-5" />
            Assistant IA Stratégique
          </CardTitle>
          {lastUpdate && !isLoading && (
            <div className="flex items-center gap-1.5 text-[9px] font-bold text-purple-400 uppercase tracking-wider ml-8">
              <Clock className="w-3 h-3" />
              Dernier rapport : {lastUpdate}
            </div>
          )}
        </div>
        <Button 
          onClick={handleGenerate} 
          disabled={isLoading}
          size="sm"
          className="bg-purple-600 hover:bg-purple-700 text-white rounded-xl px-4 h-9 font-bold text-[10px] uppercase tracking-widest gap-2 shadow-lg shadow-purple-500/20"
        >
          {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
          {analysis ? "Relancer l'analyse" : "Générer une analyse"}
        </Button>
      </CardHeader>

      <CardContent className="p-0">
        <div className="p-6">
          {!analysis && !isLoading ? (
            <div className="py-10 text-center space-y-4">
              <p className="text-sm text-purple-900/60 font-medium italic">
                &quot;Cliquez sur le bouton pour que j&apos;analyse vos chiffres en temps réel.&quot;
              </p>
            </div>
          ) : isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-4">
              <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
              <p className="text-[10px] font-black uppercase tracking-widest text-purple-600 animate-pulse">Calcul de la stratégie en cours...</p>
            </div>
          ) : (
            <div className="prose prose-sm max-w-none animate-in fade-in slide-in-from-bottom-4 duration-500 text-slate-800">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {analysis}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* FEEDBACK BAR */}
        {analysis && !isLoading && (
          <div className="px-6 py-4 bg-white/50 border-t border-purple-100 flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button 
                  onClick={toggleLike}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-xl border transition-all font-black text-[10px] uppercase tracking-widest",
                    isLiked ? "bg-green-100 border-green-200 text-green-700" : "bg-white border-slate-200 text-slate-500 hover:border-slate-300"
                  )}
                >
                  <ThumbsUp className={cn("w-3.5 h-3.5", isLiked && "fill-green-700")} />
                  {isLiked ? "Analyse utile" : "Liker"}
                </button>
                <div className="flex items-center gap-2 text-slate-400">
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span className="text-[10px] font-bold uppercase tracking-widest">Feedback Stratégique</span>
                </div>
              </div>
              {feedback !== savedFeedback && (
                <Button onClick={handleSaveFeedback} disabled={isSavingFeedback} size="sm" className="h-8 bg-slate-900 text-white rounded-xl text-[10px] font-bold uppercase">
                  {isSavingFeedback ? <Loader2 className="w-3 h-3 animate-spin mr-2" /> : <Save className="w-3 h-3 mr-2" />}
                  Enregistrer
                </Button>
              )}
            </div>
            <Input 
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Ex: 'Insiste plus sur les trajets Dakar-Thiès'..."
              className="bg-white border-slate-200 text-xs h-10 rounded-xl focus:ring-purple-500/20"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
