"use client";

import { useState, useMemo, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Sparkles, Loader2, Megaphone, Music, Instagram, 
  Twitter, Send, Image as ImageIcon, History,
  PlusCircle, Target, Trash2, RotateCcw,
  Edit3, Save, X, MapPin, Wand2, Paperclip, FileText, CheckCircle2,
  ExternalLink, Search, Filter, Inbox
} from "lucide-react";
import { MarketingComm, CommPlatform, CommStatus } from "../../types";
import { 
    updateMarketingCommAction, 
    trashMarketingCommAction, 
    restoreMarketingCommAction, 
    deleteMarketingCommAction,
    createMarketingCommAction,
    refineMarketingContentAction
} from "../../actions/communication";
import { uploadMarketingImageAction } from "../../actions/mailing";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface CommunicationTabProps {
  comms: MarketingComm[];
  isScanning: boolean;
  onGenerateIdeas: () => void;
  onGeneratePost: (platform: CommPlatform, topic: string) => void;
  onPromotePending: (platform: CommPlatform) => void;
}

export function CommunicationTab({ 
  comms, 
  isScanning, 
  onGenerateIdeas, 
  onGeneratePost,
  onPromotePending
}: CommunicationTabProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [topic, setTopic] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [statusFilter, setStatusFilter] = useState<CommStatus | 'ALL'>('DRAFT');
  
  // États de sélection et édition
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingComm>>({});
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Filtrage intelligent
  const filteredComms = useMemo(() => {
    return comms.filter(c => {
        const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter || (statusFilter === 'DRAFT' && c.status === 'NEW');
        const matchesSearch = c.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                             c.content.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesStatus && matchesSearch && c.type === 'POST';
    });
  }, [comms, statusFilter, searchTerm]);

  // Post actif
  const activePost = useMemo(() => {
    if (selectedId) return comms.find(c => c.id === selectedId) || null;
    return null;
  }, [comms, selectedId]);

  const platforms: { id: CommPlatform; label: string; icon: any; color: string }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music, color: 'text-pink-500' },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram, color: 'text-purple-500' },
    { id: 'X', label: 'X / Twitter', icon: Twitter, color: 'text-blue-400' },
  ];

  const handleStartManual = () => {
    setEditingId("NEW_MANUAL");
    setSelectedId(null);
    setEditForm({ 
        title: "Nouvelle publication", 
        content: "", 
        hashtags: [],
        visual_suggestion: "",
        platform: 'INSTAGRAM',
        image_url: null
    });
  };

  const handleStartEdit = (comm: MarketingComm) => {
    setEditingId(comm.id);
    setEditForm({ 
        title: comm.title, 
        content: comm.content, 
        hashtags: comm.hashtags || [],
        visual_suggestion: comm.visual_suggestion || '',
        platform: comm.platform,
        image_url: comm.image_url || null
    });
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setIsUpdating(true);
    try {
        if (editingId === "NEW_MANUAL") {
            const res = await createMarketingCommAction({ ...editForm, status: 'DRAFT' });
            if (res.success && res.post) {
                toast.success("Publication créée !");
                setSelectedId(res.post.id);
                setEditingId(null);
            }
        } else {
            const res = await updateMarketingCommAction(editingId, { ...editForm, status: 'DRAFT' });
            if (res.success) {
                toast.success("Publication mise à jour !");
                setEditingId(null);
            }
        }
    } catch (err) {
        console.error(err);
        toast.error("Erreur de sauvegarde");
    } finally {
        setIsUpdating(false);
    }
  };

  const handleRefineContent = async () => {
    if (!editForm.content) return;
    setIsRefining(true);
    try {
        const res = await refineMarketingContentAction(editForm.content, editForm.platform || 'GENERAL');
        if (res.success && res.refinedContent) {
            setEditForm({ ...editForm, content: res.refinedContent });
            toast.success("Texte amélioré !");
        }
    } catch (err) {
        toast.error("Échec de l'amélioration");
    } finally {
        setIsRefining(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
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

  return (
    <div className="flex gap-6 h-[800px] animate-in fade-in duration-500 text-left">
      
      {/* 1. LEFT SIDEBAR: LIST OF POSTS */}
      <div className="w-80 flex flex-col gap-4">
        <div className="space-y-3">
            <Button 
                onClick={handleStartManual}
                className="w-full h-12 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[10px] tracking-widest gap-3 shadow-lg shadow-purple-200"
            >
                <PlusCircle className="w-4 h-4" /> Créer un post
            </Button>
            
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <Input 
                    placeholder="Rechercher..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 h-10 bg-white border-slate-200 rounded-xl text-[11px] font-bold uppercase tracking-tight focus:ring-purple-500/20"
                />
            </div>
        </div>

        <div className="flex-1 bg-white border border-slate-200 rounded-[2rem] overflow-hidden flex flex-col shadow-sm">
            <div className="p-2 border-b border-slate-100 bg-slate-50/50">
                <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)} className="w-full">
                    <TabsList className="grid grid-cols-3 bg-transparent h-8 p-0 gap-1">
                        <TabsTrigger value="DRAFT" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Brouillons</TabsTrigger>
                        <TabsTrigger value="PUBLISHED" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Publiés</TabsTrigger>
                        <TabsTrigger value="TRASH" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Corbeille</TabsTrigger>
                    </TabsList>
                </Tabs>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
                {filteredComms.length > 0 ? (
                    filteredComms.map((comm) => (
                        <div 
                            key={comm.id}
                            onClick={() => {
                                setSelectedId(comm.id);
                                setEditingId(null);
                            }}
                            className={cn(
                                "p-3 rounded-2xl border transition-all cursor-pointer group relative overflow-hidden",
                                selectedId === comm.id 
                                    ? "bg-purple-50 border-purple-200 ring-1 ring-purple-200" 
                                    : "bg-white border-slate-100 hover:border-purple-200 hover:bg-slate-50"
                            )}
                        >
                            <div className="flex items-center gap-2 mb-1.5">
                                {comm.platform === 'TIKTOK' && <Music className="w-3 h-3 text-pink-500" />}
                                {comm.platform === 'INSTAGRAM' && <Instagram className="w-3 h-3 text-purple-500" />}
                                {comm.platform === 'X' && <Twitter className="w-3 h-3 text-blue-400" />}
                                <span className="text-[8px] font-black uppercase text-slate-400">{comm.platform}</span>
                            </div>
                            <p className="text-[10px] font-black text-slate-900 uppercase truncate">{comm.title}</p>
                            <p className="text-[9px] text-slate-500 line-clamp-1 italic mt-0.5">{comm.content}</p>
                            
                            {comm.image_url && (
                                <div className="absolute right-2 bottom-2">
                                    <div className="w-6 h-6 rounded-lg border border-white shadow-sm overflow-hidden">
                                        <img src={comm.image_url} alt="mini" className="w-full h-full object-cover" />
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="h-40 flex flex-col items-center justify-center opacity-20 italic">
                        <Inbox className="w-8 h-8 mb-2" />
                        <p className="text-[9px] font-black uppercase">Aucun post</p>
                    </div>
                )}
            </div>
        </div>
      </div>

      {/* 2. MAIN WORKSPACE: EDITOR OR GENERATOR */}
      <div className="flex-1 flex flex-col gap-6">
        
        {editingId ? (
            /* --- MODE ÉDITION --- */
            <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-600 rounded-xl text-white shadow-lg shadow-purple-200">
                            <Edit3 className="w-5 h-5" />
                        </div>
                        <div>
                            <h4 className="text-sm font-black uppercase text-slate-900">Éditeur de Publication</h4>
                            <p className="text-[10px] font-bold text-purple-600 uppercase tracking-widest">Contenu en cours de rédaction</p>
                        </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => setEditingId(null)} className="rounded-full hover:bg-slate-100">
                        <X className="w-5 h-5" />
                    </Button>
                </div>

                <div className="flex-1 p-8 overflow-y-auto custom-scrollbar space-y-6">
                    <div className="grid grid-cols-12 gap-6">
                        <div className="col-span-8 space-y-4">
                            <div className="space-y-1.5">
                                <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Titre de la campagne</label>
                                <Input 
                                    value={editForm.title || ""} 
                                    onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                                    className="h-12 bg-slate-50 border-slate-200 font-black uppercase text-sm rounded-xl focus:ring-purple-500/20"
                                    placeholder="Ex: PROMO WEEKEND DAKAR"
                                />
                            </div>
                            <div className="space-y-1.5 relative">
                                <div className="flex justify-between items-center mb-1">
                                    <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Légende / Texte du post</label>
                                    <Button 
                                        variant="ghost" 
                                        size="sm" 
                                        onClick={handleRefineContent}
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
                                    className="min-h-[300px] bg-slate-50 border-slate-200 leading-relaxed text-sm p-6 rounded-2xl resize-none focus:ring-purple-500/20"
                                    placeholder="Écrivez votre message ici..."
                                />
                            </div>
                        </div>

                        <div className="col-span-4 space-y-6">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black uppercase text-slate-400 pl-1">Plateforme cible</label>
                                <div className="grid grid-cols-1 gap-2">
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
                                            <p.icon className="w-4 h-4" />
                                            <span className="text-[10px] font-black uppercase">{p.label}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="p-6 bg-slate-50 rounded-[2rem] border border-dashed border-slate-200 space-y-4 text-center">
                                <label className="text-[10px] font-black uppercase text-slate-400">Visuel & Média</label>
                                {editForm.image_url ? (
                                    <div className="relative aspect-square rounded-2xl overflow-hidden shadow-lg group">
                                        <img src={editForm.image_url} alt="Preview" className="w-full h-full object-cover" />
                                        <button 
                                            onClick={() => setEditForm({...editForm, image_url: null})}
                                            className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                ) : (
                                    <div 
                                        onClick={() => fileInputRef.current?.click()}
                                        className="aspect-square bg-white border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-slate-100 hover:border-purple-300 transition-all"
                                    >
                                        {isUploading ? <Loader2 className="w-6 h-6 animate-spin text-purple-600" /> : <Paperclip className="w-6 h-6 text-slate-300" />}
                                        <span className="text-[9px] font-black uppercase text-slate-400">Ajouter Photo/PDF</span>
                                    </div>
                                )}
                                <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*,application/pdf" />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-6 border-t border-slate-100 bg-white">
                    <Button 
                        onClick={handleSaveEdit} 
                        disabled={isUpdating} 
                        className="w-full h-12 bg-green-600 hover:bg-green-700 text-white rounded-2xl gap-2 font-black uppercase text-[11px] shadow-lg shadow-green-100"
                    >
                        {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Enregistrer et passer en Brouillon
                    </Button>
                </div>
            </Card>
        ) : activePost ? (
            /* --- MODE APERÇU --- */
            <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
                <Card className="col-span-7 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-y-auto custom-scrollbar p-10 space-y-8 relative">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-blue-500/10 rounded-2xl text-blue-600">
                                <Send className="w-6 h-6" />
                            </div>
                            <div>
                                <h4 className="text-xl font-black uppercase text-slate-900 tracking-tight">{activePost.title}</h4>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">{activePost.platform} • {activePost.status}</p>
                            </div>
                        </div>
                        <Button variant="outline" onClick={() => handleStartEdit(activePost)} className="rounded-xl border-slate-200 font-black uppercase text-[10px] h-10 px-6 gap-2">
                            <Edit3 className="w-3.5 h-3.5" /> Éditer le post
                        </Button>
                    </div>

                    <div className="bg-slate-50 rounded-[2rem] p-8 border border-slate-100 relative">
                        <div className="absolute -top-3 -left-3 bg-blue-600 text-white p-1.5 rounded-lg shadow-lg z-10"><PlusCircle className="w-4 h-4" /></div>
                        <p className="text-base text-slate-800 leading-relaxed font-medium whitespace-pre-wrap">{activePost.content}</p>
                        
                        {activePost.hashtags && activePost.hashtags.length > 0 && (
                            <div className="mt-8 flex flex-wrap gap-2">
                                {activePost.hashtags.map((tag, i) => (
                                    <span key={i} className="text-[10px] font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">#{tag}</span>
                                ))}
                            </div>
                        )}
                    </div>

                    {activePost.visual_suggestion && !activePost.image_url && (
                        <div className="flex items-start gap-4 bg-orange-50/50 p-6 rounded-[2rem] border border-orange-100 border-l-4 border-l-orange-400">
                            <ImageIcon className="w-5 h-5 text-orange-500 shrink-0 mt-1" />
                            <p className="text-xs text-orange-800 italic leading-relaxed">
                                <strong>Idée de visuel IA :</strong> {activePost.visual_suggestion}
                            </p>
                        </div>
                    )}
                </Card>

                <div className="col-span-5 flex flex-col gap-6">
                    {activePost.image_url ? (
                        <Card className="flex-1 bg-slate-900 border-none rounded-[2.5rem] shadow-2xl overflow-hidden relative group">
                            <img src={activePost.image_url} alt="Post Visual" className="w-full h-full object-contain" />
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                                <Button size="sm" className="bg-white text-slate-900 hover:bg-white rounded-full font-black uppercase text-[10px] h-10 px-6 gap-2" asChild>
                                    <a href={activePost.image_url} target="_blank" rel="noreferrer"><ExternalLink className="w-4 h-4" /> Plein écran</a>
                                </Button>
                            </div>
                        </Card>
                    ) : (
                        <div className="flex-1 bg-slate-100 border-2 border-dashed border-slate-200 rounded-[2.5rem] flex flex-col items-center justify-center p-10 text-center gap-4 opacity-50">
                            <ImageIcon className="w-12 h-12 text-slate-300" />
                            <p className="text-xs font-black uppercase text-slate-400 tracking-widest">Aucun visuel final attaché</p>
                            <Button variant="ghost" onClick={() => handleStartEdit(activePost)} className="text-[10px] font-black uppercase text-purple-600 hover:bg-purple-50">Ajouter un média</Button>
                        </div>
                    )}
                </div>
            </div>
        ) : (
            /* --- MODE GÉNÉRATEUR IA (Default) --- */
            <Card className="flex-1 bg-white border-slate-200 rounded-[2.5rem] shadow-xl overflow-hidden flex flex-col">
                <div className="p-10 flex flex-col items-center justify-center text-center space-y-8 flex-1">
                    <div className="w-20 h-20 bg-purple-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-purple-200 animate-bounce duration-[2000ms]">
                        <Sparkles className="w-10 h-10 text-white" />
                    </div>
                    <div className="space-y-2 max-w-md">
                        <h4 className="text-2xl font-black uppercase tracking-tight text-slate-900">Générateur de Posts IA</h4>
                        <p className="text-sm font-medium text-slate-500 leading-relaxed italic">Sélectionnez un post à gauche ou utilisez le moteur IA ci-dessous pour créer du contenu viral.</p>
                    </div>

                    <div className="w-full max-w-xl grid grid-cols-3 gap-4 pt-4">
                        {platforms.map(p => (
                            <Button 
                                key={p.id}
                                variant="outline"
                                onClick={() => setSelectedPlatform(p.id)}
                                className={cn(
                                    "h-24 flex flex-col gap-2 rounded-2xl border-2 transition-all",
                                    selectedPlatform === p.id ? "bg-purple-50 border-purple-600 text-purple-700 shadow-inner" : "bg-white border-slate-100 text-slate-400 hover:border-purple-200 hover:bg-slate-50"
                                )}
                            >
                                <p.icon className="w-6 h-6" />
                                <span className="text-[10px] font-black uppercase">{p.label}</span>
                            </Button>
                        ))}
                    </div>

                    <div className="w-full max-w-xl space-y-4 pt-4">
                        <div className="relative">
                            <Target className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                            <Input 
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="Quel est le thème de votre post ?"
                                className="h-14 pl-12 bg-slate-50 border-slate-200 rounded-2xl text-sm font-medium shadow-inner focus:ring-purple-500/20"
                            />
                        </div>
                        <div className="flex gap-3">
                            <Button 
                                onClick={() => onGeneratePost(selectedPlatform, topic)}
                                disabled={!topic || isScanning}
                                className="flex-1 h-14 bg-purple-600 hover:bg-purple-700 text-white rounded-2xl gap-3 font-black uppercase text-[11px] shadow-lg shadow-purple-200"
                            >
                                {isScanning ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                                Générer via IA
                            </Button>
                            <Button 
                                onClick={() => onPromotePending(selectedPlatform)}
                                disabled={isScanning}
                                variant="outline"
                                className="h-14 px-6 rounded-2xl border-orange-200 bg-orange-50 text-orange-700 hover:bg-orange-100 gap-2 font-black uppercase text-[10px]"
                            >
                                <MapPin className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </Card>
        )}
      </div>
    </div>
  );
}
