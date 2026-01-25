import {
  getTicketsWithUser,
  getTicketDetail,
  getSupportStats,
} from "@/lib/queries/support";
import { SupportPageClient } from "./support-client";
import { LifeBuoy, CircleDot, Clock, CheckCircle } from "lucide-react";

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <LifeBuoy className="w-8 h-8 text-klando-gold" />
          <h1 className="text-3xl font-bold">Support Technique</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="px-3 py-1 rounded-full bg-secondary flex items-center gap-2">
            <span className="text-muted-foreground">Total:</span>
            <span className="font-semibold">{stats.total}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 flex items-center gap-2">
            <CircleDot className="w-3 h-3" />
            Ouverts: {stats.open}
          </div>
          <div className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 flex items-center gap-2">
            <Clock className="w-3 h-3" />
            En attente: {stats.pending}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 flex items-center gap-2">
            <CheckCircle className="w-3 h-3" />
            Fermes: {stats.closed}
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
