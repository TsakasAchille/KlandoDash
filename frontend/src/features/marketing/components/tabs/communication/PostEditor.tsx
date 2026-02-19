"use client";

import { useRef, useState } from "react";
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
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement> | File) => void;
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
  const [isDragging, setIsDragging] = useState(false);

  const platforms: { id: CommPlatform; label: string }[] = [
    { id: 'TIKTOK', label: 'TikTok' },
    { id: 'INSTAGRAM', label: 'Instagram' },
    { id: 'X', label: 'X / Twitter' },
  ];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  const isVisualMode = createMode === 'IMAGE';

  return (
    <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col text-left">
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600 rounded-xl text-white shadow-lg shadow-purple-200">
            {isVisualMode ? <ImagePlus className="w-5 h-5" /> : <Edit3 className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">{isVisualMode ? 'Créer un Post Visuel' : 'Éditeur de Post Standard'}</h4>
            <p className="text-[10px] font-bold text-purple-600 uppercase tracking-widest">Production de contenu</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-slate-100">
          <X className="w-5 h-5" />
        </Button>
      </div>

      <div className="p-8 md:p-10 space-y-10 overflow-y-auto custom-scrollbar">
        
        {/* 1. HEADER AREA: TITLE & PLATFORM */}
        <div className="space-y-6">
            <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-400 pl-1 tracking-widest">Titre du post</label>
                <Input 
                    value={editForm.title || ""} 
                    onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                    className="h-14 bg-slate-50 border-slate-200 font-black uppercase text-base rounded-2xl focus:ring-purple-500/20 px-6"
                    placeholder={isVisualMode ? "Nom de votre création (ex: Promo Ramadan)..." : "Ex: PROMO WEEKEND DAKAR"}
                />
            </div>

            {!isVisualMode && (
                <div className="space-y-3">
                    <label className="text-xs font-black uppercase text-slate-400 pl-1 tracking-widest">Plateforme de diffusion</label>
                    <div className="flex flex-wrap gap-3">
                        {platforms.map((p) => (
                            <button
                                key={p.id}
                                onClick={() => setEditForm({...editForm, platform: p.id})}
                                className={cn(
                                    "flex items-center gap-3 px-6 py-3 rounded-2xl border transition-all",
                                    editForm.platform === p.id 
                                        ? "bg-slate-900 border-slate-900 text-white shadow-lg" 
                                        : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
                                )}
                            >
                                <span className="text-[11px] font-black uppercase tracking-tight">{p.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>

        {/* 2. CORE CONTENT - DYNAMIC LAYOUT BASED ON MODE */}
        <div className={cn(
            "flex flex-col gap-10 items-start",
            isVisualMode ? "max-w-2xl mx-auto w-full" : "lg:flex-row"
        )}>
          
          {/* Left: Message Editor (Only in Standard mode) */}
          {!isVisualMode && (
            <div className="w-full lg:w-[68%] shrink-0 space-y-4">
              <div className="space-y-3 relative">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-black uppercase text-slate-400 pl-1 tracking-widest">Texte / Légende</label>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={onRefine}
                    disabled={isRefining || !editForm.content}
                    className="h-9 text-[10px] font-black uppercase text-purple-600 border-purple-100 bg-purple-50 hover:bg-purple-100 rounded-full gap-2 px-5"
                  >
                    {isRefining ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wand2 className="w-3.5 h-3.5" />}
                    Magic Fix IA
                  </Button>
                </div>
                <Textarea 
                  value={editForm.content || ""} 
                  onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                  className="min-h-[500px] bg-slate-50 border-slate-200 leading-relaxed text-sm p-8 rounded-[2.5rem] resize-none focus:ring-purple-500/10 shadow-inner"
                  placeholder="Écrivez votre message ici..."
                />
              </div>
            </div>
          )}

          {/* Right: Image Area (Always visible, adapted in Visual mode) */}
          <div className={cn(
              "space-y-4",
              isVisualMode ? "w-full max-w-[500px] mx-auto" : "w-full lg:w-[32%]"
          )}>
            <label className="text-xs font-black uppercase text-slate-400 pl-1 tracking-widest">
                {isVisualMode ? 'Fichier PNG / Votre Création' : 'PNG / Image Star'}
            </label>
            <div 
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={cn(
                "bg-slate-50 rounded-[3rem] border-2 border-dashed border-slate-200 p-3 overflow-hidden transition-all shadow-inner",
                isVisualMode ? "aspect-square" : "h-[500px]",
                "flex items-center justify-center w-full",
                isDragging && "border-purple-500 bg-purple-50/50 scale-[1.02]"
              )}
            >
              {editForm.image_url ? (
                <div className="relative h-full w-full rounded-[2.5rem] overflow-hidden shadow-2xl group bg-slate-900">
                  <img src={editForm.image_url} alt="Preview" className="w-full h-full object-contain" />
                  <button 
                    onClick={() => setEditForm({...editForm, image_url: null})}
                    className="absolute top-6 right-6 p-3 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-all hover:scale-110 shadow-xl"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="h-full w-full bg-white border-2 border-dashed border-slate-200 rounded-[2.5rem] flex flex-col items-center justify-center gap-5 cursor-pointer hover:bg-slate-50 hover:border-purple-300 transition-all group p-8"
                >
                  {isUploading ? <Loader2 className="w-14 h-14 text-purple-600 animate-spin" /> : <ImagePlus className="w-14 h-14 text-slate-200 group-hover:text-purple-400 transition-all group-hover:scale-110" />}
                  <div className="space-y-2 text-center">
                    <p className="text-xs font-black uppercase text-slate-900 tracking-tight leading-none">
                        {isVisualMode ? 'Glisser votre visuel ici' : 'Ajouter image'}
                    </p>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest italic leading-tight">PNG / JPG</p>
                  </div>
                </div>
              )}
              <input type="file" ref={fileInputRef} onChange={onFileUpload} className="hidden" accept="image/*,application/pdf" />
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 border-t border-slate-100 bg-white shrink-0 mt-auto">
        <Button 
          onClick={onSave} 
          disabled={isUpdating || (isVisualMode && !editForm.image_url)} 
          className="w-full h-14 bg-green-600 hover:bg-green-700 text-white rounded-[1.5rem] gap-3 font-black uppercase text-xs shadow-xl shadow-green-100"
        >
          {isUpdating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
          {isVisualMode && !editForm.image_url ? "Attachez votre visuel pour enregistrer" : "Enregistrer le Brouillon"}
        </Button>
      </div>
    </Card>
  );
}
