"use client";

import { useState, useRef, useEffect } from "react";
import { askGeminiAction, getAIInsightsAction } from "./actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Bot, User, Loader2, Info, TrendingUp, Zap, Target, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { toast } from "sonner";

interface Message {
  role: "user" | "ai";
  text: string;
}

interface Insight {
  title: string;
  description: string;
  impact: "High" | "Medium";
  type: "matching" | "growth" | "security";
}

export function KlandoAIClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadInsights = async () => {
    setLoadingInsights(true);
    try {
      const res = await getAIInsightsAction();
      if (res.success) {
        setInsights(res.insights);
      } else {
        toast.error("Impossible de générer les insights");
      }
    } catch {
      console.error("Failed to load insights");
      toast.error("Erreur de connexion avec l'IA");
    } finally {
      setLoadingInsights(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
    setIsLoading(true);

    try {
      const result = await askGeminiAction(userMessage);
      if (result.success && result.text) {
        setMessages((prev) => [...prev, { role: "ai", text: result.text! }]);
      } else {
        setMessages((prev) => [...prev, { role: "ai", text: `Erreur: ${result.message || "Désolé, j'ai rencontré une erreur."}` }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: "ai", text: "Erreur de connexion avec l'IA." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Section Insights IA */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-2">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground flex items-center gap-2">
            <Zap className="w-3 h-3 text-klando-gold" />
            Recommandations Stratégiques
          </h3>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={loadInsights}
            disabled={loadingInsights}
            className="h-8 rounded-full border-klando-gold/30 hover:border-klando-gold bg-klando-gold/5 text-klando-gold text-[9px] font-black uppercase tracking-widest px-4"
          >
            {loadingInsights ? <Loader2 className="w-3 h-3 animate-spin mr-2" /> : <RefreshCw className="w-3 h-3 mr-2" />}
            {insights.length > 0 ? "Actualiser l'analyse" : "Générer les opportunités"}
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {loadingInsights ? (
            [...Array(3)].map((_, i) => (
              <Card key={i} className="bg-card/30 border-white/5 animate-pulse">
                <CardContent className="p-6 h-32 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-muted-foreground animate-spin" />
                </CardContent>
              </Card>
            ))
          ) : insights.length > 0 ? (
            insights.map((insight, i) => (
              <Card key={i} className="bg-card/40 backdrop-blur-md border-white/5 hover:border-klando-gold/30 transition-all duration-500 group relative overflow-hidden">
                <div className={cn(
                  "absolute top-0 right-0 p-2 opacity-10 group-hover:scale-150 transition-transform duration-700",
                  insight.type === "matching" ? "text-green-500" : insight.type === "growth" ? "text-blue-500" : "text-klando-gold"
                )}>
                  {insight.type === "matching" ? <Target className="w-12 h-12" /> : insight.type === "growth" ? <TrendingUp className="w-12 h-12" /> : <Zap className="w-12 h-12" />}
                </div>
                <CardContent className="p-5 space-y-3 relative z-10">
                  <div className="flex justify-between items-start">
                    <span className={cn(
                      "text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border",
                      insight.impact === "High" ? "bg-red-500/10 text-red-500 border-red-500/20" : "bg-blue-500/10 text-blue-500 border-blue-500/20"
                    )}>
                      {insight.impact} Impact
                    </span>
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-white uppercase tracking-tight group-hover:text-klando-gold transition-colors">{insight.title}</h4>
                    <p className="text-[11px] text-muted-foreground leading-relaxed mt-1">{insight.description}</p>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="md:col-span-3 h-24 flex items-center justify-center rounded-2xl border border-dashed border-white/5 bg-white/[0.02]">
              <p className="text-xs text-muted-foreground italic">Clique sur le bouton pour lancer l&apos;analyse IA de tes données</p>
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-col h-[600px] space-y-4">
        {/* Header Info */}
        <div className="bg-klando-gold/10 border border-klando-gold/20 p-4 rounded-2xl flex gap-3 items-start">
          <Info className="w-5 h-5 text-klando-gold mt-0.5 shrink-0" />
          <div className="text-xs text-klando-gold/80 leading-relaxed">
            <p className="font-bold uppercase tracking-widest mb-1 text-[10px]">Assistant Gemini 2.0 Flash</p>
            Analyse complète de ton activité en cours. Pose-moi une question sur les chiffres ou les actions à mener.
          </div>
        </div>

        {/* Chat Zone */}
        <Card className="flex-1 overflow-hidden border-white/5 bg-card/30 backdrop-blur-sm flex flex-col rounded-3xl shadow-xl">
          <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
                <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-klando-gold to-klando-burgundy flex items-center justify-center">
                  <Bot className="w-8 h-8 text-white" />
                </div>
                <div>
                  <p className="text-sm font-black uppercase tracking-widest">Chat AI Ready</p>
                  <p className="text-xs italic mt-1">Comment puis-je t&apos;aider aujourd&apos;hui ?</p>
                </div>
              </div>
            )}

            {messages.map((m, i) => (
              <div
                key={i}
                className={cn(
                  "flex items-start gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300",
                  m.role === "user" ? "flex-row-reverse" : "flex-row"
                )}
              >
                <div className={cn(
                  "w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-sm",
                  m.role === "ai" ? "bg-klando-burgundy text-white" : "bg-klando-gold text-black"
                )}>
                  {m.role === "ai" ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                </div>
                <div className={cn(
                  "max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed",
                  m.role === "ai" 
                    ? "bg-secondary/50 text-foreground border border-white/5" 
                    : "bg-klando-gold/10 text-klando-gold border border-klando-gold/20"
                )}>
                  {m.role === "ai" ? (
                    <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-li:my-1 prose-strong:text-klando-gold">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {m.text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    m.text
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex items-center gap-3 text-muted-foreground animate-pulse">
                <div className="w-8 h-8 rounded-xl bg-secondary flex items-center justify-center">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
                <span className="text-xs font-medium uppercase tracking-widest">L&apos;IA réfléchit...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </CardContent>

          {/* Input Zone */}
          <div className="p-4 bg-muted/20 border-t border-white/5">
            <form onSubmit={handleSend} className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ex: Qui contacter pour un trajet Dakar-Mbour ?"
                className="rounded-2xl bg-background/50 border-white/10 focus:ring-klando-gold h-12"
                disabled={isLoading}
              />
              <Button 
                type="submit" 
                disabled={isLoading || !input.trim()}
                className="rounded-2xl bg-klando-burgundy hover:bg-klando-burgundy/90 text-white shadow-lg h-12 w-12 flex items-center justify-center shrink-0"
              >
                <Send className="w-5 h-5" />
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
}
