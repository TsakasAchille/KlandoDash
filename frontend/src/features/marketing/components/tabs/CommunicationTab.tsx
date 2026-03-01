"use client";

import { useState, useMemo, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { MarketingComm, CommPlatform, CommStatus } from "@/app/marketing/types";
import {
  trashMarketingCommAction,
  restoreMarketingCommAction,
  deleteMarketingCommAction
} from "@/app/marketing/actions/communication";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// Sous-composants SOLID
import { PostSidebar } from "./communication/PostSidebar";
import { PostList } from "./communication/PostList";
import { PostViewer } from "./communication/PostViewer";
import { PostCompose } from "./communication/PostCompose";
import { AIGenerator } from "./communication/AIGenerator";
import { CommunicationMobile } from "./communication/CommunicationMobile";

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
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<CommStatus | 'ALL'>('DRAFT');
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedPlatform, setSelectedPlatform] = useState<CommPlatform>("INSTAGRAM");
  const [topic, setTopic] = useState("");
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [mobileShowGenerator, setMobileShowGenerator] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => { setIsClient(true); }, []);

  const filteredComms = useMemo(() => {
    return comms.filter(c => {
      const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter || (statusFilter === 'DRAFT' && c.status === 'NEW');
      const matchesSearch = c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           c.content.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesStatus && matchesSearch && c.type === 'POST';
    });
  }, [comms, statusFilter, searchTerm]);

  const activePost = useMemo(() => {
    if (selectedId) return comms.find(c => c.id === selectedId) || null;
    return null;
  }, [comms, selectedId]);

  const commonProps = {
    comms,
    filteredComms,
    selectedId,
    activePost,
    statusFilter,
    setStatusFilter,
    searchTerm,
    setSearchTerm,
    selectedPlatform,
    setSelectedPlatform,
    topic,
    setTopic,
    isScanning,
    ideas: comms.filter(c => c.type === 'IDEA' && c.status !== 'TRASH'),
    onGenerateIdeas,
    onGenerate: async (forcedTopic?: string) => {
        const post = await onGeneratePost(selectedPlatform, forcedTopic || topic);
        if (post) {
          setStatusFilter('DRAFT');
          router.refresh();
          setTimeout(() => setSelectedId(post.id), 200);
          setMobileShowGenerator(false);
        }
    },
    onPromote: async () => {
        const post = await onPromotePending(selectedPlatform);
        if (post) {
          setStatusFilter('DRAFT');
          router.refresh();
          setTimeout(() => setSelectedId(post.id), 200);
          setMobileShowGenerator(false);
        }
    },
    onSelect: (id: string) => { setSelectedId(id || null); setMobileShowGenerator(false); },
    onCompose: () => setIsComposeOpen(true),
    onTrash: async (id: string) => {
        const res = await trashMarketingCommAction(id);
        if (res.success) { 
          toast.success("Placé dans la corbeille"); 
          setSelectedId(null);
          router.refresh();
        }
    },
    onRestore: async (id: string) => {
        const res = await restoreMarketingCommAction(id);
        if (res.success) { 
          toast.success("Restauré"); 
          setStatusFilter('DRAFT'); 
          router.refresh();
          setTimeout(() => setSelectedId(id), 200); 
        }
    },
    onDeletePerm: async (id: string) => {
        if (!confirm("Supprimer définitivement ?")) return;
        const res = await deleteMarketingCommAction(id);
        if (res.success) { 
          toast.success("Supprimé"); 
          setSelectedId(null);
          router.refresh();
        }
    }
  };

  if (!isClient) return null;

  return (
    <div className="w-full h-full flex flex-col min-h-0">
      
      {/* ──── VERSION DESKTOP FORCEE (Affichage uniquement si large) ──── */}
      <div className="hidden lg:flex flex-row flex-nowrap w-full h-[calc(100vh-250px)] gap-8 items-start overflow-hidden">
        
        {/* COLONNE GAUCHE (SIDEBAR + LISTE) - LARGEUR BLOQUÉE */}
        <div 
          style={{ width: '320px', minWidth: '320px', maxWidth: '320px' }}
          className="flex-none flex flex-col gap-4 h-full overflow-hidden border-r border-slate-100 pr-2"
        >
          <PostSidebar
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onCompose={() => setIsComposeOpen(true)}
            onShowGenerator={() => { setSelectedId(null); setMobileShowGenerator(false); }}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
          />
          <div className="flex-1 min-h-0 w-full overflow-hidden">
            <PostList
              comms={filteredComms}
              selectedId={selectedId}
              onSelect={(id) => setSelectedId(id)}
              statusFilter={statusFilter}
            />
          </div>
        </div>

        {/* COLONNE DROITE (VIEWER OU GÉNÉRATEUR) - OCCUPE TOUT LE RESTE */}
        <div className="flex-1 min-w-0 h-full flex flex-col overflow-hidden bg-slate-50/30 rounded-[2.5rem]">
          {selectedId && activePost ? (
            <PostViewer
              post={activePost}
              onClose={() => setSelectedId(null)}
              onTrash={commonProps.onTrash}
              onRestore={commonProps.onRestore}
              onDeletePerm={commonProps.onDeletePerm}
            />
          ) : (
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              <AIGenerator
                {...commonProps}
                onMobileBack={undefined}
              />
            </div>
          )}
        </div>
      </div>

      {/* ──── VERSION MOBILE FORCEE (Affichage uniquement si petit) ──── */}
      <div className="flex lg:hidden w-full flex-col">
        <CommunicationMobile 
            {...commonProps} 
            mobileShowGenerator={mobileShowGenerator}
            setMobileShowGenerator={setMobileShowGenerator}
            handleMobileBack={() => { setSelectedId(null); setMobileShowGenerator(false); }}
        />
      </div>

      <PostCompose
        isOpen={isComposeOpen}
        onOpenChange={setIsComposeOpen}
        onCreated={(id) => { 
          setStatusFilter('DRAFT'); 
          router.refresh();
          setTimeout(() => setSelectedId(id), 200); 
        }}
      />
    </div>
  );
}
