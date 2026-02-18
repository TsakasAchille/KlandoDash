"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sparkles, Loader2, Target, MapPin, Music, Instagram, Twitter
} from "lucide-react";
import { CommPlatform } from "../../../types";
import { cn } from "@/lib/utils";

interface AIGeneratorProps {
  selectedPlatform: CommPlatform;
  setSelectedPlatform: (p: CommPlatform) => void;
  topic: string;
  setTopic: (t: string) => void;
  onGenerate: () => void;
  onPromote: () => void;
  isScanning: boolean;
}

export function AIGenerator({
  selectedPlatform,
  setSelectedPlatform,
  topic,
  setTopic,
  onGenerate,
  onPromote,
  isScanning
}: AIGeneratorProps) {
  const platforms: { id: CommPlatform; label: string; icon: any }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram },
    { id: 'X', label: 'X / Twitter', icon: Twitter },
  ];

  return (
    <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col animate-in fade-in duration-500">
      <div className="p-10 flex flex-col items-center justify-center text-center space-y-8 flex-1">
        <div className="w-20 h-20 bg-purple-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-purple-200 animate-bounce duration-[2000ms]">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <div className="space-y-2 max-w-md">
          <h4 className="text-2xl font-black uppercase tracking-tight text-slate-900">Générateur de Posts IA</h4>
          <p className="text-sm font-medium text-slate-500 leading-relaxed italic">Sélectionnez un post à gauche ou utilisez le moteur IA ci-dessous pour créer du contenu viral.</p>
        </div>

        <div className="w-full max-w-xl grid grid-cols-3 gap-4 pt-4">
          {platforms.map(p => (
            <Button 
              key={p.id}
              variant="outline"
              onClick={() => setSelectedPlatform(p.id)}
              className={cn(
                "h-24 flex flex-col gap-2 rounded-2xl border-2 transition-all",
                selectedPlatform === p.id ? "bg-purple-50 border-purple-600 text-purple-700 shadow-inner" : "bg-white border-slate-100 text-slate-400 hover:border-purple-200 hover:bg-slate-50"
              )}
            >
              <p.icon className="w-6 h-6" />
              <span className="text-[10px] font-black uppercase">{p.label}</span>
            </Button>
          ))}
        </div>

        <div className="w-full max-w-xl space-y-4 pt-4">
          <div className="relative">
            <Target className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
            <Input 
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Quel est le thème de votre post ?"
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
              Générer via IA
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
  );
}
