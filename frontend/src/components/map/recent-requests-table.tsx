"use client";

import { SiteTripRequest } from "@/types/site-request";
import { cn } from "@/lib/utils";
import { Users, Eye, EyeOff, Calendar, Radar, Loader2, Sparkles } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

interface RecentRequestsTableProps {
  requests: SiteTripRequest[];
  selectedRequestId?: string;
  hiddenRequestIds: Set<string>;
  onSelectRequest: (request: SiteTripRequest) => void;
  onHoverRequest: (requestId: string | null) => void;
  onToggleVisibility: (requestId: string) => void;
  onScan: (requestId: string) => void;
  scanningId: string | null;
}

export function RecentRequestsTable({
  requests,
  selectedRequestId,
  hiddenRequestIds,
  onSelectRequest,
  onHoverRequest,
  onToggleVisibility,
  onScan,
  scanningId
}: RecentRequestsTableProps) {
  const formatRelativeDate = (date: string) => {
    try {
      return formatDistanceToNow(new Date(date), { addSuffix: true, locale: fr });
    } catch {
      return "récemment";
    }
  };

  return (
    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
      <div className="space-y-2">
        {requests.length === 0 ? (
          <div className="text-center py-8 opacity-40">
            <Users className="w-8 h-8 mx-auto mb-2" />
            <p className="text-[10px] font-black uppercase tracking-widest">Aucune demande</p>
          </div>
        ) : (
          requests.map((request) => {
            const isSelected = selectedRequestId === request.id;
            const isHidden = hiddenRequestIds.has(request.id);
            const hasMatches = request.matches && request.matches.length > 0;

            return (
              <div
                key={request.id}
                onMouseEnter={() => onHoverRequest(request.id)}
                onMouseLeave={() => onHoverRequest(null)}
                onClick={() => onSelectRequest(request)}
                className={cn(
                  "group relative p-3 rounded-2xl border transition-all duration-300 cursor-pointer overflow-hidden",
                  isSelected 
                    ? "bg-purple-500/10 border-purple-500/50 shadow-lg shadow-purple-500/5" 
                    : "bg-card/40 border-border/40 hover:border-purple-500/30 hover:bg-purple-500/5",
                  isHidden && "opacity-40"
                )}
              >
                {/* Status Bar */}
                <div className={cn(
                  "absolute left-0 top-0 bottom-0 w-1 transition-all",
                  isSelected ? "bg-purple-500" : "bg-purple-500/20 group-hover:bg-purple-500/40"
                )} />

                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-500">
                          <Users className="w-3 h-3" />
                        </div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-purple-500 truncate">
                          {request.contact_info}
                        </span>
                      </div>
                      
                      {hasMatches && (
                        <div className="flex items-center gap-1 text-[9px] font-black text-green-500 uppercase bg-green-500/10 px-2 py-0.5 rounded-full">
                          <Sparkles className="w-2.5 h-2.5" />
                          {request.matches?.length} matches
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-xs font-black uppercase tracking-tight text-foreground mb-1">
                      <span>{request.origin_city}</span>
                      <span className="text-purple-500/50">➜</span>
                      <span>{request.destination_city}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1 text-[10px] text-muted-foreground font-bold italic">
                        <Calendar className="w-3 h-3" />
                        {request.desired_date 
                          ? new Date(request.desired_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
                          : "ASAP"
                        }
                      </div>
                      <div className="text-[9px] text-muted-foreground/60 font-medium italic">
                        Soumis {formatRelativeDate(request.created_at)}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onScan(request.id);
                      }}
                      disabled={scanningId === request.id}
                      className={cn(
                        "p-2 rounded-xl border border-border/40 transition-all",
                        scanningId === request.id ? "bg-blue-500 text-white animate-pulse" : "bg-blue-500/10 text-blue-500 hover:bg-blue-500 hover:text-white"
                      )}
                      title="Scanner les trajets"
                    >
                      {scanningId === request.id ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Radar className="w-3.5 h-3.5" />
                      )}
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleVisibility(request.id);
                      }}
                      className="p-2 rounded-xl bg-secondary/50 hover:bg-secondary border border-border/40 transition-colors text-muted-foreground hover:text-foreground"
                    >
                      {isHidden ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Selected Indicator */}
                {isSelected && (
                  <div className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
