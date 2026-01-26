
import { cn } from "@/lib/utils";
import type { TicketStatus } from "@/types/support";
import { TICKET_STATUS_LABELS } from "@/types/support";

interface TicketStatusBadgeProps {
  status: TicketStatus;
  className?: string;
}

const statusColors: Record<TicketStatus, string> = {
  OPEN: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  CLOSED: "bg-green-500/20 text-green-400 border-green-500/30",
  PENDING: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
};

export function TicketStatusBadge({ status, className }: TicketStatusBadgeProps) {
  return (
    <span
      className={cn(
        "px-2 py-1 rounded-full text-xs font-medium border",
        statusColors[status] || "bg-gray-500/20 text-gray-400 border-gray-500/30",
        className
      )}
      
    >
      {TICKET_STATUS_LABELS[status] || status}
    </span>
  );
}
