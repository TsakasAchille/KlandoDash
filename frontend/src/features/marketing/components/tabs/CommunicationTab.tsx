"use client";

import { useState, useMemo } from "react";
import { LayoutGrid } from "lucide-react";
import { MarketingComm, CommPlatform, CommStatus } from "@/app/marketing/types";
import { 
    updateMarketingCommAction, 
    createMarketingCommAction,
    refineMarketingContentAction
} from "@/app/marketing/actions/communication";
import { uploadMarketingImageAction } from "@/app/marketing/actions/mailing";
import { toast } from "sonner";

// Sous-composants SOLID
import { PostList } from "./communication/PostList";
import { PostPreview } from "./communication/PostPreview";
import { PostEditor } from "./communication/PostEditor";
import { AIGenerator } from "./communication/AIGenerator";
import { IdeasGrid } from "./communication/IdeasGrid";

interface CommunicationTabProps {
  comms: MarketingComm[];
  isScanning: boolean;
  onGenerateIdeas: () => void;
  onGeneratePost: (platform: CommPlatform, topic: string) => Promise<MarketingComm | null>;
  onPromotePending: (platform: CommPlatform) => Promise<MarketingComm | null>;
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
  const [showGenerator, setShowGenerator] = useState(false);
  const [createMode, setCreateMode] = useState<'TEXT' | 'IMAGE' | null>(null);
  
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingComm>>({});

  // Filtrage intelligent
  const filteredComms = useMemo(() => {
    return comms.filter(c => {
        const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter || (statusFilter === 'DRAFT' && c.status === 'NEW');
        const matchesSearch = c.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                             c.content.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesStatus && matchesSearch && c.type === 'POST';
    });
  }, [comms, statusFilter, searchTerm]);

  const ideas = useMemo(() => comms.filter(c => c.type === 'IDEA' && c.status !== 'TRASH'), [comms]);

  // Post actif
  const activePost = useMemo(() => {
    if (selectedId) return comms.find(c => c.id === selectedId) || null;
    return null;
  }, [comms, selectedId]);

  const handleStartManual = (mode: 'TEXT' | 'IMAGE') => {
    setEditingId("NEW_MANUAL");
    setSelectedId(null);
    setShowGenerator(false);
    setCreateMode(mode);
    setEditForm({ 
        title: mode === 'IMAGE' ? "Nouveau Post Visuel" : "Nouvelle publication", 
        content: "", 
        hashtags: [],
        visual_suggestion: "",
        platform: 'INSTAGRAM',
        image_url: null
    });
  };

  const handleStartEdit = (comm: MarketingComm) => {
    setEditingId(comm.id);
    setShowGenerator(false);
    const isVis = !!comm.image_url && (!comm.content || comm.content.length < 50);
    setCreateMode(isVis ? 'IMAGE' : 'TEXT');
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
        const finalData = { 
            ...editForm, 
            content: createMode === 'IMAGE' ? "" : editForm.content,
            status: 'DRAFT' as CommStatus
        };

        if (editingId === "NEW_MANUAL") {
            const res = await createMarketingCommAction(finalData);
            if (res.success && res.post) {
                toast.success("Publication créée !");
                setStatusFilter('DRAFT');
                setTimeout(() => setSelectedId(res.post.id), 100);
                setEditingId(null);
                setCreateMode(null);
            }
        } else {
            const res = await updateMarketingCommAction(editingId, finalData);
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

  const handleGenerate = async () => {
    const post = await onGeneratePost(selectedPlatform, topic);
    if (post) {
        setStatusFilter('DRAFT');
        setTimeout(() => setSelectedId(post.id), 100);
        setShowGenerator(false);
    }
  };

  const handlePromote = async () => {
    const post = await onPromotePending(selectedPlatform);
    if (post) {
        setStatusFilter('DRAFT');
        setTimeout(() => setSelectedId(post.id), 100);
        setShowGenerator(false);
    }
  };

  return (
    <div className="space-y-10 pb-20">
      {/* 1. STRATEGIC IDEAS GRID (Utilise onGenerateIdeas) */}
      <IdeasGrid 
        ideas={ideas}
        isScanning={isScanning}
        onGenerateIdeas={onGenerateIdeas}
        onUseTheme={(theme) => {
            setTopic(theme);
            setShowGenerator(true);
            setSelectedId(null);
            setEditingId(null);
        }}
      />

      {/* 2. SPLIT WORKSPACE */}
      <div className="flex gap-6 h-[800px] animate-in fade-in duration-500 text-left">
        {/* LEFT SIDEBAR (PostList) */}
        <PostList 
            comms={filteredComms}
            selectedId={selectedId}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onSelect={(id) => { setSelectedId(id); setEditingId(null); setShowGenerator(false); }}
            onStartManual={handleStartManual}
            onShowGenerator={() => { setShowGenerator(true); setSelectedId(null); setEditingId(null); }}
            isGeneratorActive={showGenerator}
        />

        {/* MAIN WORKSPACE */}
        <div className="flex-1 flex flex-col gap-6">
            {editingId ? (
                <PostEditor 
                    editingId={editingId}
                    createMode={createMode}
                    editForm={editForm}
                    setEditForm={setEditForm}
                    onClose={() => { setEditingId(null); setCreateMode(null); }}
                    onSave={handleSaveEdit}
                    onRefine={handleRefineContent}
                    onFileUpload={handleFileUpload}
                    isUpdating={isUpdating}
                    isRefining={isRefining}
                    isUploading={isUploading}
                />
            ) : activePost ? (
                <PostPreview 
                    activePost={activePost}
                    onStartEdit={handleStartEdit}
                />
            ) : showGenerator ? (
                <AIGenerator 
                    selectedPlatform={selectedPlatform}
                    setSelectedPlatform={setSelectedPlatform}
                    topic={topic}
                    setTopic={setTopic}
                    onGenerate={handleGenerate}
                    onPromote={handlePromote}
                    isScanning={isScanning}
                />
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center opacity-20 text-slate-900 gap-4 bg-white border border-slate-200 rounded-[2.5rem]">
                    <LayoutGrid className="w-20 h-20" />
                    <p className="text-sm font-black uppercase tracking-[0.3em]">Sélectionnez un élément pour commencer</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
}
