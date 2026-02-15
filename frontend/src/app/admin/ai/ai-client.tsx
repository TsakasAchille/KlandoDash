"use client";

import { useState, useRef, useEffect } from "react";
import { askGeminiAction } from "./actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Sparkles, Send, Bot, User, Loader2, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "ai";
  text: string;
}

export function KlandoAIClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
        setMessages((prev) => [...prev, { role: "ai", text: "Désolé, j'ai rencontré une erreur." }]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, { role: "ai", text: "Erreur de connexion avec l'IA." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] max-w-4xl mx-auto space-y-4">
      {/* Header Info */}
      <div className="bg-klando-gold/10 border border-klando-gold/20 p-4 rounded-2xl flex gap-3 items-start">
        <Info className="w-5 h-5 text-klando-gold mt-0.5 shrink-0" />
        <div className="text-xs text-klando-gold/80 leading-relaxed">
          <p className="font-bold uppercase tracking-widest mb-1 text-[10px]">Assistant Gemini 1.5 Flash</p>
          Je peux analyser tes statistiques, tes trajets récents et t&apos;aider à faire du matching avec les demandes du site vitrine.
        </div>
      </div>

      {/* Chat Zone */}
      <Card className="flex-1 overflow-hidden border-white/5 bg-card/30 backdrop-blur-sm flex flex-col rounded-3xl">
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-40">
              <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-klando-gold to-klando-burgundy flex items-center justify-center">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <div>
                <p className="text-sm font-black uppercase tracking-widest">Klando AI Ready</p>
                <p className="text-xs italic mt-1">Pose-moi une question sur ton activité...</p>
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
                "max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed",
                m.role === "ai" 
                  ? "bg-secondary/50 text-foreground border border-white/5" 
                  : "bg-klando-gold/10 text-klando-gold border border-klando-gold/20"
              )}>
                {m.text}
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
              placeholder="Ex: Fais-moi un résumé de l'activité cette semaine..."
              className="rounded-2xl bg-background/50 border-white/10 focus:ring-klando-gold"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="rounded-2xl bg-klando-burgundy hover:bg-klando-burgundy/90 text-white shadow-lg"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
