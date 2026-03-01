"use client";

import { useState, useEffect, useRef } from "react";
import { InternalMessage } from "@/types/chat";
import { sendInternalMessageAction } from "./actions";
import { getInternalMessages } from "@/lib/queries/chats/get-chats";
import { supabase } from "@/lib/supabase";
import { useSession } from "next-auth/react";
import { Send, Loader2, User, Shield, TrendingUp, LifeBuoy, Sparkles } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { cn } from "@/lib/utils";

interface ChatsClientProps {
  initialMessages: InternalMessage[];
}

export function ChatsClient({ initialMessages }: ChatsClientProps) {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<InternalMessage[]>(initialMessages);
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Real-time subscription
  useEffect(() => {
    const channel = supabase
      .channel('internal_chat')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'dash_internal_messages' },
        async () => {
          const fresh = await getInternalMessages();
          setMessages(fresh);
        }
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    setIsSending(true);
    try {
      await sendInternalMessageAction(newMessage.trim());
      setNewMessage("");
    } finally {
      setIsSending(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Shield className="w-3 h-3 text-klando-gold" />;
      case 'marketing': return <TrendingUp className="w-3 h-3 text-purple-500" />;
      case 'support': return <LifeBuoy className="w-3 h-3 text-blue-500" />;
      case 'ia': return <Sparkles className="w-3 h-3 text-emerald-500" />;
      default: return <User className="w-3 h-3 text-slate-400" />;
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden shadow-xl animate-in fade-in duration-500">
      
      {/* CHANNEL HEADER */}
      <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-black">#</div>
            <div className="text-left">
                <h3 className="text-sm font-black uppercase text-slate-900 tracking-tight">Salon Général</h3>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">Coordination de l&apos;équipe Klando</p>
            </div>
        </div>
      </div>

      {/* MESSAGES LIST */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30 custom-scrollbar">
        {messages.map((msg, index) => {
          const isMe = msg.sender_email === session?.user?.email;
          const showSender = index === 0 || messages[index - 1].sender_email !== msg.sender_email;

          return (
            <div key={msg.id} className={cn("flex items-start gap-3", isMe ? "flex-row-reverse" : "flex-row")}>
              <div className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0">
                {getRoleIcon(msg.sender?.role || '')}
              </div>
              
              <div className={cn("max-w-[70%] space-y-1", isMe ? "text-right" : "text-left")}>
                {showSender && (
                  <p className="text-[10px] font-black uppercase text-slate-400 tracking-tighter px-1 flex items-center gap-1.5 justify-inherit">
                    {isMe ? 'Moi' : msg.sender_email.split('@')[0]}
                    <span className="opacity-50">•</span>
                    <span className="text-[8px] opacity-70">{msg.sender?.role}</span>
                  </p>
                )}
                <div className={cn(
                  "p-4 rounded-2xl text-sm shadow-sm leading-relaxed",
                  isMe ? "bg-slate-900 text-white rounded-tr-none" : "bg-white border border-slate-100 text-slate-800 rounded-tl-none"
                )}>
                  {msg.content}
                </div>
                <p className="text-[9px] font-bold text-slate-400 px-1 tabular-nums">
                  {format(new Date(msg.created_at), 'HH:mm', { locale: fr })}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* INPUT AREA */}
      <div className="p-6 bg-white border-t border-slate-100 shrink-0">
        <form onSubmit={handleSend} className="flex gap-3 max-w-5xl mx-auto">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Discuter avec l'équipe..."
            className="flex-1 h-12 bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !newMessage.trim()}
            className="w-12 h-12 bg-purple-600 text-white rounded-xl flex items-center justify-center hover:bg-purple-700 transition-all disabled:opacity-50 shadow-lg shadow-purple-200 active:scale-95"
          >
            {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
