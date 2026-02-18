"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { MarketingComm, CommPlatform } from "@/app/marketing/types";
import { 
  Music, Instagram, Twitter, 
  Sparkles, Loader2, Send,
  Layout
} from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { generateSocialPostAction, updateMarketingCommAction } from "@/app/marketing/actions/communication";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface PlanPostModalProps {
  date: Date | null;
  isOpen: boolean;
  onClose: () => void;
  drafts: MarketingComm[];
}

export function PlanPostModal({ date, isOpen, onClose, drafts }: PlanPostModalProps) {
  const [mode, setMode] = useState<'NEW' | 'DRAFT'>('NEW');
  const [topic, setTopic] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [loading, setLoading] = useState(false);

  const platforms: { id: CommPlatform; label: string; icon: any }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram },
    { id: 'X', label: 'X / Twitter', icon: Twitter },
  ];

  const handleGenerateAndPlan = async () => {
    if (!topic || !date) return;
    setLoading(true);
    
    const res = await generateSocialPostAction(selectedPlatform, topic);
    
    if (res.success && res.post) {
      const updateRes = await updateMarketingCommAction(res.post.id, {
        scheduled_at: date.toISOString(),
        status: 'DRAFT'
      });
      
      if (updateRes.success) {
        toast.success("Publication générée et planifiée !");
        onClose();
      }
    } else {
      toast.error("Échec de la génération.");
    }
    setLoading(false);
  };

  const handlePlanDraft = async (draftId: string) => {
    if (!date) return;
    setLoading(true);
    const res = await updateMarketingCommAction(draftId, {
      scheduled_at: date.toISOString()
    });
    
    if (res.success) {
      toast.success("Brouillon planifié !");
      onClose();
    } else {
      toast.error("Échec de la planification.");
    }
    setLoading(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md p-0 overflow-hidden bg-white border-none rounded-[2.5rem] shadow-2xl">
        <DialogHeader className="sr-only">
          <DialogTitle>
            Planifier un post pour le {date ? format(date, 'dd MMMM yyyy', { locale: fr }) : ''}
          </DialogTitle>
          <DialogDescription>
            Interface de planification de contenu marketing.
          </DialogDescription>
        </DialogHeader>

        {date ? (
          <div className="p-8 space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-black uppercase tracking-tight text-slate-900 leading-tight">
                Planifier pour le {format(date, 'dd MMMM', { locale: fr })}
              </h2>
              <p className="text-[10px] font-black uppercase tracking-widest text-purple-600">Editorial Cockpit</p>
            </div>

            <div className="flex bg-slate-100 p-1 rounded-xl">
              <button 
                  onClick={() => setMode('NEW')}
                  className={cn(
                      "flex-1 py-2 text-[9px] font-black uppercase rounded-lg transition-all",
                      mode === 'NEW' ? "bg-white text-slate-900 shadow-sm" : "text-slate-400"
                  )}
              >
                  Générer via IA
              </button>
              <button 
                  onClick={() => setMode('DRAFT')}
                  className={cn(
                      "flex-1 py-2 text-[9px] font-black uppercase rounded-lg transition-all",
                      mode === 'DRAFT' ? "bg-white text-slate-900 shadow-sm" : "text-slate-400"
                  )}
              >
                  Nouveau ou Brouillon
              </button>
            </div>

            {mode === 'NEW' ? (
              <div className="space-y-4 animate-in fade-in duration-300">
                  <div className="grid grid-cols-3 gap-2">
                      {platforms.map((p) => (
                          <button
                              key={p.id}
                              onClick={() => setSelectedPlatform(p.id)}
                              className={cn(
                                  "flex flex-col items-center gap-2 p-3 rounded-xl border transition-all",
                                  selectedPlatform === p.id 
                                      ? "bg-purple-50 border-purple-200 text-purple-700" 
                                      : "border-slate-100 text-slate-400 hover:bg-slate-50"
                              )}
                          >
                              <p.icon className="w-4 h-4" />
                              <span className="text-[8px] font-black uppercase">{p.label}</span>
                          </button>
                      ))}
                  </div>
                  <div className="space-y-2">
                      <label className="text-[9px] font-black uppercase tracking-widest text-slate-400 pl-1">Thème de la publication</label>
                      <Textarea 
                          placeholder="ex: Promotion des trajets vers Dakar ce weekend..."
                          value={topic}
                          onChange={(e) => setTopic(e.target.value)}
                          className="min-h-[100px] bg-slate-50 border-none rounded-2xl text-xs font-medium focus:ring-2 focus:ring-purple-400"
                      />
                  </div>
                  <Button 
                      onClick={handleGenerateAndPlan}
                      disabled={!topic || loading}
                      className="w-full h-12 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[10px] tracking-widest gap-2"
                  >
                      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                      Générer et Planifier
                  </Button>
              </div>
            ) : (
              <div className="space-y-4 animate-in fade-in duration-300 max-h-[300px] overflow-y-auto custom-scrollbar pr-2 text-left">
                  {drafts.length > 0 ? (
                      drafts.map((d) => (
                          <div 
                              key={d.id} 
                              onClick={() => handlePlanDraft(d.id)}
                              className="p-4 bg-slate-50 border border-slate-100 rounded-2xl hover:border-purple-400 cursor-pointer group transition-all"
                          >
                              <div className="flex justify-between items-start mb-2">
                                  <span className="text-[8px] font-black uppercase text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-100">{d.platform}</span>
                                  <Send className="w-3 h-3 text-slate-300 group-hover:text-purple-600" />
                              </div>
                              <p className="text-[10px] font-black text-slate-900 uppercase truncate">{d.title}</p>
                              <p className="text-[9px] text-slate-500 line-clamp-1 italic mt-1">{d.content}</p>
                          </div>
                      ))
                  ) : (
                      <div className="py-12 text-center text-slate-300 italic flex flex-col items-center gap-2">
                          <Layout className="w-8 h-8 opacity-20" />
                          <p className="text-[9px] font-black uppercase tracking-widest">Aucun brouillon dispo</p>
                      </div>
                  )}
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400">
            Veuillez sélectionner une date.
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
