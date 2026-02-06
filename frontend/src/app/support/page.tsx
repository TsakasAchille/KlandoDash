import {
  getTicketsWithUser,
  getTicketDetail,
  getSupportStats,
} from "@/lib/queries/support";
import { SupportPageClient } from "./support-client";
import { LifeBuoy, CircleDot, Clock, CheckCircle } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function SupportPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  // Pre-fetch selected ticket if ID in URL
  const [tickets, stats, selectedTicketData] = await Promise.all([
    getTicketsWithUser({ limit: 100 }),
    getSupportStats(),
    selected ? getTicketDetail(selected) : null,
  ]);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <LifeBuoy className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Support Technique</h1>
        </div>
        <RefreshButton />
      </div>

      {/* Stats responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <div className="flex flex-wrap gap-2">
          <div className="px-3 py-1 rounded-full bg-secondary flex items-center gap-2">
            <span className="text-muted-foreground text-xs sm:text-sm">Total:</span>
            <span className="font-semibold text-xs sm:text-sm">{stats.total}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 flex items-center gap-2">
            <CircleDot className="w-3 h-3" />
            <span className="text-xs sm:text-sm">Ouverts: {stats.open}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center gap-2">
            <Clock className="w-3 h-3" />
            <span className="text-xs sm:text-sm">En attente: {stats.pending}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 flex items-center gap-2">
            <CheckCircle className="w-3 h-3" />
            <span className="text-xs sm:text-sm">Fermés: {stats.closed}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <SupportPageClient
        tickets={tickets}
        initialSelectedId={selected || null}
        initialSelectedTicket={selectedTicketData}
      />
    </div>
  );
}
