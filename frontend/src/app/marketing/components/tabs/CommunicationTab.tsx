"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Sparkles, Loader2, Megaphone, Music, Instagram, 
  Twitter, Send, Image as ImageIcon, History,
  PlusCircle, Target, ArrowRightCircle
} from "lucide-react";
import { MarketingComm, CommPlatform } from "../../types";
import { cn } from "@/lib/utils";

interface CommunicationTabProps {
  comms: MarketingComm[];
  isScanning: boolean;
  onGenerateIdeas: () => void;
  onGeneratePost: (platform: CommPlatform, topic: string) => void;
}

export function CommunicationTab({ 
  comms, 
  isScanning, 
  onGenerateIdeas, 
  onGeneratePost 
}: CommunicationTabProps) {
  const [topic, setTopic] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState<CommPlatform>("INSTAGRAM");

  const ideas = comms.filter(c => c.type === 'IDEA');
  const posts = comms.filter(c => c.type === 'POST');

  const platforms: { id: CommPlatform; label: string; icon: any; color: string }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music, color: 'text-pink-500' },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram, color: 'text-purple-500' },
    { id: 'X', label: 'X / Twitter', icon: Twitter, color: 'text-blue-400' },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      
      {/* 1. STRATEGIC IDEAS GRID */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-2">
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
            className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest gap-2"
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
                    onClick={() => setTopic(idea.title)}
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

      {/* 2. SOCIAL POST GENERATOR */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
            <div className="p-2 bg-blue-500/10 rounded-xl">
                <PlusCircle className="w-4 h-4 text-blue-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Générateur de Publications</h3>
        </div>

        <Card className="bg-slate-50 border-white/10 rounded-[2.5rem] overflow-hidden shadow-2xl">
            <div className="grid md:grid-cols-12 h-[450px]">
                {/* Selector */}
                <div className="md:col-span-4 border-r border-slate-200 p-8 space-y-8 bg-white">
                    <div className="space-y-4">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">1. Choisir la plateforme</label>
                        <div className="grid grid-cols-1 gap-2">
                            {platforms.map((p) => (
                                <button
                                    key={p.id}
                                    onClick={() => setSelectedPlatform(p.id)}
                                    className={cn(
                                        "flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-300",
                                        selectedPlatform === p.id 
                                            ? "bg-blue-50 border-blue-200 text-blue-700 shadow-sm" 
                                            : "border-transparent text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <p.icon className={cn("w-4 h-4", selectedPlatform === p.id ? "text-blue-600" : "opacity-40")} />
                                        <span className="text-[11px] font-black uppercase tracking-widest">{p.label}</span>
                                    </div>
                                    {selectedPlatform === p.id && <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">2. Thème de la pub</label>
                        <div className="relative">
                            <Input 
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="ex: Covoiturage pour le travail..."
                                className="bg-slate-50 border-slate-200 rounded-xl h-12 text-sm pl-4 pr-12 text-slate-900 outline-none focus:ring-2 focus:ring-blue-500/20 transition-all placeholder:text-slate-400"
                            />
                            <Target className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        </div>
                    </div>

                    <Button 
                        onClick={() => onGeneratePost(selectedPlatform, topic)}
                        disabled={!topic || isScanning}
                        className="w-full h-12 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-black uppercase text-[10px] tracking-widest gap-2 shadow-lg shadow-blue-500/20 transition-all active:scale-95"
                    >
                        {isScanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                        Générer le contenu
                    </Button>
                </div>

                {/* Post Display Area */}
                <div className="md:col-span-8 p-10 bg-black/20 flex flex-col items-center justify-center text-left">
                    {posts.length > 0 ? (
                        <div className="w-full max-w-xl space-y-6 animate-in slide-in-from-right-4 duration-700">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-blue-500/20 rounded-lg"><Send className="w-4 h-4 text-blue-400" /></div>
                                <h4 className="text-sm font-black text-white uppercase tracking-tight">{posts[0].title}</h4>
                            </div>
                            <div className="bg-white/5 border border-white/10 rounded-3xl p-8 shadow-2xl relative">
                                <div className="absolute -top-3 -left-3 bg-blue-600 text-white p-1.5 rounded-lg shadow-lg"><PlusCircle className="w-4 h-4" /></div>
                                <p className="text-sm text-white/90 leading-relaxed font-medium whitespace-pre-wrap">{posts[0].content}</p>
                                
                                {posts[0].hashtags && posts[0].hashtags.length > 0 && (
                                    <div className="mt-6 flex flex-wrap gap-2">
                                        {posts[0].hashtags.map((tag, i) => (
                                            <span key={i} className="text-[10px] font-black text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full">#{tag}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                            {posts[0].visual_suggestion && (
                                <div className="flex items-start gap-3 bg-white/5 p-4 rounded-2xl border border-white/5 border-l-4 border-l-klando-gold">
                                    <ImageIcon className="w-4 h-4 text-klando-gold shrink-0 mt-0.5" />
                                    <p className="text-[10px] text-muted-foreground/80 italic leading-relaxed"><strong>Idée Visuel :</strong> {posts[0].visual_suggestion}</p>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center space-y-4 opacity-20">
                            <Megaphone className="w-16 h-16 mx-auto text-white" />
                            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-white">Prêt à créer du contenu viral</p>
                        </div>
                    )}
                </div>
            </div>
        </Card>
      </div>

      {/* 3. HISTORY */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
            <div className="p-2 bg-white/5 rounded-xl">
                <History className="w-4 h-4 text-muted-foreground" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white/40">Historique des Générations</h3>
        </div>
        
        <div className="grid md:grid-cols-4 gap-4 opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-700 text-left">
            {posts.slice(1, 5).map((post) => (
                <Card key={post.id} className="bg-white/5 border-white/5 p-4">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="text-[8px] font-black text-blue-400 border border-blue-400/20 px-1.5 py-0.5 rounded uppercase">{post.platform}</span>
                        <span className="text-[8px] text-muted-foreground tabular-nums">{new Date(post.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-[10px] font-bold text-white uppercase truncate mb-1">{post.title}</p>
                    <p className="text-[9px] text-muted-foreground line-clamp-2 italic">&quot;{post.content}&quot;</p>
                </Card>
            ))}
        </div>
      </div>
    </div>
  );
}
