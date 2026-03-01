"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Plus, Loader2, Type } from "lucide-react";
import { CommPlatform } from "@/app/marketing/types";
import { createMarketingCommAction } from "@/app/marketing/actions/communication";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface PostComposeProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (postId: string) => void;
}

export function PostCompose({ isOpen, onOpenChange, onCreated }: PostComposeProps) {
  const [title, setTitle] = useState("");
  const [platform, setPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [isSaving, setIsSaving] = useState(false);

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
        onOpenChange(false);
        onCreated(res.post.id);
        setTitle("");
        setPlatform("INSTAGRAM");
      }
    } catch {
      toast.error("Erreur de création");
    } finally {
      setIsSaving(false);
    }
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
              Créer un brouillon de publication
            </DialogDescription>
          </DialogHeader>

          <div className="p-8 space-y-6 bg-white text-left">
            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1 flex items-center gap-2">
                <Type className="w-3 h-3 text-purple-600" /> Titre de référence
              </label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex: Promo Tabaski, Lancement Mbour..."
                className="bg-slate-50 border-slate-300 rounded-xl text-slate-900 h-11 placeholder:text-slate-400 focus:border-purple-500/50 transition-all outline-none text-left"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-black text-slate-700 uppercase pl-1">Plateforme cible</label>
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
          </div>

          <DialogFooter className="p-6 bg-slate-50 border-t border-slate-200 gap-3">
            <Button variant="ghost" onClick={() => onOpenChange(false)} className="rounded-xl text-slate-600 font-black text-[10px] uppercase hover:bg-slate-200 transition-colors">Annuler</Button>
            <Button
              onClick={handleCreate}
              disabled={isSaving}
              className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest px-8 h-11 shadow-lg shadow-purple-500/20 transition-all active:scale-95"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <Plus className="w-4 h-4 text-white" />}
              Créer le brouillon
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
}
