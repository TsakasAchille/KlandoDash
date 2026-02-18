"use client";

import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { 
  Sparkles, Loader2, Megaphone, Music, Instagram, 
  Twitter, Send, Image as ImageIcon, History,
  PlusCircle, Target, ArrowRightCircle, Trash2, RotateCcw,
  Edit3, Save, X, MapPin
} from "lucide-react";
import { MarketingComm, CommPlatform, CommStatus } from "../../types";
import { updateMarketingCommAction, trashMarketingCommAction, restoreMarketingCommAction, deleteMarketingCommAction } from "../../actions/communication";
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
  const [topic, setTopic] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [statusFilter, setStatusFilter] = useState<CommStatus | 'ALL'>('NEW');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingComm>>({});

  const ideas = comms.filter(c => c.type === 'IDEA' && c.status !== 'TRASH');
  
  const filteredComms = useMemo(() => {
    return comms.filter(c => {
        if (statusFilter === 'ALL') return true;
        return c.status === statusFilter;
    });
  }, [comms, statusFilter]);

  const platforms: { id: CommPlatform; label: string; icon: any; color: string }[] = [
    { id: 'TIKTOK', label: 'TikTok', icon: Music, color: 'text-pink-500' },
    { id: 'INSTAGRAM', label: 'Instagram', icon: Instagram, color: 'text-purple-500' },
    { id: 'X', label: 'X / Twitter', icon: Twitter, color: 'text-blue-400' },
  ];

  const handleStartEdit = (comm: MarketingComm) => {
    setEditingId(comm.id);
    setEditForm({ 
        title: comm.title, 
        content: comm.content, 
        hashtags: comm.hashtags || [],
        visual_suggestion: comm.visual_suggestion || '',
        platform: comm.platform
    });
  };

  const handleSaveEdit = async () => {
    if (!editingId) return;
    setIsUpdating(true);
    try {
        const res = await updateMarketingCommAction(editingId, { ...editForm, status: 'DRAFT' });
        if (res.success) {
            toast.success("Publication mise à jour (Brouillon)");
            setEditingId(null);
        }
    } catch (err) {
        console.error(err);
        toast.error("Erreur de sauvegarde");
    } finally {
        setIsUpdating(false);
    }
  };

  const handleTrash = async (id: string) => {
    const res = await trashMarketingCommAction(id);
    if (res.success) toast.success("Placé dans la corbeille");
  };

  const handleRestore = async (id: string) => {
    const res = await restoreMarketingCommAction(id);
    if (res.success) toast.success("Restauré en brouillon");
  };

  const handleDeletePerm = async (id: string) => {
    if (!confirm("Supprimer définitivement ?")) return;
    const res = await deleteMarketingCommAction(id);
    if (res.success) toast.success("Supprimé définitivement");
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700 pb-20">
      
      {/* 1. STRATEGIC IDEAS GRID */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/10 rounded-xl">
              <Megaphone className="w-4 h-4 text-purple-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Angles de Communication ✨</h3>
          </div>
          <Button 
            onClick={onGenerateIdeas} 
            disabled={isScanning}
            size="sm"
            className="rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black text-[10px] uppercase tracking-widest gap-2 shadow-lg shadow-purple-500/20"
          >
            {isScanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            Nouveaux Angles
          </Button>
        </div>

        <div className="grid md:grid-cols-3 gap-6 text-left">
          {ideas.length > 0 ? (
            ideas.slice(0, 3).map((idea) => (
              <Card key={idea.id} className="bg-card/40 backdrop-blur-md border-white/5 hover:border-purple-500/30 transition-all duration-500 group overflow-hidden">
                <CardContent className="p-6 space-y-4">
                  <h4 className="font-black text-sm text-white uppercase group-hover:text-purple-400 transition-colors">{idea.title}</h4>
                  <p className="text-[11px] text-muted-foreground leading-relaxed">{idea.content}</p>
                  {idea.visual_suggestion && (
                    <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                        <p className="text-[9px] font-black uppercase text-purple-400 mb-1 flex items-center gap-1.5"><ImageIcon className="w-2.5 h-2.5" /> Idée Visuelle</p>
                        <p className="text-[10px] text-muted-foreground/80 italic">&quot;{idea.visual_suggestion}&quot;</p>
                    </div>
                  )}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setTopic(idea.title)}
                    className="w-full rounded-xl hover:bg-white/5 text-[10px] font-black uppercase tracking-tighter gap-2"
                  >
                    Utiliser ce thème <ArrowRightCircle className="w-3 h-3" />
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-3 py-12 bg-white/[0.02] border border-dashed border-white/5 rounded-[2rem] flex flex-col items-center justify-center opacity-30 italic text-[10px] font-black uppercase tracking-[0.2em]">
                Aucune idée générée. Cliquez sur le scan.
            </div>
          )}
        </div>
      </div>

      {/* 2. SOCIAL POST GENERATOR */}
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-2">
            <div className="p-2 bg-blue-500/10 rounded-xl">
                <PlusCircle className="w-4 h-4 text-blue-500" />
            </div>
            <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Générateur de Publications</h3>
        </div>

        <Card className="bg-slate-50 border-slate-200 rounded-[2.5rem] overflow-hidden shadow-2xl">
            <div className="grid md:grid-cols-12 h-[500px]">
                {/* Selector */}
                <div className="md:col-span-4 border-r border-slate-200 p-8 space-y-6 bg-white overflow-y-auto">
                    <div className="space-y-4">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">1. Choisir la plateforme</label>
                        <div className="grid grid-cols-1 gap-2">
                            {platforms.map((p) => (
                                <button
                                    key={p.id}
                                    onClick={() => setSelectedPlatform(p.id)}
                                    className={cn(
                                        "flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-300",
                                        selectedPlatform === p.id 
                                            ? "bg-blue-50 border-blue-200 text-blue-700 shadow-sm" 
                                            : "border-transparent text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <p.icon className={cn("w-4 h-4", selectedPlatform === p.id ? "text-blue-600" : "opacity-40")} />
                                        <span className="text-[11px] font-black uppercase tracking-widest">{p.label}</span>
                                    </div>
                                    {selectedPlatform === p.id && <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-4 pt-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">2. Action Rapide</label>
                        <Button 
                            onClick={() => onPromotePending(selectedPlatform)}
                            disabled={isScanning}
                            variant="outline"
                            className="w-full h-11 rounded-xl border-orange-200 bg-orange-50 text-orange-700 hover:bg-orange-100 gap-2 font-black uppercase text-[9px] tracking-widest"
                        >
                            {isScanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <MapPin className="w-3.5 h-3.5" />}
                            Promouvoir Trajets en attente
                        </Button>
                    </div>

                    <div className="space-y-4 pt-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-500 pl-1">3. Ou Thème libre</label>
                        <div className="relative">
                            <Input 
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="ex: Covoiturage pour le travail..."
                                className="bg-slate-50 border-slate-200 rounded-xl h-12 text-sm pl-4 pr-12 text-slate-900 outline-none focus:ring-2 focus:ring-blue-500/20 transition-all placeholder:text-slate-400 shadow-inner"
                            />
                            <Target className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/30" />
                        </div>
                    </div>

                    <Button 
                        onClick={() => onGeneratePost(selectedPlatform, topic)}
                        disabled={!topic || isScanning}
                        className="w-full h-12 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-black uppercase text-[10px] tracking-widest gap-2 shadow-lg shadow-blue-500/20 transition-all active:scale-95"
                    >
                        {isScanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                        Générer via thème
                    </Button>
                </div>

                {/* Post Display Area */}
                <div className="md:col-span-8 p-10 bg-slate-100/50 flex flex-col items-center justify-center text-left">
                    {editingId ? (
                        <div className="w-full max-w-xl space-y-4 animate-in fade-in duration-300 bg-white p-8 rounded-3xl border border-slate-200 shadow-xl">
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="text-xs font-black uppercase text-slate-900 flex items-center gap-2"><Edit3 className="w-4 h-4" /> Édition en cours</h4>
                                <Button variant="ghost" size="sm" onClick={() => setEditingId(null)} className="h-8 rounded-lg"><X className="w-4 h-4" /></Button>
                            </div>
                            <Input 
                                value={editForm.title || ""} 
                                onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                                className="bg-slate-50 border-slate-200 font-bold"
                                placeholder="Titre de la publication"
                            />
                            <Textarea 
                                value={editForm.content || ""} 
                                onChange={(e) => setEditForm({...editForm, content: e.target.value})}
                                className="min-h-[150px] bg-slate-50 border-slate-200 leading-relaxed"
                                placeholder="Corps de la publication..."
                            />
                            <Input 
                                value={editForm.visual_suggestion || ""} 
                                onChange={(e) => setEditForm({...editForm, visual_suggestion: e.target.value})}
                                className="bg-slate-50 border-slate-200 text-[10px]"
                                placeholder="Suggestion de visuel"
                            />
                            <Button onClick={handleSaveEdit} disabled={isUpdating} className="w-full h-11 bg-green-600 hover:bg-green-700 text-white rounded-xl gap-2 font-black uppercase text-[10px]">
                                {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                Enregistrer les modifications
                            </Button>
                        </div>
                    ) : comms.filter(c => c.type === 'POST').length > 0 ? (
                        <div className="w-full max-w-xl space-y-6 animate-in slide-in-from-right-4 duration-700">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-blue-500/20 rounded-lg"><Send className="w-4 h-4 text-blue-600" /></div>
                                    <h4 className="text-sm font-black text-slate-900 uppercase tracking-tight">{comms.filter(c => c.type === 'POST')[0].title}</h4>
                                </div>
                                <Button variant="outline" size="sm" onClick={() => handleStartEdit(comms.filter(c => c.type === 'POST')[0])} className="h-8 rounded-xl border-slate-200 text-slate-600 font-bold text-[9px] uppercase hover:bg-white transition-all shadow-sm">
                                    <Edit3 className="w-3 h-3 mr-2" /> Éditer
                                </Button>
                            </div>
                            <div className="bg-white border border-slate-200 rounded-3xl p-8 shadow-2xl relative">
                                <div className="absolute -top-3 -left-3 bg-blue-600 text-white p-1.5 rounded-lg shadow-lg"><PlusCircle className="w-4 h-4" /></div>
                                <p className="text-sm text-slate-800 leading-relaxed font-medium whitespace-pre-wrap">{comms.filter(c => c.type === 'POST')[0].content}</p>
                                
                                {comms.filter(c => c.type === 'POST')[0].hashtags && comms.filter(c => c.type === 'POST')[0].hashtags!.length > 0 && (
                                    <div className="mt-6 flex flex-wrap gap-2">
                                        {comms.filter(c => c.type === 'POST')[0].hashtags!.map((tag, i) => (
                                            <span key={i} className="text-[10px] font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">#{tag}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                            {comms.filter(c => c.type === 'POST')[0].visual_suggestion && (
                                <div className="flex items-start gap-3 bg-white p-4 rounded-2xl border border-slate-200 border-l-4 border-l-klando-gold shadow-sm">
                                    <ImageIcon className="w-4 h-4 text-klando-gold shrink-0 mt-0.5" />
                                    <p className="text-[10px] text-slate-500 italic leading-relaxed text-left"><strong>Idée Visuel :</strong> {comms.filter(c => c.type === 'POST')[0].visual_suggestion}</p>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center space-y-4 opacity-20">
                            <Megaphone className="w-16 h-16 mx-auto text-slate-900" />
                            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-900">Prêt à créer du contenu viral</p>
                        </div>
                    )}
                </div>
            </div>
        </Card>
      </div>

      {/* 3. MANAGEMENT TABLE */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-100 rounded-xl">
                    <History className="w-4 h-4 text-slate-600" />
                </div>
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white">Gestion des Publications</h3>
            </div>
            
            <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)} className="bg-white/5 p-1 rounded-xl border border-white/10">
                <TabsList className="bg-transparent border-none h-8">
                    <TabsTrigger value="NEW" className="text-[9px] font-black uppercase rounded-lg px-3 data-[state=active]:bg-blue-600">Nouveau</TabsTrigger>
                    <TabsTrigger value="DRAFT" className="text-[9px] font-black uppercase rounded-lg px-3 data-[state=active]:bg-purple-600">Brouillons</TabsTrigger>
                    <TabsTrigger value="PUBLISHED" className="text-[9px] font-black uppercase rounded-lg px-3 data-[state=active]:bg-green-600">Publiés</TabsTrigger>
                    <TabsTrigger value="TRASH" className="text-[9px] font-black uppercase rounded-lg px-3 data-[state=active]:bg-red-600">Corbeille</TabsTrigger>
                    <TabsTrigger value="ALL" className="text-[9px] font-black uppercase rounded-lg px-3">Tous</TabsTrigger>
                </TabsList>
            </Tabs>
        </div>
        
        <Card className="bg-white border-slate-200 rounded-[2rem] overflow-hidden shadow-xl">
            <Table>
                <TableHeader className="bg-slate-50">
                    <TableRow className="hover:bg-transparent border-slate-100">
                        <TableHead className="text-[10px] font-black uppercase text-slate-500 py-5 pl-8">Plateforme</TableHead>
                        <TableHead className="text-[10px] font-black uppercase text-slate-500">Titre / Contenu</TableHead>
                        <TableHead className="text-[10px] font-black uppercase text-slate-500">Statut</TableHead>
                        <TableHead className="text-right text-[10px] font-black uppercase text-slate-500 pr-8">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredComms.length > 0 ? (
                        filteredComms.map((comm) => (
                            <TableRow key={comm.id} className="border-slate-50 hover:bg-slate-50/50 group transition-colors">
                                <TableCell className="pl-8">
                                    <div className="flex items-center gap-3">
                                        {comm.platform === 'TIKTOK' && <Music className="w-4 h-4 text-pink-500" />}
                                        {comm.platform === 'INSTAGRAM' && <Instagram className="w-4 h-4 text-purple-500" />}
                                        {comm.platform === 'X' && <Twitter className="w-4 h-4 text-blue-400" />}
                                        {comm.platform === 'GENERAL' && <Megaphone className="w-4 h-4 text-slate-400" />}
                                        <span className="text-[10px] font-black text-slate-900 uppercase">{comm.platform}</span>
                                    </div>
                                </TableCell>
                                <TableCell className="max-w-md">
                                    <div className="flex flex-col text-left">
                                        <span className="text-xs font-black text-slate-900 uppercase truncate">{comm.title}</span>
                                        <span className="text-[10px] text-slate-400 line-clamp-1 italic">&quot;{comm.content}&quot;</span>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <span className={cn(
                                        "text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border",
                                        comm.status === 'NEW' ? "bg-blue-50 text-blue-600 border-blue-100" :
                                        comm.status === 'DRAFT' ? "bg-purple-50 text-purple-600 border-purple-100" :
                                        comm.status === 'PUBLISHED' ? "bg-green-50 text-green-600 border-green-100" :
                                        "bg-red-50 text-red-600 border-red-100"
                                    )}>
                                        {comm.status}
                                    </span>
                                </TableCell>
                                <TableCell className="text-right pr-8">
                                    <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        {comm.status === 'TRASH' ? (
                                            <>
                                                <Button size="icon" variant="ghost" onClick={() => handleRestore(comm.id)} className="h-8 w-8 text-blue-600 hover:bg-blue-50" title="Restaurer"><RotateCcw className="w-3.5 h-3.5" /></Button>
                                                <Button size="icon" variant="ghost" onClick={() => handleDeletePerm(comm.id)} className="h-8 w-8 text-red-600 hover:bg-red-50" title="Supprimer définitivement"><X className="w-3.5 h-3.5" /></Button>
                                            </>
                                        ) : (
                                            <>
                                                <Button size="icon" variant="ghost" onClick={() => handleStartEdit(comm)} className="h-8 w-8 text-purple-600 hover:bg-purple-50" title="Éditer"><Edit3 className="w-3.5 h-3.5" /></Button>
                                                <Button size="icon" variant="ghost" onClick={() => handleTrash(comm.id)} className="h-8 w-8 text-red-600 hover:bg-red-50" title="Mettre à la corbeille"><Trash2 className="w-3.5 h-3.5" /></Button>
                                            </>
                                        )}
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={4} className="h-32 text-center text-slate-300 font-black uppercase text-[10px] tracking-widest italic opacity-50">
                                Aucun contenu trouvé dans cette catégorie
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </Card>
      </div>
    </div>
  );
}
