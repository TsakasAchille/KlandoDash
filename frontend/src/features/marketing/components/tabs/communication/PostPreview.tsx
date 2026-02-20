"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { 
  Send, PlusCircle, Edit3, Image as ImageIcon, ExternalLink, Trash2, RotateCcw
} from "lucide-react";
import { MarketingComm } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

interface PostPreviewProps {
  activePost: MarketingComm;
  onStartEdit: (comm: MarketingComm) => void;
  onTrash: (id: string) => void;
  onRestore: (id: string) => void;
  onDeletePerm: (id: string) => void;
}

export function PostPreview({ 
    activePost, 
    onStartEdit, 
    onTrash, 
    onRestore, 
    onDeletePerm 
}: PostPreviewProps) {
  // Détection automatique : Si le contenu est très court (ou vide) mais qu'il y a une image -> C'est un post VISUEL
  const isVisualPost = !!activePost.image_url && (!activePost.content || activePost.content.length < 50);
  const isInTrash = activePost.status === 'TRASH';

  return (
    <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col text-left animate-in zoom-in-95 duration-300">
      {/* 1. HEADER (Même style que l'Editor) */}
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30 shrink-0">
        <div className="flex items-center gap-3">
          <div className={cn(
              "p-2 rounded-xl text-white shadow-lg",
              isInTrash ? "bg-red-500 shadow-red-100" : "bg-blue-600 shadow-blue-100"
          )}>
            {isInTrash ? <Trash2 className="w-5 h-5" /> : <Send className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">{activePost.title}</h4>
            <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest">{activePost.platform} • {activePost.status}</p>
          </div>
        </div>
        
        {!isInTrash && (
          <Button variant="outline" size="sm" onClick={() => onStartEdit(activePost)} className="rounded-full border-slate-200 font-black uppercase text-[10px] h-9 px-5 gap-2">
            <Edit3 className="w-3.5 h-3.5" /> Éditer
          </Button>
        )}
      </div>

      {/* 2. CONTENT AREA (Scrollable) */}
      <div className="p-8 md:p-10 space-y-10 overflow-y-auto custom-scrollbar">
        
        <div className={cn(
            "flex flex-col gap-10 items-start",
            isVisualPost ? "max-w-2xl mx-auto w-full" : "lg:flex-row"
        )}>
          
          {/* Left/Main: Content */}
          <div className={cn(
            "space-y-6",
            isVisualPost ? "w-full" : "w-full lg:w-[60%]"
          )}>
            <div className={cn(
              "bg-slate-50 rounded-[2.5rem] border border-slate-100 relative shadow-inner",
              isVisualPost ? "p-6 border-dashed text-center" : "p-10"
            )}>
              {!isInTrash && <div className="absolute -top-3 -left-3 bg-blue-600 text-white p-1.5 rounded-lg shadow-lg z-10"><PlusCircle className="w-4 h-4" /></div>}
              <p className={cn(
                "text-slate-800 leading-relaxed font-medium whitespace-pre-wrap",
                isVisualPost ? "text-[10px] italic opacity-60" : "text-base"
              )}>
                {activePost.content || "Post visuel pur (aucune légende)"}
              </p>
              
              {activePost.hashtags && activePost.hashtags.length > 0 && (
                <div className="mt-8 flex flex-wrap gap-2 justify-center lg:justify-start">
                  {activePost.hashtags.map((tag: string, i: number) => (
                    <span key={i} className="text-[10px] font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">#{tag}</span>
                  ))}
                </div>
              )}
            </div>

            {isVisualPost && !isInTrash && (
                <div className="flex justify-center">
                    <Button variant="ghost" onClick={() => onStartEdit(activePost)} className="text-[10px] font-black uppercase text-purple-600 hover:bg-purple-50 rounded-full px-8">
                        Changer le visuel ou le titre
                    </Button>
                </div>
            )}
          </div>

          {/* Right/Side: Image */}
          <div className={cn(
            "space-y-4",
            isVisualPost ? "w-full max-w-[500px] mx-auto" : "w-full lg:w-[40%]"
          )}>
            {activePost.image_url ? (
              <div className={cn(
                "relative bg-slate-900 rounded-[3rem] shadow-2xl overflow-hidden group border-4 border-white",
                isVisualPost ? "aspect-square" : "aspect-[4/5]"
              )}>
                <Image 
                  src={activePost.image_url} 
                  alt="Preview" 
                  fill
                  className="object-contain" 
                  sizes="(max-width: 768px) 100vw, 500px"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Button size="sm" className="bg-white text-slate-900 hover:bg-white rounded-full font-black uppercase text-[10px] h-10 px-6 gap-2" asChild>
                    <a href={activePost.image_url} target="_blank" rel="noreferrer"><ExternalLink className="w-4 h-4" /> Voir plein écran</a>
                  </Button>
                </div>
              </div>
            ) : (
              <div className="aspect-[4/5] bg-slate-50 border-2 border-dashed border-slate-200 rounded-[3rem] flex flex-col items-center justify-center p-8 text-center gap-4 opacity-40">
                <ImageIcon className="w-10 h-10 text-slate-300" />
                <p className="text-[10px] font-black uppercase text-slate-400">Aucun visuel attaché</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. FOOTER (Actions de corbeille) */}
      <div className="p-8 border-t border-slate-100 bg-white shrink-0 mt-auto">
        {isInTrash ? (
            <div className="flex gap-4">
                <Button 
                    onClick={() => onRestore(activePost.id)}
                    className="flex-1 h-12 rounded-xl bg-green-600 hover:bg-green-700 text-white font-black uppercase text-[10px] gap-2 shadow-lg shadow-green-100"
                >
                    <RotateCcw className="w-4 h-4" /> Restaurer le post
                </Button>
                <Button 
                    onClick={() => onDeletePerm(activePost.id)}
                    variant="destructive"
                    className="flex-1 h-12 rounded-xl font-black uppercase text-[10px] gap-2 shadow-lg shadow-red-100"
                >
                    <Trash2 className="w-4 h-4" /> Supprimer définitivement
                </Button>
            </div>
        ) : (
            <div className="flex justify-between items-center">
                <Button 
                    variant="ghost" 
                    onClick={() => onTrash(activePost.id)}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl font-black uppercase text-[10px] gap-2 px-6 h-12"
                >
                    <Trash2 className="w-4 h-4" /> Placer dans la corbeille
                </Button>
                
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest italic">
                    Dernière modification : {new Date().toLocaleDateString()}
                </p>
            </div>
        )}
      </div>
    </Card>
  );
}
