"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Plus, Loader2, Type, Sparkles, Target } from "lucide-react";
import { CommPlatform } from "@/app/marketing/types";
import { createMarketingCommAction, generateSocialPostAction } from "@/app/marketing/actions/communication";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface PostComposeProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (postId: string) => void;
}

export function PostCompose({ isOpen, onOpenChange, onCreated }: PostComposeProps) {
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const platforms: { id: CommPlatform; label: string }[] = [
    { id: 'TIKTOK', label: 'TikTok' },
    { id: 'INSTAGRAM', label: 'Instagram' },
    { id: 'LINKEDIN', label: 'LinkedIn' },
    { id: 'X', label: 'X / Twitter' },
    { id: 'OTHER', label: 'Autre' },
  ];

  const handleCreate = async () => {
    setIsSaving(true);
    try {
      const res = await createMarketingCommAction({
        title: title || "Nouvelle publication",
        content: "",
        hashtags: [],
        visual_suggestion: "",
        platform,
        image_url: null,
        status: 'DRAFT'
      });
      if (res.success && res.post) {
        toast.success("Publication créée !");
        resetAndClose(res.post.id);
      }
    } catch {
      toast.error("Erreur de création");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAIGenerate = async () => {
    if (!topic.trim()) {
      toast.error("Veuillez saisir un sujet pour l'IA");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await generateSocialPostAction(platform, topic);
      if (res.success && res.post) {
        toast.success(`Post ${platform} généré avec succès !`);
        resetAndClose(res.post.id);
      } else {
        toast.error("L'IA n'a pas pu générer le post");
      }
    } catch (error) {
      toast.error("Erreur technique lors de la génération");
    } finally {
      setIsGenerating(false);
    }
  };

  const resetAndClose = (id: string) => {
    onOpenChange(false);
    onCreated(id);
    setTitle("");
    setTopic("");
    setPlatform("INSTAGRAM");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-slate-50 border-slate-300 rounded-[2.5rem] p-0 overflow-hidden outline-none shadow-2xl">
        <div className="flex flex-col">
          <DialogHeader className="p-8 pb-6 bg-white border-b border-slate-200 text-left">
            <DialogTitle className="text-xl font-black text-slate-900 uppercase tracking-tight flex items-center gap-3 text-left">
              <Plus className="w-5 h-5 text-purple-600" /> Nouveau Post
            </DialogTitle>
            <DialogDescription className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mt-1 text-left">
              Choisissez entre création manuelle ou assistée par IA
            </DialogDescription>
          </DialogHeader>

          <div className="p-8 space-y-8 bg-white text-left">
            {/* PLATFORM SELECTOR */}
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1 tracking-widest">1. Plateforme cible</label>
              <div className="flex flex-wrap gap-2">
                {platforms.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPlatform(p.id)}
                    className={cn(
                      "flex-1 min-w-[80px] flex items-center justify-center py-2.5 rounded-xl border transition-all text-[9px] font-black uppercase tracking-tighter",
                      platform === p.id
                        ? "bg-slate-900 border-slate-900 text-white shadow-md"
                        : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
                    )}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* CHOICE 1: IA GENERATION */}
            <div className="p-5 bg-purple-50 rounded-2xl border border-purple-100 space-y-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <span className="text-[10px] font-black text-purple-700 uppercase tracking-widest">Générer avec l'IA</span>
              </div>
              <div className="space-y-2">
                <div className="relative">
                  <Target className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-purple-400" />
                  <Input
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="Sujet (ex: Promo weekend, Tips carpool...)"
                    className="bg-white border-purple-200 rounded-xl text-slate-900 h-11 pl-10 text-sm focus:ring-purple-500/20"
                  />
                </div>
                <Button
                  onClick={handleAIGenerate}
                  disabled={isGenerating || isSaving || !topic.trim()}
                  className="w-full h-11 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest gap-2 shadow-lg shadow-purple-500/20"
                >
                  {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  Générer le post complet
                </Button>
              </div>
            </div>

            {/* DIVIDER */}
            <div className="relative flex items-center py-2">
                <div className="flex-grow border-t border-slate-100"></div>
                <span className="flex-shrink mx-4 text-[9px] font-black text-slate-300 uppercase tracking-widest">OU</span>
                <div className="flex-grow border-t border-slate-100"></div>
            </div>

            {/* CHOICE 2: MANUAL CREATION */}
            <div className="space-y-3">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1 tracking-widest flex items-center gap-2">
                <Type className="w-3 h-3 text-slate-400" /> Création manuelle (Titre)
              </label>
              <div className="flex gap-2">
                <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Titre interne..."
                    className="bg-slate-50 border-slate-300 rounded-xl text-slate-900 h-11 flex-1 text-sm outline-none"
                />
                <Button
                    onClick={handleCreate}
                    variant="outline"
                    disabled={isGenerating || isSaving}
                    className="h-11 rounded-xl border-slate-200 font-black text-[10px] uppercase tracking-widest px-6"
                >
                    {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : "Créer vide"}
                </Button>
              </div>
            </div>
          </div>

          <DialogFooter className="p-6 bg-slate-50 border-t border-slate-200">
            <Button variant="ghost" onClick={() => onOpenChange(false)} className="w-full rounded-xl text-slate-500 font-black text-[10px] uppercase hover:bg-slate-200">Annuler</Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
}
