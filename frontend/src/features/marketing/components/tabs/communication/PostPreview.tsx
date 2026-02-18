"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Send, PlusCircle, Edit3, ImageIcon, ExternalLink
} from "lucide-react";
import { MarketingComm } from "../../../types";
import { cn } from "@/lib/utils";

interface PostPreviewProps {
  activePost: MarketingComm;
  onStartEdit: (comm: MarketingComm) => void;
}

export function PostPreview({ activePost, onStartEdit }: PostPreviewProps) {
  // Détection automatique : Si le contenu est très court (ou vide) mais qu'il y a une image -> C'est un post VISUEL
  const isVisualPost = !!activePost.image_url && (!activePost.content || activePost.content.length < 50);

  return (
    <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden animate-in zoom-in-95 duration-300 h-full">
      <Card className={cn(
        "bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-y-auto custom-scrollbar p-10 space-y-8 relative transition-all",
        isVisualPost ? "col-span-4" : "col-span-7"
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 text-left">
            <div className="p-3 bg-blue-500/10 rounded-2xl text-blue-600">
              <Send className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-xl font-black uppercase text-slate-900 tracking-tight">{activePost.title}</h4>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">{activePost.platform} • {activePost.status}</p>
            </div>
          </div>
          {!isVisualPost && (
            <Button variant="outline" onClick={() => onStartEdit(activePost)} className="rounded-xl border-slate-200 font-black uppercase text-[10px] h-10 px-6 gap-2">
              <Edit3 className="w-3.5 h-3.5" /> Éditer
            </Button>
          )}
        </div>

        <div className={cn(
          "bg-slate-50 rounded-[2rem] p-8 border border-slate-100 relative text-left",
          isVisualPost ? "p-4 border-dashed" : "p-8"
        )}>
          <div className="absolute -top-3 -left-3 bg-blue-600 text-white p-1.5 rounded-lg shadow-lg z-10"><PlusCircle className="w-4 h-4" /></div>
          <p className={cn(
            "text-slate-800 leading-relaxed font-medium whitespace-pre-wrap",
            isVisualPost ? "text-[10px] italic opacity-60 text-center" : "text-base"
          )}>
            {activePost.content || "Post visuel pur (aucune légende)"}
          </p>
          
          {activePost.hashtags && activePost.hashtags.length > 0 && (
            <div className="mt-8 flex flex-wrap gap-2">
              {activePost.hashtags.map((tag, i) => (
                <span key={i} className="text-[10px] font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">#{tag}</span>
              ))}
            </div>
          )}
        </div>

        {isVisualPost && (
          <Button variant="outline" onClick={() => onStartEdit(activePost)} className="w-full rounded-2xl border-slate-200 font-black uppercase text-[10px] h-12 gap-2">
            <Edit3 className="w-3.5 h-3.5" /> Modifier le visuel / titre
          </Button>
        )}
      </Card>

      <div className={cn(
        "flex flex-col gap-6 transition-all",
        isVisualPost ? "col-span-8" : "col-span-5"
      )}>
        {activePost.image_url ? (
          <Card className="flex-1 bg-slate-900 border-none rounded-[3rem] shadow-2xl overflow-hidden relative group">
            <img src={activePost.image_url} alt="Post Visual" className="w-full h-full object-contain" />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
              <Button size="sm" className="bg-white text-slate-900 hover:bg-white rounded-full font-black uppercase text-[10px] h-10 px-6 gap-2" asChild>
                <a href={activePost.image_url} target="_blank" rel="noreferrer"><ExternalLink className="w-4 h-4" /> Plein écran</a>
              </Button>
            </div>
            {isVisualPost && (
              <div className="absolute top-6 left-6">
                <span className="bg-purple-600 text-white px-4 py-1.5 rounded-full text-[10px] font-black uppercase shadow-xl border border-white/20">Post Visuel (PNG)</span>
              </div>
            )}
          </Card>
        ) : (
          <div className="flex-1 bg-slate-100 border-2 border-dashed border-slate-200 rounded-[2.5rem] flex flex-col items-center justify-center p-10 text-center gap-4 opacity-50 h-full">
            <ImageIcon className="w-12 h-12 text-slate-300" />
            <p className="text-xs font-black uppercase text-slate-400 tracking-widest">Aucun visuel final attaché</p>
            <Button variant="ghost" onClick={() => onStartEdit(activePost)} className="text-[10px] font-black uppercase text-purple-600 hover:bg-purple-50">Ajouter un média</Button>
          </div>
        )}
      </div>
    </div>
  );
}
