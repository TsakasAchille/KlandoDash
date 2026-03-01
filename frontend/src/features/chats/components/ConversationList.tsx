"use client";

import { Conversation } from "@/types/chat";
import { cn } from "@/lib/utils";
import { MessageSquare, Car, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { fr } from "date-fns/locale";

interface ConversationListProps {
  conversations: Conversation[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function ConversationList({ 
  conversations, 
  selectedId, 
  onSelect 
}: ConversationListProps) {
  return (
    <div className="flex flex-col h-full bg-white border-r border-slate-200 w-80 lg:w-96 shrink-0">
      <div className="p-6 border-b border-slate-100 flex-none bg-slate-50/50">
        <h2 className="text-xl font-black uppercase tracking-tight text-slate-900 flex items-center gap-3">
          <MessageSquare className="w-6 h-6 text-purple-600" />
          Messages
        </h2>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Direct & Trajets</p>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {conversations.length > 0 ? (
          conversations.map((conv) => (
            <div
              key={conv.trip_id}
              onClick={() => onSelect(conv.trip_id)}
              className={cn(
                "p-5 border-b border-slate-50 cursor-pointer transition-all hover:bg-slate-50 group relative overflow-hidden",
                selectedId === conv.trip_id ? "bg-purple-50/50 border-l-4 border-l-purple-600" : ""
              )}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-blue-50 rounded-lg">
                    <Car className="w-3.5 h-3.5 text-blue-600" />
                  </div>
                  <span className="text-[10px] font-black uppercase text-slate-400 tracking-tighter truncate max-w-[150px]">
                    #{conv.trip_id.substring(0, 8)}
                  </span>
                </div>
                <span className="text-[9px] font-bold text-slate-400 flex items-center gap-1">
                  <Clock className="w-2.5 h-2.5" />
                  {formatDistanceToNow(new Date(conv.last_timestamp), { addSuffix: true, locale: fr })}
                </span>
              </div>

              <div className="space-y-1">
                <p className="text-xs font-black text-slate-900 uppercase truncate">
                  {conv.departure_name?.split(',')[0]} → {conv.destination_name?.split(',')[0]}
                </p>
                <p className="text-[11px] text-slate-500 line-clamp-1 italic">
                  &quot;{conv.last_message}&quot;
                </p>
              </div>

              <div className="mt-3 flex items-center gap-1.5">
                <div className="flex -space-x-2 overflow-hidden">
                  {conv.participants.slice(0, 3).map((p, i) => (
                    <div key={p.uid} className="inline-block h-6 w-6 rounded-full ring-2 ring-white bg-slate-200 overflow-hidden">
                        {p.photo_url ? (
                            <img src={p.photo_url} alt="" className="w-full h-full object-cover" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center bg-purple-100 text-[8px] font-bold text-purple-600">
                                {p.display_name?.charAt(0) || '?'}
                            </div>
                        )}
                    </div>
                  ))}
                </div>
                <div className="flex flex-col ml-1">
                    <span className="text-[9px] font-black uppercase text-slate-400">
                        {conv.participant_ids.length} participants
                    </span>
                    <p className="text-[8px] text-slate-400 truncate max-w-[150px]">
                        {conv.participants.map(p => p.display_name?.split(' ')[0]).join(', ')}
                    </p>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="h-60 flex flex-col items-center justify-center opacity-30 italic p-10 text-center">
            <MessageSquare className="w-12 h-12 mb-4 text-slate-400" />
            <p className="text-[10px] font-black uppercase tracking-widest">Aucune discussion active</p>
          </div>
        )}
      </div>
    </div>
  );
}
