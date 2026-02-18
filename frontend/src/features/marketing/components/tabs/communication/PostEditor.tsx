"use client";

import { useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Edit3, Wand2, Loader2, X, Save, ImagePlus
} from "lucide-react";
import { MarketingComm, CommPlatform } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

interface PostEditorProps {
  createMode: 'TEXT' | 'IMAGE' | null;
  editForm: Partial<MarketingComm>;
  setEditForm: (val: Partial<MarketingComm>) => void;
  onClose: () => void;
  onSave: () => void;
  onRefine: () => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isUpdating: boolean;
  isRefining: boolean;
  isUploading: boolean;
}

export function PostEditor({
  createMode,
  editForm,
  setEditForm,
  onClose,
  onSave,
  onRefine,
  onFileUpload,
  isUpdating,
  isRefining,
  isUploading
}: PostEditorProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const platforms: { id: CommPlatform; label: string }[] = [
    { id: 'TIKTOK', label: 'TikTok' },
    { id: 'INSTAGRAM', label: 'Instagram' },
    { id: 'X', label: 'X / Twitter' },
  ];

  return (
    <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col h-full text-left">
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600 rounded-xl text-white shadow-lg shadow-purple-200">
            <Edit3 className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">Éditeur : {createMode === 'IMAGE' ? 'Post Visuel' : 'Post Standard'}</h4>
            <p className="text-[10px] font-bold text-purple-600 uppercase tracking-widest">Rédaction en cours</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-slate-100">
          <X className="w-5 h-5" />
        </Button>
      </div>

      <div className="flex-1 p-8 overflow-y-auto custom-scrollbar space-y-6">
        <div className="grid grid-cols-12 gap-6 h-full">
          <div className={cn("space-y-4", createMode === 'IMAGE' ? "col-span-4" : "col-span-8")}>
            <div className="space-y-1.5">
              <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Titre du post</label>
              <Input 
                value={editForm.title || ""} 
                onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                className="h-12 bg-slate-50 border-slate-200 font-black uppercase text-sm rounded-xl focus:ring-purple-500/20"
                placeholder={createMode === 'IMAGE' ? "Nom de l'affiche..." : "Ex: PROMO WEEKEND DAKAR"}
              />
            </div>
            
            {createMode !== 'IMAGE' && (
              <div className="space-y-1.5 relative animate-in fade-in slide-in-from-top-2">
                <div className="flex justify-between items-center mb-1">
                  <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Texte / Légende</label>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={onRefine}
                    disabled={isRefining || !editForm.content}
                    className="h-6 text-[8px] font-black uppercase text-purple-600 bg-purple-50 hover:bg-purple-100 rounded-full gap-1"
                  >
                    {isRefining ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
                    Magic Fix IA
                  </Button>
                </div>
                <Textarea 
                  value={editForm.content || ""} 
                  onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                  className="min-h-[350px] bg-slate-50 border-slate-200 leading-relaxed text-sm p-6 rounded-2xl resize-none"
                  placeholder="Écrivez votre message ici..."
                />
              </div>
            )}

            {createMode === 'IMAGE' && (
              <div className="p-10 bg-purple-50/30 border border-dashed border-purple-200 rounded-3xl text-center space-y-3 animate-in zoom-in-95">
                <ImagePlus className="w-10 h-10 text-purple-300 mx-auto" />
                <p className="text-[10px] font-black uppercase text-purple-600">Mode Visuel Activé</p>
                <p className="text-[9px] text-slate-400 font-medium">Dans ce mode, seul le titre et l&apos;image sont conservés.</p>
              </div>
            )}
          </div>

          <div className={cn("space-y-6", createMode === 'IMAGE' ? "col-span-8" : "col-span-4")}>
            <div className="space-y-3">
              <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Plateforme</label>
              <div className={cn("grid gap-2", createMode === 'IMAGE' ? "grid-cols-3" : "grid-cols-1")}>
                {platforms.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setEditForm({...editForm, platform: p.id})}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-xl border transition-all",
                      editForm.platform === p.id 
                        ? "bg-slate-900 border-slate-900 text-white shadow-md" 
                        : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
                    )}
                  >
                    <span className="text-[10px] font-black uppercase">{p.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className={cn(
              "p-6 bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 space-y-4 text-center transition-all",
              createMode === 'IMAGE' ? "aspect-video bg-purple-50/20 border-purple-200" : "aspect-square"
            )}>
              <label className="text-[10px] font-black uppercase text-purple-600">Fichier PNG / Image Star</label>
              {editForm.image_url ? (
                <div className="relative h-full w-full rounded-2xl overflow-hidden shadow-lg group bg-slate-900">
                  <img src={editForm.image_url} alt="Preview" className="w-full h-full object-contain" />
                  <button 
                    onClick={() => setEditForm({...editForm, image_url: null})}
                    className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="h-full w-full bg-white border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center gap-3 cursor-pointer hover:bg-slate-100 hover:border-purple-300 transition-all group"
                >
                  {isUploading ? <Loader2 className="w-10 h-10 text-purple-600 animate-spin" /> : <ImagePlus className="w-10 h-10 text-slate-300 group-hover:text-purple-400 transition-colors" />}
                  <div className="space-y-1">
                    <p className="text-[10px] font-black uppercase text-slate-900">Sélectionner l&apos;image</p>
                    <p className="text-[8px] font-bold text-slate-400 uppercase tracking-widest italic">PNG ou JPG recommandé</p>
                  </div>
                </div>
              )}
              <input type="file" ref={fileInputRef} onChange={onFileUpload} className="hidden" accept="image/*,application/pdf" />
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 border-t border-slate-100 bg-white">
        <Button 
          onClick={onSave} 
          disabled={isUpdating || (createMode === 'IMAGE' && !editForm.image_url)} 
          className="w-full h-12 bg-green-600 hover:bg-green-700 text-white rounded-2xl gap-2 font-black uppercase text-[11px] shadow-lg shadow-green-100"
        >
          {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {createMode === 'IMAGE' && !editForm.image_url ? "Attachez une image d'abord" : "Enregistrer le Brouillon"}
        </Button>
      </div>
    </Card>
  );
}
