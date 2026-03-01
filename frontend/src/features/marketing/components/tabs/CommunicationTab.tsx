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
import { PenLine } from "lucide-react";

// Sous-composants SOLID
import { PostSidebar } from "./communication/PostSidebar";
import { PostList } from "./communication/PostList";
import { PostViewer } from "./communication/PostViewer";
import { PostCompose } from "./communication/PostCompose";
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
  const [isComposeOpen, setIsComposeOpen] = useState(false);
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
    onSelect: (id: string) => { setSelectedId(id || null); },
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
      
      {/* ──── VERSION DESKTOP FORCEE ──── */}
      <div className="hidden lg:flex flex-row w-full h-full gap-8 items-start overflow-hidden border-2 border-transparent">
        
        {/* COLONNE GAUCHE (SIDEBAR + LISTE) */}
        <div 
          style={{ width: '320px', minWidth: '320px', maxWidth: '320px' }}
          className="flex-none flex flex-col gap-4 h-full overflow-hidden border-r border-slate-100 pr-2"
        >
          <PostSidebar
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onCompose={() => setIsComposeOpen(true)}
            onShowGenerator={() => {}} // Not used anymore
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

        {/* COLONNE DROITE (VIEWER) */}
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
            <div className="flex-1 flex flex-col items-center justify-center p-10 text-center space-y-4 opacity-40">
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center">
                <PenLine className="w-8 h-8 text-slate-400" />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-black uppercase tracking-widest text-slate-900">Espace de Production</p>
                <p className="text-[10px] font-medium text-slate-500 italic max-w-xs mx-auto">Sélectionnez une publication à gauche pour l&apos;éditer ou cliquez sur &quot;Nouveau Post&quot; pour commencer.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ──── VERSION MOBILE FORCEE ──── */}
      <div className="flex lg:hidden w-full flex-col">
        <CommunicationMobile 
            {...commonProps} 
            handleMobileBack={() => { setSelectedId(null); }}
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
