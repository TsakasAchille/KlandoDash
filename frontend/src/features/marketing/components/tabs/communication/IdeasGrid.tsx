"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Megaphone, Loader2, Sparkles, ImageIcon, ArrowRightCircle
} from "lucide-react";
import { MarketingComm } from "@/app/marketing/types";

interface IdeasGridProps {
  ideas: MarketingComm[];
  isScanning: boolean;
  onGenerateIdeas: () => void;
  onUseTheme: (topic: string) => void;
}

export function IdeasGrid({ 
  ideas, 
  isScanning, 
  onGenerateIdeas, 
  onUseTheme 
}: IdeasGridProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between px-2 text-left">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-xl">
            <Megaphone className="w-4 h-4 text-purple-500" />
          </div>
          <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Angles de Communication ✨</h3>
        </div>
        <Button 
          onClick={onGenerateIdeas} 
          disabled={isScanning}
          size="sm"
          className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest gap-2 shadow-lg shadow-purple-500/20"
        >
          {isScanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          Nouveaux Angles
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-6 text-left">
        {ideas.length > 0 ? (
          ideas.slice(0, 3).map((idea) => (
            <Card key={idea.id} className="bg-card/40 backdrop-blur-md border-white/5 hover:border-purple-500/30 transition-all duration-500 group overflow-hidden">
              <CardContent className="p-6 space-y-4">
                <h4 className="font-black text-sm text-white uppercase group-hover:text-purple-400 transition-colors">{idea.title}</h4>
                <p className="text-[11px] text-muted-foreground leading-relaxed">{idea.content}</p>
                {idea.visual_suggestion && (
                  <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                      <p className="text-[9px] font-black uppercase text-purple-400 mb-1 flex items-center gap-1.5"><ImageIcon className="w-2.5 h-2.5" /> Idée Visuelle</p>
                      <p className="text-[10px] text-muted-foreground/80 italic">&quot;{idea.visual_suggestion}&quot;</p>
                  </div>
                )}
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => onUseTheme(idea.title)}
                  className="w-full rounded-xl hover:bg-white/5 text-[10px] font-black uppercase tracking-tighter gap-2"
                >
                  Utiliser ce thème <ArrowRightCircle className="w-3 h-3" />
                </Button>
              </CardContent>
            </Card>
          ))
        ) : (
          <div className="col-span-3 py-12 bg-white/[0.02] border border-dashed border-white/5 rounded-[2rem] flex flex-col items-center justify-center opacity-30 italic text-[10px] font-black uppercase tracking-[0.2em]">
              Aucune idée générée. Cliquez sur le scan.
          </div>
        )}
      </div>
    </div>
  );
}
