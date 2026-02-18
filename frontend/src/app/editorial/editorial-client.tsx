"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

// Actions & Types
import { 
  generateMailingSuggestionsAction, 
  sendMarketingEmailAction 
} from "@/app/marketing/actions/mailing";
import { 
  generateCommIdeasAction, 
  generateSocialPostAction,
  generatePendingRequestsPostAction
} from "@/app/marketing/actions/communication";
import { 
  MarketingEmail, 
  MarketingComm, 
  CommPlatform 
} from "@/app/marketing/types";

// Sub-components
import { CommunicationTab } from "@/features/marketing/components/tabs/CommunicationTab";
import { MailingTab } from "@/features/marketing/components/tabs/MailingTab";
import { CalendarTab } from "@/features/marketing/components/tabs/CalendarTab";

// UI / Icons
import { Button } from "@/components/ui/button";
import { 
  Megaphone, Mail, Calendar as CalendarIcon, 
  Sparkles, Loader2
} from "lucide-react";

interface EditorialClientProps {
  initialEmails: MarketingEmail[];
  initialComms: MarketingComm[];
}

export function EditorialClient({ 
  initialEmails, 
  initialComms
}: EditorialClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Tabs state from URL
  const tabParam = searchParams.get("tab") || "comm";

  // Data state
  const [emails, setEmails] = useState<MarketingEmail[]>(initialEmails);
  const [comms, setComms] = useState<MarketingComm[]>(initialComms);
  
  // Loading states
  const [isScanningMailing, setIsScanningMailing] = useState(false);
  const [isScanningComm, setIsScanningComm] = useState(false);
  const [sendingEmailId, setSendingEmailId] = useState<string | null>(null);

  // --- EFFECT: SYNC PROPS ---
  useEffect(() => { setEmails(initialEmails); }, [initialEmails]);
  useEffect(() => { setComms(initialComms); }, [initialComms]);

  // --- HANDLERS: NAVIGATION ---
  const handleTabChange = (value: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", value);
    router.replace(url.pathname + url.search, { scroll: false });
  };

  // --- HANDLERS: ACTIONS ---
  const handleMailingScan = async () => {
    setIsScanningMailing(true);
    const res = await generateMailingSuggestionsAction();
    if (res.success) {
      toast.success(`${res.count} nouvelles opportunités de mail identifiées.`);
      router.refresh();
    }
    setIsScanningMailing(false);
  };

  const handleCommIdeasScan = async () => {
    setIsScanningComm(true);
    const res = await generateCommIdeasAction();
    if (res.success) {
      toast.success("Nouveaux angles de communication générés.");
      router.refresh();
    }
    setIsScanningComm(false);
  };

  const handleGenerateSocialPost = async (platform: CommPlatform, topic: string) => {
    setIsScanningComm(true);
    const res = await generateSocialPostAction(platform, topic);
    if (res.success && res.post) {
      toast.success(`Publication ${platform} générée !`);
      router.refresh();
      setIsScanningComm(false);
      return res.post;
    }
    setIsScanningComm(false);
    return null;
  };

  const handlePromotePending = async (platform: CommPlatform) => {
    setIsScanningComm(true);
    const res = await generatePendingRequestsPostAction(platform);
    if (res.success && res.post) {
      toast.success(`Publication promotionnelle ${platform} générée !`);
      router.refresh();
      setIsScanningComm(false);
      return res.post;
    } else {
      toast.error(res?.message || "Échec de la génération.");
    }
    setIsScanningComm(false);
    return null;
  };

  const handleSendEmail = async (id: string) => {
    setSendingEmailId(id);
    const res = await sendMarketingEmailAction(id);
    if (res.success) {
      toast.success("Email envoyé avec succès !");
      router.refresh();
    } else {
      toast.error("Échec de l'envoi.");
    }
    setSendingEmailId(null);
  };

  return (
    <div className="space-y-8">
      <Tabs value={tabParam} onValueChange={handleTabChange} className="space-y-8">
        {/* HEADER: TABS LIST & MAIN ACTIONS */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-card/30 p-2 rounded-3xl border border-white/5 backdrop-blur-sm shadow-xl">
          <TabsList className="bg-transparent border-none p-0 h-auto gap-1">
            <TabsTrigger value="comm" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[10px] tracking-widest gap-2">
              <Megaphone className="w-3.5 h-3.5" /> Social Media
            </TabsTrigger>
            <TabsTrigger value="calendar" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[10px] tracking-widest gap-2">
              <CalendarIcon className="w-3.5 h-3.5" /> Calendrier
            </TabsTrigger>
            <TabsTrigger value="mailing" className="rounded-2xl px-6 py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[10px] tracking-widest gap-2">
              <Mail className="w-3.5 h-3.5" /> Mailing
            </TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
            {tabParam === "mailing" && (
                <Button onClick={handleMailingScan} disabled={isScanningMailing} size="sm" className="bg-purple-600 hover:bg-purple-700 text-white font-black rounded-2xl px-6 h-10 shadow-lg shadow-purple-500/20">
                    {isScanningMailing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                    Scan IA Mailing
                </Button>
            )}
          </div>
        </div>

        {/* --- TABS CONTENT --- */}

        <TabsContent value="comm" className="outline-none">
          <CommunicationTab 
            comms={comms}
            isScanning={isScanningComm}
            onGenerateIdeas={handleCommIdeasScan}
            onGeneratePost={handleGenerateSocialPost}
            onPromotePending={handlePromotePending}
          />
        </TabsContent>

        <TabsContent value="mailing" className="outline-none">
          <MailingTab 
            emails={emails}
            isScanning={isScanningMailing}
            sendingEmailId={sendingEmailId}
            onScan={handleMailingScan}
            onSendEmail={handleSendEmail}
          />
        </TabsContent>

        <TabsContent value="calendar" className="outline-none">
          <CalendarTab comms={comms} emails={emails} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
