"use client";

import { useState, useEffect, useMemo, useCallback, useTransition } from "react";
import { useRouter } from "next/navigation";
import { MarketingMessage, MessageChannel } from "@/app/marketing/types";
import { 
  createMessageDraftAction, 
  moveMessageToTrashAction, 
  updateMarketingMessageAction 
} from "@/app/marketing/actions/messaging";
import { toast } from "sonner";
import { useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";

// Sous-composants SOLID
import { MessageSidebar, MessageFolder } from "./messaging/MessageSidebar";
import { MessageList } from "./messaging/MessageList";
import { MessageViewer } from "./messaging/MessageViewer";
import { MessageCompose } from "./messaging/MessageCompose";

interface MessagingTabProps {
  messages: MarketingMessage[];
  isScanning: boolean;
  sendingMessageId: string | null;
  onScan: () => void;
  onSendMessage: (id: string) => void;
}

export function MessagingTab({ 
  messages, 
  isScanning, 
  sendingMessageId, 
  onScan, 
  onSendMessage 
}: MessagingTabProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  
  const [activeFolder, setActiveFolder] = useState<MessageFolder>('SUGGESTIONS');
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTrashing, setIsTrashing] = useState(false);

  // --- AUTO-SELECTION DEPUIS L'URL ---
  useEffect(() => {
    const msgIdFromUrl = searchParams.get("messageId");
    if (msgIdFromUrl) {
        const msg = messages.find(m => m.id === msgIdFromUrl);
        if (msg) {
            setSelectedMessageId(msgIdFromUrl);
            if (msg.status === 'DRAFT') {
                setActiveFolder(msg.is_ai_generated ? 'SUGGESTIONS' : 'DRAFTS');
            } else if (msg.status === 'SENT') {
                setActiveFolder('SENT');
            } else if (msg.status === 'TRASH') {
                setActiveFolder('TRASH');
            }
        }
    }
  }, [searchParams, messages]);

  const filteredMessages = useMemo(() => {
    return messages.filter(m => {
        if (activeFolder === 'SUGGESTIONS') return m.status === 'DRAFT' && m.is_ai_generated;
        if (activeFolder === 'DRAFTS') return m.status === 'DRAFT' && !m.is_ai_generated;
        if (activeFolder === 'SENT') return m.status === 'SENT';
        if (activeFolder === 'FAILED') return m.status === 'FAILED';
        if (activeFolder === 'TRASH') return m.status === 'TRASH';
        return false;
    });
  }, [messages, activeFolder]);

  const selectedMessage = useMemo(() => 
    messages.find(m => m.id === selectedMessageId) || null
  , [messages, selectedMessageId]);

  const folderCounts = useMemo(() => ({
    suggestions: messages.filter(m => m.status === 'DRAFT' && m.is_ai_generated).length,
    drafts: messages.filter(m => m.status === 'DRAFT' && !m.is_ai_generated).length
  }), [messages]);

  const handleCreateDraft = async (data: Partial<MarketingMessage>) => {
    if (!data.recipient_contact || !data.content || !data.channel) {
        toast.error("Veuillez remplir tous les champs obligatoires");
        return;
    }
    setIsSaving(true);
    try {
        const res = await createMessageDraftAction({
            recipient_contact: data.recipient_contact,
            recipient_name: data.recipient_name ?? undefined,
            subject: data.subject ?? (data.channel === 'WHATSAPP' ? 'WhatsApp' : 'Sans objet'),
            content: data.content,
            category: data.category || 'GENERAL',
            channel: data.channel,
            is_ai_generated: false,
            image_url: data.image_url ?? undefined
        });
        if (res.success) {
            toast.success("Brouillon créé !");
            setIsComposeOpen(false);
            
            // On mémorise l'ID pour le sélectionner après le refresh
            if (res.id) {
                console.log("[MessagingTab] Draft created with ID:", res.id);
                localStorage.setItem('lastCreatedDraftId', res.id as string);
                setSelectedMessageId(res.id as string);
            }
            
            setActiveFolder('DRAFTS');
            startTransition(() => {
                router.refresh();
            });
        } else {
            console.error("[MessagingTab] Creation failed:", res.message);
            toast.error(res.message || "Échec de création");
        }
    } catch (err) {
        console.error("[MessagingTab] Exception during creation:", err);
        toast.error("Erreur de sauvegarde");
    } finally {
        setIsSaving(false);
    }
  };

  // Sélection automatique du dernier brouillon après refresh
  useEffect(() => {
    const lastId = localStorage.getItem('lastCreatedDraftId');
    if (lastId && messages.some(m => m.id === lastId)) {
        setSelectedMessageId(lastId);
        setActiveFolder('DRAFTS');
        localStorage.removeItem('lastCreatedDraftId');
    }
  }, [messages]);

  const handleUpdateMessage = async (id: string, data: Partial<MarketingMessage>) => {
    setIsSaving(true);
    try {
        const res = await updateMarketingMessageAction(id, data);
        if (res.success) {
          toast.success("Mis à jour !");
          startTransition(() => {
            router.refresh();
          });
        }
    } catch (err) {
        toast.error("Erreur");
    } finally {
        setIsSaving(false);
    }
  };

  const handleTrashMessage = async (id: string) => {
    setIsTrashing(true);
    try {
        const res = await moveMessageToTrashAction(id);
        if (res.success) {
            toast.success("Corbeille !");
            setSelectedMessageId(null);
            startTransition(() => {
                router.refresh();
            });
        }
    } catch (err) {
        toast.error("Erreur");
    } finally {
        setIsTrashing(false);
    }
  };

  const handleConvertToDraft = async (id: string) => {
    setIsSaving(true);
    try {
        const res = await updateMarketingMessageAction(id, { is_ai_generated: false });
        if (res.success) {
            toast.success("Converti !");
            setActiveFolder('DRAFTS');
            setTimeout(() => setSelectedMessageId(id), 200);
            startTransition(() => {
                router.refresh();
            });
        }
    } catch (err) {
        toast.error("Erreur");
    } finally {
        setIsSaving(false);
    }
  };

  // Mobile: viewer replaces sidebar+list
  const isViewerActive = !!selectedMessage;

  const handleMobileBack = useCallback(() => {
    setSelectedMessageId(null);
  }, []);

  return (
    <div className="flex flex-col lg:flex-row flex-nowrap gap-4 lg:gap-6 h-full lg:h-[calc(100vh-250px)] min-h-0 animate-in fade-in duration-500 overflow-hidden">

      {/* LEFT COLUMN: Sidebar + List stacked (fixed height, internal scroll for list) */}
      <div className={cn(
        "flex-none flex flex-col gap-4 lg:w-[320px] h-full overflow-hidden",
        isViewerActive ? 'hidden lg:flex' : 'flex'
      )}>
        <div className="flex-none">
          <MessageSidebar
            activeFolder={activeFolder}
            setActiveFolder={setActiveFolder}
            onCompose={() => setIsComposeOpen(true)}
            onScan={onScan}
            isScanning={isScanning}
            counts={folderCounts}
          />
        </div>
        <div className="flex-1 min-h-0">
          <MessageList
            messages={filteredMessages}
            selectedId={selectedMessageId}
            onSelect={setSelectedMessageId}
            activeFolder={activeFolder}
          />
        </div>
      </div>

      {/* RIGHT COLUMN: Viewer (Independent scroll) */}
      <div className={cn(
        "flex-1 min-w-0 h-full overflow-hidden",
        !isViewerActive && "hidden lg:block"
      )}>
        {(selectedMessage || isPending) && (
          <div className={cn(isPending && "opacity-50 pointer-events-none transition-opacity")}>
            {selectedMessage && (
              <MessageViewer
                  message={selectedMessage}
                  onClose={() => setSelectedMessageId(null)}
                  onUpdate={handleUpdateMessage}
                  onTrash={handleTrashMessage}
                  onConvertToDraft={handleConvertToDraft}
                  onSend={onSendMessage}
                  isSaving={isSaving || isPending}
                  isTrashing={isTrashing}
                  sendingMessageId={sendingMessageId}
                  onMobileBack={handleMobileBack}
              />
            )}
          </div>
        )}
      </div>

      <MessageCompose
        isOpen={isComposeOpen}
        onOpenChange={setIsComposeOpen}
        onSave={handleCreateDraft}
        isSaving={isSaving || isPending}
      />
    </div>
  );
}
