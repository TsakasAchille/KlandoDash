"use client";

import {
  Inbox, Music, Instagram, Twitter, Linkedin, MoreHorizontal
} from "lucide-react";
import { cn } from "@/lib/utils";
import { MarketingComm, CommStatus } from "@/app/marketing/types";

interface PostListProps {
  comms: MarketingComm[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  statusFilter: CommStatus | 'ALL';
}

export function PostList({ comms, selectedId, onSelect, statusFilter }: PostListProps) {
  return (
    <div className="w-full bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden flex flex-col shadow-sm h-full min-h-0">
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 text-left shrink-0">
        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-600 pl-2">
          {statusFilter === 'DRAFT' ? 'Brouillons' : statusFilter === 'PUBLISHED' ? 'Publiés' : statusFilter === 'TRASH' ? 'Corbeille' : 'Tous'}
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar p-3 space-y-2">
        {comms.length > 0 ? (
          comms.map((comm) => (
            <div
              key={comm.id}
              onClick={() => onSelect(comm.id)}
              className={cn(
                "p-4 rounded-[1.5rem] border transition-all cursor-pointer group relative overflow-hidden h-[110px] flex flex-col justify-center shrink-0 w-full max-w-full",
                selectedId === comm.id
                  ? "bg-purple-50 border-purple-200 ring-1 ring-purple-200"
                  : "bg-white border-slate-100 hover:border-purple-200 hover:bg-slate-50 shadow-sm hover:shadow-md"
              )}
            >
              {/* PLATFORM BADGE */}
              <div className="flex items-center justify-between gap-2 mb-1.5 shrink-0">
                <div className="flex items-center gap-2 min-w-0">
                  <div className={cn(
                    "p-1.5 rounded-lg shrink-0",
                    comm.platform === 'TIKTOK' ? "bg-pink-50 text-pink-500" :
                    comm.platform === 'INSTAGRAM' ? "bg-purple-50 text-purple-500" :
                    comm.platform === 'LINKEDIN' ? "bg-blue-50 text-blue-700" :
                    comm.platform === 'OTHER' ? "bg-slate-100 text-slate-600" :
                    "bg-blue-50 text-blue-400"
                  )}>
                    {comm.platform === 'TIKTOK' && <Music className="w-3 h-3" />}
                    {comm.platform === 'INSTAGRAM' && <Instagram className="w-3 h-3" />}
                    {comm.platform === 'LINKEDIN' && <Linkedin className="w-3 h-3" />}
                    {comm.platform === 'X' && <Twitter className="w-3 h-3" />}
                    {comm.platform === 'OTHER' && <MoreHorizontal className="w-3 h-3" />}
                  </div>
                  <span className="text-[9px] font-black uppercase text-slate-400 tracking-tighter truncate">{comm.platform}</span>
                </div>
                
                <span className="text-[9px] font-bold text-slate-300 tabular-nums shrink-0">
                  {new Date(comm.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                  <span className="ml-1 opacity-70">
                    {new Date(comm.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </span>
              </div>
              
              {/* TEXT CONTENT - WRAPPED WITH min-w-0 TO FORCE TRUNCATE */}
              <div className="min-w-0 w-full pr-10">
                <p className="text-[11px] font-black text-slate-900 uppercase truncate block w-full">
                  {comm.title}
                </p>
                
                <p className="text-[9px] text-slate-500 line-clamp-2 italic mt-1 leading-tight overflow-hidden whitespace-normal break-words">
                  {comm.content || "(Média uniquement)"}
                </p>
              </div>
              
              {/* IMAGE THUMBNAIL */}
              {comm.image_url && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 shrink-0">
                  <div className="w-10 h-10 rounded-xl border-2 border-white shadow-lg overflow-hidden">
                    <img src={comm.image_url} alt="mini" className="w-full h-full object-cover" />
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="h-60 flex flex-col items-center justify-center opacity-30 italic">
            <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <Inbox className="w-6 h-6 text-slate-400" />
            </div>
            <p className="text-[10px] font-black uppercase tracking-widest">Aucun post trouvé</p>
          </div>
        )}
      </div>
    </div>
  );
}
