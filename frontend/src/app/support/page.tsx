import {
  getTicketsWithUser,
  getTicketDetail,
  getSupportStats,
} from "@/lib/queries/support";
import { SupportPageClient } from "./support-client";
import { LifeBuoy, CircleDot, Clock, CheckCircle, Ticket } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function SupportPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  const [tickets, stats, selectedTicketData] = await Promise.all([
    getTicketsWithUser({ limit: 100 }),
    getSupportStats(),
    selected ? getTicketDetail(selected) : null,
  ]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <LifeBuoy className="w-8 h-8 text-klando-gold" />
            Support
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Gestion des tickets et assistance utilisateurs
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total} 
          icon={Ticket} 
          color="purple" 
        />
        <MiniStatCard 
          title="Ouverts" 
          value={stats.open} 
          icon={CircleDot} 
          color="red" 
        />
        <MiniStatCard 
          title="En attente" 
          value={stats.pending} 
          icon={Clock} 
          color="gold" 
        />
        <MiniStatCard 
          title="Fermés" 
          value={stats.closed} 
          icon={CheckCircle} 
          color="green" 
        />
      </div>

      <SupportPageClient
        tickets={tickets}
        initialSelectedId={selected || null}
        initialSelectedTicket={selectedTicketData}
      />
    </div>
  );
}