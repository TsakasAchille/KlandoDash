"use client";

import { useRef, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Edit3, Wand2, Loader2, X, Save, ImagePlus, Hash, Sparkles, Type
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
      {/* HEADER */}
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30 shrink-0">
        <div className="flex items-center gap-3">
          <div className={cn(
            "p-2 rounded-xl text-white shadow-lg",
            isVisualMode ? "bg-purple-600 shadow-purple-200" : "bg-blue-600 shadow-blue-200"
          )}>
            {isVisualMode ? <ImagePlus className="w-5 h-5" /> : <Edit3 className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">
                {isVisualMode ? 'Post Visuel (PNG)' : 'Post Standard (Texte)'}
            </h4>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                {editForm.platform || 'Choisir plateforme'}
            </p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full hover:bg-slate-100">
          <X className="w-5 h-5" />
        </Button>
      </div>

      <div className="p-8 md:p-10 space-y-8 overflow-y-auto custom-scrollbar">
        
        {/* 1. TOP BAR: TITLE & PLATFORM */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                    <Type className="w-3 h-3" /> Titre de référence
                </label>
                <Input 
                    value={editForm.title || ""} 
                    onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                    className="h-12 bg-slate-50 border-slate-200 font-black uppercase text-sm rounded-xl focus:ring-purple-500/20 px-4"
                    placeholder="Nom interne du post..."
                />
            </div>

            <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest">Plateforme cible</label>
                <div className="flex gap-2">
                    {platforms.map((p) => (
                        <button
                            key={p.id}
                            type="button"
                            onClick={() => setEditForm({...editForm, platform: p.id})}
                            className={cn(
                                "flex-1 flex items-center justify-center py-3 rounded-xl border transition-all text-[10px] font-black uppercase tracking-tighter",
                                editForm.platform === p.id 
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
            {/* 2. LEFT: CONTENT EDITOR (66%) */}
            <div className="lg:col-span-2 space-y-8">
                {/* Main Content / Description */}
                <div className="space-y-3 relative">
                    <div className="flex justify-between items-center">
                        <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                            <PenLine className="w-3 h-3" /> Description / Légende
                        </label>
                        <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={onRefine}
                            disabled={isRefining || !editForm.content}
                            className="h-8 text-[9px] font-black uppercase text-purple-600 border-purple-100 bg-purple-50 hover:bg-purple-100 rounded-full gap-2 px-4"
                        >
                            {isRefining ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
                            Améliorer par IA
                        </Button>
                    </div>
                    <Textarea 
                        value={editForm.content || ""} 
                        onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                        className="min-h-[300px] bg-slate-50 border-slate-200 leading-relaxed text-sm p-6 rounded-2xl resize-none focus:ring-purple-500/10 shadow-inner"
                        placeholder={isVisualMode ? "Détails optionnels sur le visuel..." : "Contenu de la publication..."}
                    />
                </div>

                {/* Hashtags & Bio Section (Platform specific feel) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                            <Hash className="w-3 h-3 text-purple-500" /> Hashtags
                        </label>
                        <Textarea 
                            value={(editForm.hashtags || []).join(' ')} 
                            onChange={(e) => setEditForm({...editForm, hashtags: e.target.value.split(' ')})}
                            className="h-24 bg-slate-50 border-slate-200 text-[11px] font-bold p-4 rounded-xl resize-none"
                            placeholder="#carpooling #senegal #klando..."
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                            <Sparkles className="w-3 h-3 text-klando-gold" /> Idée Visuelle
                        </label>
                        <Textarea 
                            value={editForm.visual_suggestion || ""} 
                            onChange={(e) => setEditForm({...editForm, visual_suggestion: e.target.value})}
                            className="h-24 bg-slate-50 border-slate-200 text-[11px] p-4 rounded-xl resize-none italic text-slate-600"
                            placeholder="Brief pour le créateur : 'Une photo de famille dans une voiture...'"
                        />
                    </div>
                </div>
            </div>

            {/* 3. RIGHT: MEDIA PREVIEW (33%) */}
            <div className="space-y-4">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                    <ImagePlus className="w-3 h-3" /> Image Attachée
                </label>
                <div 
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={cn(
                        "bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 p-2 overflow-hidden transition-all shadow-inner",
                        "aspect-square flex items-center justify-center w-full",
                        isDragging && "border-purple-500 bg-purple-50/50 scale-[1.02]"
                    )}
                >
                    {editForm.image_url ? (
                        <div className="relative h-full w-full rounded-[1.8rem] overflow-hidden shadow-xl group bg-slate-900">
                            <img src={editForm.image_url} alt="Preview" className="w-full h-full object-contain" />
                            <button 
                                onClick={() => setEditForm({...editForm, image_url: null})}
                                className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-all hover:scale-110 shadow-lg"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <div 
                            onClick={() => fileInputRef.current?.click()}
                            className="h-full w-full bg-white border-2 border-dashed border-slate-200 rounded-[1.8rem] flex flex-col items-center justify-center gap-4 cursor-pointer hover:bg-slate-50 transition-all group"
                        >
                            {isUploading ? <Loader2 className="w-10 h-10 text-purple-600 animate-spin" /> : <ImagePlus className="w-10 h-10 text-slate-200 group-hover:text-purple-400 transition-all" />}
                            <div className="text-center px-4">
                                <p className="text-[10px] font-black uppercase text-slate-900 tracking-tight">Ajouter média</p>
                                <p className="text-[8px] text-slate-400 italic">PNG, JPG ou Screenshot</p>
                            </div>
                        </div>
                    )}
                    <input type="file" ref={fileInputRef} onChange={onFileUpload} className="hidden" accept="image/*" />
                </div>
                
                {/* Platform specific bio notice */}
                {(editForm.platform === 'INSTAGRAM' || editForm.platform === 'TIKTOK') && (
                    <div className="p-4 bg-purple-50 border border-purple-100 rounded-xl">
                        <p className="text-[9px] font-black text-purple-700 uppercase mb-1">💡 Note {editForm.platform}</p>
                        <p className="text-[10px] text-purple-600 leading-tight">
                            N&apos;oubliez pas d&apos;inclure l&apos;URL de téléchargement dans votre bio ou description pour convertir les vues.
                        </p>
                    </div>
                )}
            </div>
        </div>
      </div>

      <div className="p-8 border-t border-slate-100 bg-white shrink-0 mt-auto">
        <Button 
          onClick={onSave} 
          disabled={isUpdating || (isVisualMode && !editForm.image_url)} 
          className={cn(
            "w-full h-14 text-white rounded-2xl gap-3 font-black uppercase text-xs shadow-xl transition-all",
            isVisualMode ? "bg-purple-600 hover:bg-purple-700" : "bg-green-600 hover:bg-green-700"
          )}
        >
          {isUpdating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
          {isVisualMode && !editForm.image_url ? "Attachez votre visuel pour enregistrer" : "Enregistrer le Brouillon"}
        </Button>
      </div>
    </Card>
  );
}

// Sub-component Helper
function PenLine({ className }: { className?: string }) {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
    )
}
