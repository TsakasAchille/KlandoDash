"use client";

import { useState, useMemo, useEffect } from "react";
import { LayoutGrid } from "lucide-react";
import { MarketingComm, CommPlatform, CommStatus } from "@/app/marketing/types";
import { 
    updateMarketingCommAction, 
    createMarketingCommAction,
    refineMarketingContentAction,
    trashMarketingCommAction,
    restoreMarketingCommAction,
    deleteMarketingCommAction
} from "@/app/marketing/actions/communication";
import { uploadMarketingImageAction } from "@/app/marketing/actions/mailing";
import { toast } from "sonner";

// Sous-composants SOLID
import { PostList } from "./communication/PostList";
import { PostPreview } from "./communication/PostPreview";
import { PostEditor } from "./communication/PostEditor";
import { AIGenerator } from "./communication/AIGenerator";

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
  
  // Le générateur est maintenant affiché par défaut si rien n'est sélectionné
  const [showGenerator, setShowGenerator] = useState(true);
  
  const [isUpdating, setIsUpdating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [editForm, setEditForm] = useState<Partial<MarketingComm>>({});

  // Synchronisation auto : si on sélectionne un post, on cache le générateur
  useEffect(() => {
    if (selectedId || editingId) {
        setShowGenerator(false);
    }
  }, [selectedId, editingId]);

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
                setStatusFilter('DRAFT');
                setTimeout(() => setSelectedId(res.post.id), 100);
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

  const handleGenerate = async (forcedTopic?: string) => {
    const post = await onGeneratePost(selectedPlatform, forcedTopic || topic);
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

  // --- ACTIONS DE CORBEILLE ---
  const handleTrash = async (id: string) => {
    const res = await trashMarketingCommAction(id);
    if (res.success) {
        toast.success("Placé dans la corbeille");
        setSelectedId(null);
    }
  };

  const handleRestore = async (id: string) => {
    const res = await restoreMarketingCommAction(id);
    if (res.success) {
        toast.success("Restauré en brouillon");
        setStatusFilter('DRAFT');
        setTimeout(() => setSelectedId(id), 100);
    }
  };

  const handleDeletePerm = async (id: string) => {
    if (!confirm("Supprimer définitivement ce post ? Cette action est irréversible.")) return;
    const res = await deleteMarketingCommAction(id);
    if (res.success) {
        toast.success("Supprimé définitivement");
        setSelectedId(null);
    }
  };

  return (
    <div className="flex gap-6 h-[750px] animate-in fade-in duration-500 text-left">
      {/* LEFT SIDEBAR */}
      <PostList 
          comms={filteredComms}
          selectedId={selectedId}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          onSelect={(id) => { setSelectedId(id); setEditingId(null); }}
          onStartManual={handleStartManual}
          onShowGenerator={() => { setShowGenerator(true); setSelectedId(null); setEditingId(null); }}
          isGeneratorActive={showGenerator}
      />

      {/* MAIN WORKSPACE */}
      <div className="flex-1 flex flex-col gap-6">
          {editingId ? (
              <PostEditor 
                  createMode={editForm.image_url && (!editForm.content || editForm.content.length < 50) ? 'IMAGE' : 'TEXT'}
                  editForm={editForm}
                  setEditForm={setEditForm}
                  onClose={() => { setEditingId(null); }}
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
                  onTrash={handleTrash}
                  onRestore={handleRestore}
                  onDeletePerm={handleDeletePerm}
              />
          ) : (
              <AIGenerator 
                  selectedPlatform={selectedPlatform}
                  setSelectedPlatform={setSelectedPlatform}
                  topic={topic}
                  setTopic={setTopic}
                  onGenerate={() => handleGenerate()}
                  onPromote={handlePromote}
                  isScanning={isScanning}
                  ideas={ideas}
                  onGenerateIdeas={onGenerateIdeas}
                  onUseTheme={(theme) => handleGenerate(theme)}
              />
          )}
      </div>
    </div>
  );
}
