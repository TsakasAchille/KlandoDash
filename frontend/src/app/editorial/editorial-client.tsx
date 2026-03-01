"use client";

import { useState, useEffect, Suspense, useTransition } from "react";
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
import { DualPaneSkeleton, CalendarSkeleton } from "@/features/editorial/components/EditorialSkeletons";

// UI / Icons
import { Button } from "@/components/ui/button";
import { 
  Megaphone, Mail, Calendar as CalendarIcon, 
  Sparkles, Loader2, PenTool, CheckCircle, 
  Clock
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { cn } from "@/lib/utils";

interface EditorialClientProps {
  initialEmails: MarketingEmail[];
  initialComms: MarketingComm[];
}

function TabStat({ icon: Icon, label, value, color }: { icon: any, label: string, value: number, color: string }) {
  return (
    <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-2 duration-500">
      <div className={cn("p-1.5 rounded-lg bg-slate-50", color.replace('text-', 'bg-') + '/10')}>
        <Icon className={cn("w-3 h-3 sm:w-3.5 sm:h-3.5", color)} />
      </div>
      <div className="text-left">
        <p className="text-[9px] sm:text-[10px] font-black leading-none">{value}</p>
        <p className="text-[7px] sm:text-[8px] font-bold text-slate-400 uppercase tracking-tighter">{label}</p>
      </div>
    </div>
  );
}

function EditorialClientContent({ 
  initialEmails, 
  initialComms
}: EditorialClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  // Tabs state from URL
  const tabParam = searchParams.get("tab") || "comm";

  // Data state
  const [emails, setEmails] = useState<MarketingEmail[]>(initialEmails);
  const [comms, setComms] = useState<MarketingComm[]>(initialComms);

  // --- STATS CALCULATIONS ---
  const commDrafts = comms.filter(c => (c.status === 'DRAFT' || c.status === 'NEW') && c.type === 'POST').length;
  const commScheduled = comms.filter(c => c.scheduled_at !== null && c.type === 'POST').length;
  const emailDrafts = emails.filter(e => e.status === 'DRAFT').length;
  const emailSent = emails.filter(e => e.status === 'SENT').length;
  const calendarTotal = comms.filter(c => c.scheduled_at !== null).length + emails.filter(e => e.status === 'SENT').length; // Simplifié pour le calendrier
  
  // Loading states
  const [isScanningMailing, setIsScanningMailing] = useState(false);
  const [isScanningComm, setIsScanningComm] = useState(false);
  const [sendingEmailId, setSendingEmailId] = useState<string | null>(null);

  // --- EFFECT: SYNC PROPS ---
  useEffect(() => { setEmails(initialEmails); }, [initialEmails]);
  useEffect(() => { setComms(initialComms); }, [initialComms]);

  // --- HANDLERS: NAVIGATION ---
  const handleTabChange = (value: string) => {
    startTransition(() => {
      const url = new URL(window.location.href);
      url.searchParams.set("tab", value);
      router.replace(url.pathname + url.search, { scroll: false });
    });
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
    <div className="flex flex-col flex-1 min-h-0 gap-4 pt-0">
      <Tabs value={tabParam} onValueChange={handleTabChange} className="flex flex-col flex-1 min-h-0 gap-4">
        {/* HEADER: TABS LIST & MAIN ACTIONS */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-2 sm:gap-4 bg-white/50 p-2 rounded-2xl sm:rounded-3xl border border-slate-200 backdrop-blur-sm shadow-sm overflow-hidden shrink-0">
          <div className="flex items-center gap-4">
            <TabsList className="bg-transparent border-none p-0 h-auto gap-1 w-full sm:w-auto">
                <TabsTrigger value="comm" className="flex-1 sm:flex-initial rounded-xl sm:rounded-2xl px-2.5 sm:px-6 py-2 sm:py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[8px] sm:text-[10px] tracking-widest gap-1 sm:gap-2">
                <Megaphone className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> Social Media
                </TabsTrigger>
                <TabsTrigger value="calendar" className="flex-1 sm:flex-initial rounded-xl sm:rounded-2xl px-2.5 sm:px-6 py-2 sm:py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[8px] sm:text-[10px] tracking-widest gap-1 sm:gap-2">
                <CalendarIcon className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> Calendrier
                </TabsTrigger>
                <TabsTrigger value="mailing" className="flex-1 sm:flex-initial rounded-xl sm:rounded-2xl px-2.5 sm:px-6 py-2 sm:py-2.5 data-[state=active]:bg-purple-600 data-[state=active]:text-white font-black uppercase text-[8px] sm:text-[10px] tracking-widest gap-1 sm:gap-2">
                <Mail className="w-3 h-3 sm:w-3.5 sm:h-3.5" /> Mailing
                </TabsTrigger>
            </TabsList>

            {/* TAB-SPECIFIC STATS */}
            <div className="hidden lg:flex items-center gap-8 px-6 py-1 border-l border-slate-200/60 ml-2">
                {tabParam === 'comm' && (
                <>
                    <TabStat icon={PenTool} label="Brouillons" value={commDrafts} color="text-purple-500" />
                    <TabStat icon={Clock} label="Planifiés" value={commScheduled} color="text-orange-500" />
                </>
                )}
                {tabParam === 'mailing' && (
                <>
                    <TabStat icon={PenTool} label="Brouillons" value={emailDrafts} color="text-purple-500" />
                    <TabStat icon={CheckCircle} label="Envoyés" value={emailSent} color="text-green-500" />
                </>
                )}
                {tabParam === 'calendar' && (
                <>
                    <TabStat icon={CalendarIcon} label="Événements" value={calendarTotal} color="text-blue-500" />
                </>
                )}
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <RefreshButton />
          </div>
        </div>

        {/* --- TABS CONTENT: SMART LOADING --- */}
        <div className="flex-1 min-h-0 relative">
          {isPending && (
            <div className="absolute inset-0 z-50 bg-slate-50/20 backdrop-blur-[2px] animate-in fade-in duration-300">
              {tabParam === 'calendar' ? <CalendarSkeleton /> : <DualPaneSkeleton />}
            </div>
          )}

          <TabsContent value="comm" className="outline-none h-full flex-1 min-h-0 m-0">
            {tabParam === "comm" && (
              <CommunicationTab
                comms={comms}
                isScanning={isScanningComm}
                onGenerateIdeas={handleCommIdeasScan}
                onGeneratePost={handleGenerateSocialPost}
                onPromotePending={handlePromotePending}
              />
            )}
          </TabsContent>

          <TabsContent value="mailing" className="outline-none h-full flex-1 min-h-0 m-0">
            {tabParam === "mailing" && (
              <MailingTab
                emails={emails}
                isScanning={isScanningMailing}
                sendingEmailId={sendingEmailId}
                onScan={handleMailingScan}
                onSendEmail={handleSendEmail}
              />
            )}
          </TabsContent>

          <TabsContent value="calendar" className="outline-none h-full flex-1 min-h-0 m-0">
            {tabParam === "calendar" && (
              <CalendarTab comms={comms} emails={emails} />
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

export function EditorialClient(props: EditorialClientProps) {
  return (
    <Suspense fallback={
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="w-10 h-10 text-klando-gold animate-spin" />
        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground animate-pulse">Chargement de l&apos;espace éditorial...</p>
      </div>
    }>
      <EditorialClientContent {...props} />
    </Suspense>
  );
}
