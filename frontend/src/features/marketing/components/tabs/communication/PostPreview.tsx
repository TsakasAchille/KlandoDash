"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import {
  Send, Edit3, Image as ImageIcon, ExternalLink, Trash2, RotateCcw,
  PenLine, Hash, Sparkles, Calendar, Clock, ChevronLeft
} from "lucide-react";
import { MarketingComm } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

interface PostPreviewProps {
  activePost: MarketingComm;
  onStartEdit: (comm: MarketingComm) => void;
  onTrash: (id: string) => void;
  onRestore: (id: string) => void;
  onDeletePerm: (id: string) => void;
  onMobileBack?: () => void;
}

export function PostPreview({
    activePost,
    onStartEdit,
    onTrash,
    onRestore,
    onDeletePerm,
    onMobileBack
}: PostPreviewProps) {
  const isInTrash = activePost.status === 'TRASH';
  const hasContent = !!activePost.content;
  const hasHashtags = activePost.hashtags && activePost.hashtags.length > 0;
  const hasVisualSuggestion = !!activePost.visual_suggestion;
  const hasImage = !!activePost.image_url;

  const formatDate = (date: string | null | undefined) => {
    if (!date) return null;
    return new Date(date).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col text-left animate-in zoom-in-95 duration-300">
      {/* HEADER */}
      <div className="p-4 lg:p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30 shrink-0">
        <div className="flex items-center gap-3">
          {onMobileBack && (
            <button onClick={onMobileBack} className="lg:hidden p-1.5 -ml-1 rounded-lg hover:bg-slate-100 text-slate-500">
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div className={cn(
              "p-2 rounded-xl text-white shadow-lg",
              isInTrash ? "bg-red-500 shadow-red-100" : "bg-purple-600 shadow-purple-200"
          )}>
            {isInTrash ? <Trash2 className="w-5 h-5" /> : <Send className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">{activePost.title}</h4>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={cn(
                "text-[9px] font-black uppercase px-2 py-0.5 rounded-md",
                activePost.platform === 'TIKTOK' ? "bg-pink-50 text-pink-600" :
                activePost.platform === 'INSTAGRAM' ? "bg-purple-50 text-purple-600" :
                activePost.platform === 'LINKEDIN' ? "bg-blue-50 text-blue-700" :
                activePost.platform === 'OTHER' ? "bg-slate-100 text-slate-600" :
                "bg-blue-50 text-blue-500"
              )}>
                {activePost.platform}
              </span>
              <span className={cn(
                "text-[9px] font-black uppercase px-2 py-0.5 rounded-md",
                activePost.status === 'PUBLISHED' ? "bg-green-50 text-green-600" :
                activePost.status === 'TRASH' ? "bg-red-50 text-red-500" :
                "bg-amber-50 text-amber-600"
              )}>
                {activePost.status === 'NEW' ? 'BROUILLON' : activePost.status === 'DRAFT' ? 'BROUILLON' : activePost.status === 'PUBLISHED' ? 'PUBLIÉ' : activePost.status}
              </span>
            </div>
          </div>
        </div>

        {!isInTrash && (
          <Button variant="outline" size="sm" onClick={() => onStartEdit(activePost)} className="rounded-full border-slate-200 font-black uppercase text-[10px] h-9 px-5 gap-2">
            <Edit3 className="w-3.5 h-3.5" /> Éditer
          </Button>
        )}
      </div>

      {/* CONTENT AREA */}
      <div className="p-6 md:p-8 space-y-6 overflow-y-auto custom-scrollbar">

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* LEFT: Text content (2/3) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description / Légende */}
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                <PenLine className="w-3 h-3" /> Description / Légende
              </label>
              <div className="bg-slate-50 rounded-2xl border border-slate-100 p-5 shadow-inner">
                <p className={cn(
                  "text-sm text-slate-800 leading-relaxed whitespace-pre-wrap",
                  !hasContent && "text-slate-400 italic text-xs"
                )}>
                  {activePost.content || "Aucune légende (post visuel uniquement)"}
                </p>
              </div>
            </div>

            {/* Hashtags */}
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                <Hash className="w-3 h-3 text-purple-500" /> Hashtags
              </label>
              {hasHashtags ? (
                <div className="flex flex-wrap gap-1.5">
                  {activePost.hashtags!.map((tag: string, i: number) => (
                    <span key={i} className="text-[10px] font-bold text-purple-600 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-100">#{tag}</span>
                  ))}
                </div>
              ) : (
                <p className="text-[10px] text-slate-400 italic pl-1">Aucun hashtag</p>
              )}
            </div>

            {/* Idée Visuelle */}
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                <Sparkles className="w-3 h-3 text-klando-gold" /> Idée Visuelle
              </label>
              {hasVisualSuggestion ? (
                <div className="bg-amber-50/50 rounded-xl border border-amber-100 p-4">
                  <p className="text-[11px] text-amber-800 leading-relaxed italic">{activePost.visual_suggestion}</p>
                </div>
              ) : (
                <p className="text-[10px] text-slate-400 italic pl-1">Aucune suggestion visuelle</p>
              )}
            </div>
          </div>

          {/* RIGHT: Image (1/3) */}
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
              <ImageIcon className="w-3 h-3" /> Image Attachée
            </label>
            {hasImage ? (
              <div className="relative bg-slate-900 rounded-2xl shadow-lg overflow-hidden group border-2 border-white aspect-square">
                <Image
                  src={activePost.image_url!}
                  alt="Preview"
                  fill
                  className="object-contain"
                  sizes="(max-width: 768px) 100vw, 400px"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Button size="sm" className="bg-white text-slate-900 hover:bg-white rounded-full font-black uppercase text-[9px] h-8 px-4 gap-1.5" asChild>
                    <a href={activePost.image_url!} target="_blank" rel="noreferrer"><ExternalLink className="w-3 h-3" /> Plein écran</a>
                  </Button>
                </div>
              </div>
            ) : (
              <div className="aspect-square bg-slate-50 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center gap-2 opacity-40">
                <ImageIcon className="w-8 h-8 text-slate-300" />
                <p className="text-[9px] font-black uppercase text-slate-400">Aucun visuel</p>
              </div>
            )}
          </div>
        </div>

        {/* METADATA: Dates */}
        <div className="flex flex-wrap gap-4 pt-2 border-t border-slate-100">
          {activePost.created_at && (
            <div className="flex items-center gap-1.5 text-[9px] text-slate-400">
              <Clock className="w-3 h-3" />
              <span className="font-bold uppercase">Créé :</span> {formatDate(activePost.created_at)}
            </div>
          )}
          {activePost.updated_at && (
            <div className="flex items-center gap-1.5 text-[9px] text-slate-400">
              <Calendar className="w-3 h-3" />
              <span className="font-bold uppercase">Modifié :</span> {formatDate(activePost.updated_at)}
            </div>
          )}
        </div>
      </div>

      {/* FOOTER (Actions) */}
      <div className="p-6 border-t border-slate-100 bg-white shrink-0 mt-auto">
        {isInTrash ? (
            <div className="flex gap-3">
                <Button
                    onClick={() => onRestore(activePost.id)}
                    className="flex-1 h-11 rounded-xl bg-green-600 hover:bg-green-700 text-white font-black uppercase text-[10px] gap-2 shadow-lg shadow-green-100"
                >
                    <RotateCcw className="w-3.5 h-3.5" /> Restaurer
                </Button>
                <Button
                    onClick={() => onDeletePerm(activePost.id)}
                    variant="destructive"
                    className="flex-1 h-11 rounded-xl font-black uppercase text-[10px] gap-2 shadow-lg shadow-red-100"
                >
                    <Trash2 className="w-3.5 h-3.5" /> Supprimer définitivement
                </Button>
            </div>
        ) : (
            <Button
                variant="ghost"
                onClick={() => onTrash(activePost.id)}
                className="text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl font-black uppercase text-[10px] gap-2 px-5 h-10"
            >
                <Trash2 className="w-3.5 h-3.5" /> Placer dans la corbeille
            </Button>
        )}
      </div>
    </Card>
  );
}
