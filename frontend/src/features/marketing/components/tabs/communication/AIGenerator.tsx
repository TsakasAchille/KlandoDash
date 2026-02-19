"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sparkles, Loader2, Target, MapPin, Music, Instagram, Twitter
} from "lucide-react";
import { CommPlatform, MarketingComm } from "@/app/marketing/types";
import { cn } from "@/lib/utils";
import { IdeasGrid } from "./IdeasGrid";

interface AIGeneratorProps {
  selectedPlatform: CommPlatform;
  setSelectedPlatform: (p: CommPlatform) => void;
  topic: string;
  setTopic: (t: string) => void;
  onGenerate: () => void;
  onPromote: () => void;
  isScanning: boolean;
  ideas: MarketingComm[];
  onGenerateIdeas: () => void;
  onUseTheme: (theme: string) => void;
}

export function AIGenerator({
  selectedPlatform,
  setSelectedPlatform,
  topic,
  setTopic,
  onGenerate,
  onPromote,
  isScanning,
  ideas,
  onGenerateIdeas,
  onUseTheme
}: AIGeneratorProps) {
  const platforms: { id: CommPlatform; label: string; icon: React.ElementType }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram },
    { id: 'X', label: 'X / Twitter', icon: Twitter },
  ];

  return (
    <div className="flex flex-col gap-6 h-full animate-in fade-in duration-500 overflow-y-auto custom-scrollbar pr-2">
      {/* 1. IDEAS GRID (Inspirations) */}
      <div className="bg-white/50 backdrop-blur-sm border border-slate-200 rounded-[2.5rem] p-6 shadow-sm">
        <IdeasGrid 
            ideas={ideas}
            isScanning={isScanning}
            onGenerateIdeas={onGenerateIdeas}
            onUseTheme={onUseTheme}
        />
      </div>

      {/* 2. GENERATOR FORM */}
      <Card className="bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col shrink-0">
        <div className="p-8 flex flex-col items-center justify-center text-center space-y-6">
          <div className="w-14 h-14 bg-purple-600 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-200">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div className="space-y-1 max-w-md">
            <h4 className="text-lg font-black uppercase tracking-tight text-slate-900">Moteur de Création Libre</h4>
            <p className="text-[10px] font-medium text-slate-500 leading-relaxed italic px-4 text-center">Vous avez déjà une idée précise ? Saisissez-la ci-dessous et laissez l&apos;IA s&apos;occuper de la rédaction.</p>
          </div>

          <div className="w-full max-w-xl grid grid-cols-3 gap-3">
            {platforms.map(p => (
              <Button 
                key={p.id}
                variant="outline"
                onClick={() => setSelectedPlatform(p.id)}
                className={cn(
                  "h-16 flex flex-col gap-1 rounded-2xl border-2 transition-all",
                  selectedPlatform === p.id ? "bg-purple-50 border-purple-600 text-purple-700 shadow-inner" : "bg-white border-slate-100 text-slate-400 hover:border-purple-200 hover:bg-slate-50"
                )}
              >
                <p.icon className="w-4 h-4" />
                <span className="text-[8px] font-black uppercase">{p.label}</span>
              </Button>
            ))}
          </div>

          <div className="w-full max-w-xl space-y-3 pb-4">
            <div className="relative">
              <Target className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
              <Input 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Ex: Promo Tabaski, Nouveau trajet Dakar-Mbour..."
                className="h-14 pl-12 bg-slate-50 border-slate-200 rounded-2xl text-sm font-medium shadow-inner focus:ring-purple-500/20"
              />
            </div>
            <div className="flex gap-3">
              <Button 
                onClick={onGenerate}
                disabled={!topic || isScanning}
                className="flex-1 h-14 bg-purple-600 hover:bg-purple-700 text-white rounded-2xl gap-3 font-black uppercase text-[11px] shadow-lg shadow-purple-200"
              >
                {isScanning ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                Générer Publication
              </Button>
              <Button 
                onClick={onPromote}
                disabled={isScanning}
                variant="outline"
                title="Promouvoir les trajets en attente"
                className="h-14 px-6 rounded-2xl border-orange-200 bg-orange-50 text-orange-700 hover:bg-orange-100 gap-2 font-black uppercase text-[10px]"
              >
                <MapPin className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
