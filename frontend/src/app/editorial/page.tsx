import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingEmailsAction } from "@/app/marketing/actions/mailing";
import { getMarketingCommAction } from "@/app/marketing/actions/communication";
import { EditorialClient } from "./editorial-client";
import { PenTool, CheckCircle, Clock, Calendar as CalendarIcon, MessageSquare } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

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

  const emails = emailResult.success ? emailResult.data : [];
  const comms = commResult.success ? commResult.data : [];

  // Stats simplifiées pour l'éditorial
  const draftsCount = emails.filter((e: any) => e.status === 'DRAFT').length + comms.filter((c: any) => (c.status === 'DRAFT' || c.status === 'NEW') && c.type === 'POST').length;
  const sentCount = emails.filter((e: any) => e.status === 'SENT').length;
  const scheduledCount = comms.filter((c: any) => c.scheduled_at !== null).length;

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1 text-left">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <PenTool className="w-8 h-8 text-purple-500" />
            Centre Éditorial
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Production de contenu et planification des campagnes
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats Quick View */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <MiniStatCard 
          title="Brouillons" 
          value={draftsCount} 
          icon={PenTool} 
          color="purple" 
        />
        <MiniStatCard 
          title="Planifiés" 
          value={scheduledCount} 
          icon={CalendarIcon} 
          color="gold" 
        />
        <MiniStatCard 
          title="Mails Envoyés" 
          value={sentCount} 
          icon={CheckCircle} 
          color="green" 
        />
      </div>

      <EditorialClient 
        initialEmails={emails}
        initialComms={comms}
      />
    </div>
  );
}
