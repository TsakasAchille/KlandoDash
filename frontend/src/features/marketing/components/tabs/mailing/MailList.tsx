"use client";

import { cn } from "@/lib/utils";
import { Search, Filter, Mail, CheckCircle2, Inbox } from "lucide-react";
import { MarketingEmail } from "../../../types";

interface MailListProps {
  emails: MarketingEmail[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  activeFolder: string;
}

export function MailList({ emails, selectedId, onSelect, activeFolder }: MailListProps) {
  return (
    <div className={cn(
      "flex-1 bg-white border border-slate-200 rounded-[2rem] overflow-hidden shadow-xl flex flex-col transition-all duration-500",
      selectedId ? "flex-[0.4]" : "flex-1"
    )}>
      <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between text-left">
        <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-600 pl-2">{activeFolder}</h3>
        <div className="flex items-center gap-2 pr-2">
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <Filter className="w-3.5 h-3.5 text-slate-400" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {emails.length > 0 ? (
          emails.map((email) => (
            <div 
              key={email.id}
              onClick={() => onSelect(email.id)}
              className={cn(
                "flex items-center gap-4 px-6 py-4 border-b border-slate-50 cursor-pointer transition-all hover:bg-slate-50 group text-left",
                selectedId === email.id ? "bg-purple-50/50 border-l-4 border-l-purple-600" : ""
              )}
            >
              <div className="flex-shrink-0">
                {email.status === 'SENT' ? <CheckCircle2 className="w-4 h-4 text-green-600" /> : <Mail className="w-4 h-4 text-slate-400 group-hover:text-purple-600" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-baseline mb-0.5">
                  <span className="text-xs font-black text-slate-900 uppercase truncate pr-4">
                    {email.recipient_name || email.recipient_email.split('@')[0]}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 tabular-nums">
                    {new Date(email.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                  </span>
                </div>
                <p className="text-[11px] font-bold text-slate-700 truncate">{email.subject}</p>
                <p className="text-[10px] text-slate-500 truncate mt-0.5">{email.content.substring(0, 60)}...</p>
              </div>
            </div>
          ))
        ) : (
          <div className="h-full flex flex-col items-center justify-center opacity-40 italic text-slate-400">
            <Inbox className="w-12 h-12 mb-4" />
            <p className="text-[10px] font-black uppercase tracking-widest text-center">Dossier vide</p>
          </div>
        )}
      </div>
    </div>
  );
}
