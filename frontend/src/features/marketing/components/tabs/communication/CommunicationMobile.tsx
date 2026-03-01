"use client";

import { MarketingComm, CommPlatform } from "@/app/marketing/types";
import { PostSidebar } from "./PostSidebar";
import { PostList } from "./PostList";
import { PostViewer } from "./PostViewer";
import { AIGenerator } from "./AIGenerator";
import { cn } from "@/lib/utils";

interface CommunicationMobileProps {
  filteredComms: MarketingComm[];
  selectedId: string | null;
  activePost: MarketingComm | null;
  statusFilter: any;
  setStatusFilter: (v: any) => void;
  searchTerm: string;
  setSearchTerm: (v: string) => void;
  selectedPlatform: CommPlatform;
  setSelectedPlatform: (p: CommPlatform) => void;
  topic: string;
  setTopic: (t: string) => void;
  isScanning: boolean;
  ideas: MarketingComm[];
  onGenerateIdeas: () => void;
  onGenerate: () => void;
  onPromote: () => void;
  onSelect: (id: string) => void;
  onCompose: () => void;
  onTrash: (id: string) => void;
  onRestore: (id: string) => void;
  onDeletePerm: (id: string) => void;
  mobileShowGenerator: boolean;
  setMobileShowGenerator: (v: boolean) => void;
  handleMobileBack: () => void;
}

export function CommunicationMobile({
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
  ideas,
  onGenerateIdeas,
  onGenerate,
  onPromote,
  onSelect,
  onCompose,
  onTrash,
  onRestore,
  onDeletePerm,
  mobileShowGenerator,
  setMobileShowGenerator,
  handleMobileBack
}: CommunicationMobileProps) {
  
  // Sur mobile, on est soit en mode liste, soit en mode détail (Post ou Générateur)
  const isDetailActive = !!(selectedId || mobileShowGenerator);

  return (
    <div className="flex flex-col gap-4 animate-in fade-in duration-500">
      {/* MODE LISTE */}
      {!isDetailActive && (
        <div className="flex flex-col gap-4">
          <PostSidebar
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onCompose={onCompose}
            onShowGenerator={() => setMobileShowGenerator(true)}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
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

      {/* MODE DÉTAIL (GÉNÉRATEUR) */}
      {mobileShowGenerator && !selectedId && (
        <AIGenerator
          selectedPlatform={selectedPlatform}
          setSelectedPlatform={setSelectedPlatform}
          topic={topic}
          setTopic={setTopic}
          onGenerate={onGenerate}
          onPromote={onPromote}
          isScanning={isScanning}
          ideas={ideas}
          onGenerateIdeas={onGenerateIdeas}
          onUseTheme={(theme) => setTopic(theme)}
          onMobileBack={handleMobileBack}
        />
      )}
    </div>
  );
}
