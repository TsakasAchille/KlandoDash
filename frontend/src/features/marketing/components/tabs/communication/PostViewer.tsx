"use client";

import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import Image from "next/image";
import {
  Send, Edit3, Image as ImageIcon, ExternalLink, Trash2, RotateCcw,
  PenLine, Hash, Sparkles, Calendar, Clock, ChevronLeft,
  Wand2, Loader2, X, Save, ImagePlus, Type,
  Instagram, Linkedin, Twitter
} from "lucide-react";

// Helper component for Platform Logos
export function PlatformLogo({ platform, className = "w-4 h-4" }: { platform: CommPlatform, className?: string }) {
  switch (platform) {
    case 'INSTAGRAM': return <Instagram className={className} />;
    case 'LINKEDIN': return <Linkedin className={className} />;
    case 'X': return <Twitter className={className} />;
    case 'TIKTOK': return (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.17-2.81-.74-3.94-1.69-.16-.13-.31-.27-.45-.4v6.38c-.01 2.57-.88 5.1-2.73 6.84-1.91 1.81-4.74 2.52-7.31 1.94-2.55-.57-4.74-2.42-5.6-4.9-.81-2.31-.44-5.01 1.04-7.01 1.51-2.02 4.13-3.04 6.59-2.52.14.03.27.07.41.11v4.07c-.87-.34-1.87-.34-2.73.08-1.07.53-1.78 1.67-1.83 2.87-.03 1.21.5 2.45 1.43 3.16.95.73 2.31.84 3.35.27.91-.5 1.44-1.49 1.46-2.52l.01-14.68z"/>
      </svg>
    );
    default: return <ImageIcon className={className} />;
  }
}
import { MarketingComm, CommPlatform } from "@/app/marketing/types";
import {
  updateMarketingCommAction,
  refineMarketingContentAction
} from "@/app/marketing/actions/communication";
import { uploadMarketingImageAction } from "@/app/marketing/actions/mailing";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface PostViewerProps {
  post: MarketingComm;
  onClose: () => void;
  onTrash: (id: string) => void;
  onRestore: (id: string) => void;
  onDeletePerm: (id: string) => void;
  onUpdate?: (post: MarketingComm) => void;
  onMobileBack?: () => void;
}

export function PostViewer({
  post,
  onClose,
  onTrash,
  onRestore,
  onDeletePerm,
  onUpdate,
  onMobileBack
}: PostViewerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingComm>>({});
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const lastLoadedId = useRef<string | null>(null);

  // Reset form when post changes (like MailViewer)
  useEffect(() => {
    setEditForm({
      title: post.title,
      content: post.content,
      hashtags: post.hashtags || [],
      visual_suggestion: post.visual_suggestion || '',
      platform: post.platform,
      image_url: post.image_url || null
    });
    
    // Auto-edit mode ONLY when switching to a brand new post ID
    if (lastLoadedId.current !== post.id) {
        const isBrandNew = !post.content && post.status === 'DRAFT' && post.title === "Nouvelle publication";
        setIsEditing(isBrandNew);
        lastLoadedId.current = post.id;
    }
  }, [post]);

  const isInTrash = post.status === 'TRASH';

  const handleSave = async () => {
    setIsUpdating(true);
    try {
      const updates = { ...editForm, status: 'DRAFT' as const };
      const res = await updateMarketingCommAction(post.id, updates);
      if (res.success) {
        toast.success("Publication mise à jour !");
        setIsEditing(false);
        // Notifier le parent avec le post fusionné
        if (onUpdate) {
            onUpdate({ ...post, ...updates });
        }
      }
    } catch {
      toast.error("Erreur de sauvegarde");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRefine = async () => {
    if (!editForm.content) return;
    setIsRefining(true);
    try {
      const res = await refineMarketingContentAction(editForm.content, editForm.platform || 'GENERAL');
      if (res.success && res.refinedContent) {
        setEditForm(prev => ({ ...prev, content: res.refinedContent }));
        toast.success("Texte amélioré !");
      }
    } catch {
      toast.error("Échec de l'amélioration");
    } finally {
      setIsRefining(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement> | File) => {
    const file = e instanceof File ? e : e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
      const base64 = reader.result as string;
      const res = await uploadMarketingImageAction(base64);
      if (res.success && res.url) {
        setEditForm(prev => ({ ...prev, image_url: res.url }));
        toast.success("Fichier attaché !");
      }
      setIsUploading(false);
    };
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileUpload(file);
  };

  const formatDate = (date: string | null | undefined) => {
    if (!date) return null;
    return new Date(date).toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  const platforms: { id: CommPlatform; label: string }[] = [
    { id: 'TIKTOK', label: 'TikTok' },
    { id: 'INSTAGRAM', label: 'Instagram' },
    { id: 'LINKEDIN', label: 'LinkedIn' },
    { id: 'X', label: 'X / Twitter' },
    { id: 'OTHER', label: 'Autre' },
  ];

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
            isEditing ? "bg-purple-600 shadow-purple-200" :
            isInTrash ? "bg-red-500 shadow-red-100" : "bg-purple-600 shadow-purple-200"
          )}>
            {isEditing ? <PenLine className="w-5 h-5" /> :
             isInTrash ? <Trash2 className="w-5 h-5" /> : <Send className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="text-sm font-black uppercase text-slate-900">
              {isEditing ? "Éditeur de Publication" : post.title}
            </h4>
            <div className="flex items-center gap-2 mt-0.5">
              <div className={cn(
                "flex items-center gap-1.5 px-2 py-0.5 rounded-md",
                post.platform === 'TIKTOK' ? "bg-pink-50 text-pink-600" :
                post.platform === 'INSTAGRAM' ? "bg-purple-50 text-purple-600" :
                post.platform === 'LINKEDIN' ? "bg-blue-50 text-blue-700" :
                post.platform === 'OTHER' ? "bg-slate-100 text-slate-600" :
                "bg-blue-50 text-blue-500"
              )}>
                <PlatformLogo platform={post.platform} className="w-2.5 h-2.5" />
                <span className="text-[9px] font-black uppercase">
                  {post.platform}
                </span>
              </div>
              {!isEditing && (
                <span className={cn(
                  "text-[9px] font-black uppercase px-2 py-0.5 rounded-md",
                  post.status === 'PUBLISHED' ? "bg-green-50 text-green-600" :
                  post.status === 'TRASH' ? "bg-red-50 text-red-500" :
                  "bg-amber-50 text-amber-600"
                )}>
                  {post.status === 'NEW' || post.status === 'DRAFT' ? 'BROUILLON' : post.status === 'PUBLISHED' ? 'PUBLIÉ' : post.status}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!isInTrash && !isEditing && (
            <Button variant="outline" size="sm" onClick={() => setIsEditing(true)} className="rounded-full border-slate-200 font-black uppercase text-[10px] h-9 px-5 gap-2">
              <Edit3 className="w-3.5 h-3.5" /> Éditer
            </Button>
          )}
          {isEditing && (
            <Button variant="ghost" size="icon" onClick={() => setIsEditing(false)} className="rounded-full hover:bg-slate-100">
              <X className="w-5 h-5" />
            </Button>
          )}
        </div>
      </div>

      {/* CONTENT AREA */}
      <div className="p-6 md:p-8 space-y-6 overflow-y-auto custom-scrollbar flex-1">
        {isEditing ? (
          /* ──── EDIT MODE ──── */
          <div className="space-y-8">
            {/* Title & Platform */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                  <Type className="w-3 h-3" /> Titre de référence
                </label>
                <Input
                  value={editForm.title || ""}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  className="h-12 bg-slate-50 border-slate-200 font-black uppercase text-sm rounded-xl focus:ring-purple-500/20 px-4"
                  placeholder="Nom interne du post..."
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest">Plateforme cible</label>
                <div className="flex flex-wrap gap-2">
                  {platforms.map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => setEditForm({ ...editForm, platform: p.id })}
                      className={cn(
                        "flex-1 min-w-[80px] flex items-center justify-center gap-2 py-2.5 rounded-xl border transition-all text-[9px] font-black uppercase tracking-tighter",
                        editForm.platform === p.id
                          ? "bg-slate-900 border-slate-900 text-white shadow-md"
                          : "bg-white border-slate-200 text-slate-500 hover:bg-slate-50"
                      )}
                    >
                      <PlatformLogo platform={p.id} className="w-3.5 h-3.5" />
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
              {/* Content Editor (2/3) */}
              <div className="lg:col-span-2 space-y-8">
                <div className="space-y-3 relative">
                  <div className="flex justify-between items-center">
                    <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                      <PenLine className="w-3 h-3" /> Description / Légende
                    </label>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRefine}
                      disabled={isRefining || !editForm.content}
                      className="h-8 text-[9px] font-black uppercase text-purple-600 border-purple-100 bg-purple-50 hover:bg-purple-100 rounded-full gap-2 px-4"
                    >
                      {isRefining ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
                      Améliorer par IA
                    </Button>
                  </div>
                  <Textarea
                    value={editForm.content || ""}
                    onChange={(e) => setEditForm({ ...editForm, content: e.target.value })}
                    className="min-h-[180px] lg:min-h-[300px] bg-slate-50 border-slate-200 leading-relaxed text-sm p-4 lg:p-6 rounded-2xl resize-none focus:ring-purple-500/10 shadow-inner"
                    placeholder="Contenu de la publication (optionnel si post visuel uniquement)..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                      <Hash className="w-3 h-3 text-purple-500" /> Hashtags
                    </label>
                    <Textarea
                      value={(editForm.hashtags || []).join(' ')}
                      onChange={(e) => setEditForm({ ...editForm, hashtags: e.target.value.split(' ') })}
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
                      onChange={(e) => setEditForm({ ...editForm, visual_suggestion: e.target.value })}
                      className="h-24 bg-slate-50 border-slate-200 text-[11px] p-4 rounded-xl resize-none italic text-slate-600"
                      placeholder="Brief pour le créateur : 'Une photo de famille dans une voiture...'"
                    />
                  </div>
                </div>
              </div>

              {/* Media Upload (1/3) */}
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
                        onClick={() => setEditForm({ ...editForm, image_url: null })}
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
                  <input type="file" ref={fileInputRef} onChange={(e) => handleFileUpload(e)} className="hidden" accept="image/*" />
                </div>

                {(editForm.platform === 'INSTAGRAM' || editForm.platform === 'TIKTOK') && (
                  <div className="p-4 bg-purple-50 border border-purple-100 rounded-xl">
                    <p className="text-[9px] font-black text-purple-700 uppercase mb-1">Note {editForm.platform}</p>
                    <p className="text-[10px] text-purple-600 leading-tight">
                      N&apos;oubliez pas d&apos;inclure l&apos;URL de téléchargement dans votre bio ou description pour convertir les vues.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* ──── VIEW MODE ──── */
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Text content (2/3) */}
              <div className="lg:col-span-2 space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                    <PenLine className="w-3 h-3" /> Description / Légende
                  </label>
                  <div className="bg-slate-50 rounded-2xl border border-slate-100 p-5 shadow-inner">
                    <p className={cn(
                      "text-sm text-slate-800 leading-relaxed whitespace-pre-wrap",
                      !post.content && "text-slate-400 italic text-xs"
                    )}>
                      {post.content || "Aucune légende (post visuel uniquement)"}
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                    <Hash className="w-3 h-3 text-purple-500" /> Hashtags
                  </label>
                  {post.hashtags && post.hashtags.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {post.hashtags.map((tag: string, i: number) => (
                        <span key={i} className="text-[10px] font-bold text-purple-600 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-100">#{tag}</span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[10px] text-slate-400 italic pl-1">Aucun hashtag</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                    <Sparkles className="w-3 h-3 text-klando-gold" /> Idée Visuelle
                  </label>
                  {post.visual_suggestion ? (
                    <div className="bg-amber-50/50 rounded-xl border border-amber-100 p-4">
                      <p className="text-[11px] text-amber-800 leading-relaxed italic">{post.visual_suggestion}</p>
                    </div>
                  ) : (
                    <p className="text-[10px] text-slate-400 italic pl-1">Aucune suggestion visuelle</p>
                  )}
                </div>
              </div>

              {/* Image (1/3) */}
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-slate-400 pl-1 tracking-widest flex items-center gap-2">
                  <ImageIcon className="w-3 h-3" /> Image Attachée
                </label>
                {post.image_url ? (
                  <div className="relative bg-slate-900 rounded-2xl shadow-lg overflow-hidden group border-2 border-white aspect-square">
                    <Image
                      src={post.image_url}
                      alt="Preview"
                      fill
                      className="object-contain"
                      sizes="(max-width: 768px) 100vw, 400px"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      <Button size="sm" className="bg-white text-slate-900 hover:bg-white rounded-full font-black uppercase text-[9px] h-8 px-4 gap-1.5" asChild>
                        <a href={post.image_url} target="_blank" rel="noreferrer"><ExternalLink className="w-3 h-3" /> Plein écran</a>
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

            {/* Metadata dates */}
            <div className="flex flex-wrap gap-4 pt-2 border-t border-slate-100">
              {post.created_at && (
                <div className="flex items-center gap-1.5 text-[9px] text-slate-400">
                  <Clock className="w-3 h-3" />
                  <span className="font-bold uppercase">Créé :</span> {formatDate(post.created_at)}
                </div>
              )}
              {post.updated_at && (
                <div className="flex items-center gap-1.5 text-[9px] text-slate-400">
                  <Calendar className="w-3 h-3" />
                  <span className="font-bold uppercase">Modifié :</span> {formatDate(post.updated_at)}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* FOOTER */}
      <div className="p-4 lg:p-6 border-t border-slate-100 bg-white shrink-0 mt-auto">
        {isEditing ? (
          <Button
            onClick={handleSave}
            disabled={isUpdating}
            className="w-full h-14 bg-green-600 hover:bg-green-700 text-white rounded-2xl gap-3 font-black uppercase text-xs shadow-xl transition-all"
          >
            {isUpdating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            Enregistrer le Brouillon
          </Button>
        ) : isInTrash ? (
          <div className="flex gap-3">
            <Button
              onClick={() => onRestore(post.id)}
              className="flex-1 h-11 rounded-xl bg-green-600 hover:bg-green-700 text-white font-black uppercase text-[10px] gap-2 shadow-lg shadow-green-100"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Restaurer
            </Button>
            <Button
              onClick={() => onDeletePerm(post.id)}
              variant="destructive"
              className="flex-1 h-11 rounded-xl font-black uppercase text-[10px] gap-2 shadow-lg shadow-red-100"
            >
              <Trash2 className="w-3.5 h-3.5" /> Supprimer définitivement
            </Button>
          </div>
        ) : (
          <Button
            variant="ghost"
            onClick={() => onTrash(post.id)}
            className="text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl font-black uppercase text-[10px] gap-2 px-5 h-10"
          >
            <Trash2 className="w-3.5 h-3.5" /> Placer dans la corbeille
          </Button>
        )}
      </div>
    </Card>
  );
}
