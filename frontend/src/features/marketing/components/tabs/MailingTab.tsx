"use client";

import { useState, useEffect, useMemo } from "react";
import { MarketingEmail } from "@/app/marketing/types";
import { createEmailDraftAction, moveEmailToTrashAction, updateMarketingEmailAction } from "@/app/marketing/actions/mailing";
import { toast } from "sonner";
import { useSearchParams } from "next/navigation";

// Sous-composants SOLID
import { MailSidebar, MailFolder } from "./mailing/MailSidebar";
import { MailList } from "./mailing/MailList";
import { MailViewer } from "./mailing/MailViewer";
import { MailCompose } from "./mailing/MailCompose";

interface MailingTabProps {
  emails: MarketingEmail[];
  isScanning: boolean;
  sendingEmailId: string | null;
  onScan: () => void;
  onSendEmail: (id: string) => void;
}

export function MailingTab({ 
  emails, 
  isScanning, 
  sendingEmailId, 
  onScan, 
  onSendEmail 
}: MailingTabProps) {
  const searchParams = useSearchParams();
  
  const [activeFolder, setActiveFolder] = useState<MailFolder>('SUGGESTIONS');
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(null);
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTrashing, setIsTrashing] = useState(false);

  // --- AUTO-SELECTION DEPUIS L'URL ---
  useEffect(() => {
    const mailIdFromUrl = searchParams.get("mailId");
    if (mailIdFromUrl) {
        const mail = emails.find(e => e.id === mailIdFromUrl);
        if (mail) {
            setSelectedEmailId(mailIdFromUrl);
            if (mail.status === 'DRAFT') {
                setActiveFolder(mail.is_ai_generated ? 'SUGGESTIONS' : 'DRAFTS');
            } else if (mail.status === 'SENT') {
                setActiveFolder('SENT');
            } else if (mail.status === 'TRASH') {
                setActiveFolder('TRASH');
            }
        }
    }
  }, [searchParams, emails]);

  const filteredEmails = useMemo(() => {
    return emails.filter(e => {
        if (activeFolder === 'SUGGESTIONS') return e.status === 'DRAFT' && e.is_ai_generated;
        if (activeFolder === 'DRAFTS') return e.status === 'DRAFT' && !e.is_ai_generated;
        if (activeFolder === 'SENT') return e.status === 'SENT';
        if (activeFolder === 'FAILED') return e.status === 'FAILED';
        if (activeFolder === 'TRASH') return e.status === 'TRASH';
        return false;
    });
  }, [emails, activeFolder]);

  const selectedEmail = useMemo(() => 
    emails.find(e => e.id === selectedEmailId) || null
  , [emails, selectedEmailId]);

  const folderCounts = useMemo(() => ({
    suggestions: emails.filter(e => e.status === 'DRAFT' && e.is_ai_generated).length,
    drafts: emails.filter(e => e.status === 'DRAFT' && !e.is_ai_generated).length
  }), [emails]);

  const handleCreateDraft = async (data: Partial<MarketingEmail>) => {
    if (!data.recipient_email || !data.subject || !data.content || !data.category) {
        toast.error("Veuillez remplir tous les champs obligatoires");
        return;
    }
    setIsSaving(true);
    try {
        const res = await createEmailDraftAction({
            recipient_email: data.recipient_email,
            recipient_name: data.recipient_name || undefined,
            subject: data.subject,
            content: data.content,
            category: data.category,
            is_ai_generated: false,
            image_url: data.image_url || undefined
        });
        if (res.success) {
            toast.success("Brouillon créé !");
            setIsComposeOpen(false);
            if (res.id) setSelectedEmailId(res.id as string);
            setActiveFolder('DRAFTS');
        }
    } catch (err) {
        toast.error("Erreur de sauvegarde");
    } finally {
        setIsSaving(false);
    }
  };

  const handleUpdateMail = async (id: string, data: Partial<MarketingEmail>) => {
    setIsSaving(true);
    try {
        const res = await updateMarketingEmailAction(id, data);
        if (res.success) toast.success("Mis à jour !");
    } catch (err) {
        toast.error("Erreur");
    } finally {
        setIsSaving(false);
    }
  };

  const handleTrashMail = async (id: string) => {
    setIsTrashing(true);
    try {
        const res = await moveEmailToTrashAction(id);
        if (res.success) {
            toast.success("Corbeille !");
            setSelectedEmailId(null);
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
        const res = await updateMarketingEmailAction(id, { is_ai_generated: false });
        if (res.success) {
            toast.success("Converti !");
            setActiveFolder('DRAFTS');
            setSelectedEmailId(id);
        }
    } catch (err) {
        toast.error("Erreur");
    } finally {
        setIsSaving(false);
    }
  };

  return (
    <div className="flex gap-6 h-[750px] animate-in fade-in duration-500">
      
      <MailSidebar 
        activeFolder={activeFolder}
        setActiveFolder={setActiveFolder}
        onCompose={() => setIsComposeOpen(true)}
        onScan={onScan}
        isScanning={isScanning}
        counts={folderCounts}
      />

      <MailList 
        emails={filteredEmails}
        selectedId={selectedEmailId}
        onSelect={setSelectedEmailId}
        activeFolder={activeFolder}
      />

      {selectedEmail && (
        <MailViewer 
            email={selectedEmail}
            onClose={() => setSelectedEmailId(null)}
            onUpdate={handleUpdateMail}
            onTrash={handleTrashMail}
            onConvertToDraft={handleConvertToDraft}
            onSend={onSendEmail}
            isSaving={isSaving}
            isTrashing={isTrashing}
            sendingEmailId={sendingEmailId}
        />
      )}

      <MailCompose 
        isOpen={isComposeOpen}
        onOpenChange={setIsComposeOpen}
        onSave={handleCreateDraft}
        isSaving={isSaving}
      />
    </div>
  );
}
