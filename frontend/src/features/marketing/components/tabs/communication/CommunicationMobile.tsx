"use client";

import { MarketingComm, CommPlatform } from "@/app/marketing/types";
import { PostSidebar } from "./PostSidebar";
import { PostList } from "./PostList";
import { PostViewer } from "./PostViewer";
import { cn } from "@/lib/utils";

interface CommunicationMobileProps {
  filteredComms: MarketingComm[];
  selectedId: string | null;
  activePost: MarketingComm | null;
  statusFilter: any;
  setStatusFilter: (v: any) => void;
  searchTerm: string;
  setSearchTerm: (v: string) => void;
  onSelect: (id: string) => void;
  onCompose: () => void;
  onTrash: (id: string) => void;
  onRestore: (id: string) => void;
  onDeletePerm: (id: string) => void;
  handleMobileBack: () => void;
  isCreating?: boolean;
}

export function CommunicationMobile({
  filteredComms,
  selectedId,
  activePost,
  statusFilter,
  setStatusFilter,
  searchTerm,
  setSearchTerm,
  onSelect,
  onCompose,
  onTrash,
  onRestore,
  onDeletePerm,
  handleMobileBack,
  isCreating = false
}: CommunicationMobileProps) {
  
  // Sur mobile, on est soit en mode liste, soit en mode détail (Post)
  const isDetailActive = !!selectedId;

  return (
    <div className="flex flex-col gap-4 animate-in fade-in duration-500">
      {/* MODE LISTE */}
      {!isDetailActive && (
        <div className="flex flex-col gap-4">
          <PostSidebar
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onCompose={onCompose}
            onShowGenerator={() => {}} // Could be enabled if needed
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            isCreating={isCreating}
          />
          <PostList
            comms={filteredComms}
            selectedId={selectedId}
            onSelect={onSelect}
            statusFilter={statusFilter}
          />
        </div>
      )}

      {/* MODE DÉTAIL (POST) */}
      {selectedId && activePost && (
        <PostViewer
          post={activePost}
          onClose={handleMobileBack}
          onTrash={onTrash}
          onRestore={onRestore}
          onDeletePerm={onDeletePerm}
          onMobileBack={handleMobileBack}
        />
      )}
    </div>
  );
}
