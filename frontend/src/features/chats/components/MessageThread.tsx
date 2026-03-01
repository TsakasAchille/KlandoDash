"use client";

import { ChatMessage, Conversation } from "@/types/chat";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { Send, Loader2, User, ExternalLink, ChevronLeft } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";

interface MessageThreadProps {
  conversation: Conversation;
  messages: ChatMessage[];
  currentUserId?: string | null;
  onSendMessage: (text: string) => Promise<void>;
  onBack?: () => void;
  isLoading?: boolean;
}

export function MessageThread({ 
  conversation,
  messages, 
  currentUserId, 
  onSendMessage,
  onBack,
  isLoading = false
}: MessageThreadProps) {
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsGenerating] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    setIsGenerating(true);
    try {
      await onSendMessage(newMessage.trim());
      setNewMessage("");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50/30 flex-1 min-w-0">
      {/* HEADER */}
      <div className="p-4 lg:p-6 bg-white border-b border-slate-100 flex items-center justify-between shrink-0 shadow-sm">
        <div className="flex items-center gap-3 min-w-0">
          {onBack && (
            <button onClick={onBack} className="lg:hidden p-2 -ml-2 text-slate-500 hover:bg-slate-100 rounded-xl transition-colors">
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
          <div className="min-w-0">
            <h3 className="text-sm font-black uppercase text-slate-900 truncate">
              {conversation.departure_name?.split(',')[0]} → {conversation.destination_name?.split(',')[0]}
            </h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">Discussion Trajet #{conversation.trip_id.substring(0, 8)}</p>
          </div>
        </div>
        
        <Link 
          href={`/trips?id=${conversation.trip_id}`}
          className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-800 transition-all shrink-0"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Détails Trajet</span>
        </Link>
      </div>

      {/* MESSAGES LIST */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar"
      >
        {messages.map((msg, index) => {
          const isMe = msg.sender_id === currentUserId;
          const showAvatar = index === 0 || messages[index - 1].sender_id !== msg.sender_id;

          return (
            <div
              key={msg.id || index}
              className={cn(
                "flex items-start gap-3 animate-in fade-in duration-300",
                isMe ? "flex-row-reverse" : "flex-row"
              )}
            >
              {/* Avatar */}
              <div className="w-8 h-8 rounded-full bg-white border border-slate-200 shadow-sm flex-none flex items-center justify-center overflow-hidden">
                {showAvatar ? (
                  msg.sender?.photo_url ? (
                    <img src={msg.sender.photo_url} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <User className="w-4 h-4 text-slate-400" />
                  )
                ) : (
                  <div className="w-full h-full opacity-0" />
                )}
              </div>

              {/* Bubble */}
              <div className={cn(
                "max-w-[70%] space-y-1",
                isMe ? "text-right" : "text-left"
              )}>
                {showAvatar && (
                  <p className="text-[10px] font-black uppercase text-slate-400 tracking-tighter px-1">
                    {msg.sender?.display_name || "Utilisateur"}
                  </p>
                )}
                <div className={cn(
                  "p-4 rounded-2xl text-sm shadow-sm",
                  isMe 
                    ? "bg-purple-600 text-white rounded-tr-none" 
                    : "bg-white border border-slate-100 text-slate-800 rounded-tl-none"
                )}>
                  {msg.message}
                </div>
                <p className="text-[9px] font-bold text-slate-400 px-1">
                  {format(new Date(msg.timestamp), 'HH:mm', { locale: fr })}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* INPUT AREA */}
      <div className="p-6 bg-white border-t border-slate-100 flex-none shadow-[0_-4px_20px_-2px_rgba(0,0,0,0.05)]">
        <form onSubmit={handleSend} className="flex gap-3 max-w-5xl mx-auto">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Écrire votre message..."
            className="flex-1 h-12 bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:ring-2 focus:ring-purple-500/20 outline-none"
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !newMessage.trim()}
            className="w-12 h-12 bg-slate-900 text-white rounded-xl flex items-center justify-center hover:bg-slate-800 transition-colors disabled:opacity-50"
          >
            {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
