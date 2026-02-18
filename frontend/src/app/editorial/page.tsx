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

export default async function EditorialPage() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) {
    redirect("/login");
  }

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
    <div className="max-w-[1600px] mx-auto space-y-6 pb-10 px-4 sm:px-6 lg:px-8">
      {/* HEADER ULTRA COMPACT */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-4 bg-background/95 backdrop-blur sticky top-0 z-[100] -mx-4 px-4 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8 py-4">
        <div className="flex items-center gap-6">
            <div className="space-y-0.5 text-left">
                <h1 className="text-xl font-black tracking-tight uppercase flex items-center gap-3">
                    <PenTool className="w-6 h-6 text-purple-500" />
                    Centre Éditorial
                </h1>
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest opacity-60">Production & Planning</p>
            </div>

            {/* MINI STATS INLINE */}
            <div className="hidden lg:flex items-center gap-4 border-l border-slate-200 pl-6 ml-2">
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

function HeaderStat({ icon: Icon, label, value, color }: any) {
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
