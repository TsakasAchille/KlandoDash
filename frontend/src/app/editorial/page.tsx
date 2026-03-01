import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingEmailsAction } from "@/app/marketing/actions/mailing";
import { getMarketingCommAction } from "@/app/marketing/actions/communication";
import { EditorialClient } from "./editorial-client";
import { PenTool, CheckCircle, Calendar as CalendarIcon, Hash } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MarketingEmail, MarketingComm } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ 
    tab?: string;
  }>;
}

export default async function EditorialPage({ searchParams }: Props) {
  const { tab = "comm" } = await searchParams;
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) {
    redirect("/login");
  }

  // On récupère toujours les deux pour les stats du header, 
  // mais on pourrait optimiser ici plus tard avec une requête de comptage légère.
  const [emailResult, commResult] = await Promise.all([
    getMarketingEmailsAction(),
    getMarketingCommAction()
  ]);

  const emails = (emailResult.success ? emailResult.data : []) as MarketingEmail[];
  const comms = (commResult.success ? commResult.data : []) as MarketingComm[];

  // Stats
  const draftsCount = emails.filter(e => e.status === 'DRAFT').length + comms.filter(c => (c.status === 'DRAFT' || c.status === 'NEW') && c.type === 'POST').length;
  const sentCount = emails.filter(e => e.status === 'SENT').length;
  const scheduledCount = comms.filter(c => c.scheduled_at !== null).length;

  return (
    <div className="max-w-[1600px] mx-auto flex flex-col h-[calc(100vh-3rem)] px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* HEADER ULTRA COMPACT (No Title) */}
      <div className="flex items-center justify-between gap-4 border-b border-border/40 pb-4 bg-background/95 backdrop-blur z-30 mb-4 shrink-0">
        <div className="flex items-center gap-6">
            {/* MINI STATS INLINE */}
            <div className="flex items-center gap-6">
                <HeaderStat icon={PenTool} label="Brouillons" value={draftsCount} color="text-purple-500" />
                <HeaderStat icon={CalendarIcon} label="Planifiés" value={scheduledCount} color="text-orange-500" />
                <HeaderStat icon={CheckCircle} label="Mails" value={sentCount} color="text-green-500" />
            </div>
        </div>

        <div className="flex items-center gap-3">
            <RefreshButton />
        </div>
      </div>

      <EditorialClient
        initialEmails={emails}
        initialComms={comms}
      />
    </div>
  );
}

interface HeaderStatProps {
  icon: React.ElementType;
  label: string;
  value: number;
  color: string;
}

function HeaderStat({ icon: Icon, label, value, color }: HeaderStatProps) {
    return (
        <div className="flex items-center gap-2">
            <div className={cn("p-1.5 rounded-lg bg-slate-50", color.replace('text-', 'bg-') + '/10')}>
                <Icon className={cn("w-3.5 h-3.5", color)} />
            </div>
            <div className="text-left">
                <p className="text-[10px] font-black leading-none">{value}</p>
                <p className="text-[8px] font-bold text-slate-400 uppercase tracking-tighter">{label}</p>
            </div>
        </div>
    );
}
