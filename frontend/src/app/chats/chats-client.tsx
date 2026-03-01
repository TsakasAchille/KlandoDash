"use client";

import { useState, useEffect, useMemo } from "react";
import { Conversation, ChatMessage } from "@/types/chat";
import { ConversationList } from "@/features/chats/components/ConversationList";
import { MessageThread } from "@/features/chats/components/MessageThread";
import { getChatMessages } from "@/lib/queries/chats/get-chats";
import { sendMessageAction } from "./actions";
import { supabase } from "@/lib/supabase";
import { useSession } from "next-auth/react";
import { MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatsClientProps {
  initialConversations: Conversation[];
}

export function ChatsClient({ initialConversations }: ChatsClientProps) {
  const { data: session } = useSession();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);

  const selectedConversation = useMemo(() => 
    initialConversations.find(c => c.trip_id === selectedId) || null
  , [initialConversations, selectedId]);

  // Fetch messages when selection changes
  useEffect(() => {
    if (!selectedId) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      setIsLoadingMessages(true);
      const data = await getChatMessages(selectedId);
      setMessages(data);
      setIsLoadingMessages(false);
    };

    fetchMessages();
  }, [selectedId]);

  // Real-time subscription
  useEffect(() => {
    if (!selectedId) return;

    const channel = supabase
      .channel(`chat:${selectedId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'chats',
          filter: `trip_id=eq.${selectedId}`
        },
        async () => {
          const freshMessages = await getChatMessages(selectedId);
          setMessages(freshMessages);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [selectedId]);

  const handleSendMessage = async (text: string) => {
    if (!selectedId) return;
    const res = await sendMessageAction(selectedId, text);
    if (!res.success) {
      console.error("Failed to send message:", res.error);
    }
  };

  return (
    <div className="flex h-[calc(100vh-180px)] bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden shadow-xl animate-in fade-in duration-500">
      
      {/* CONVERSATION LIST - Hidden on mobile if detail is active */}
      <div className={cn(
        "h-full lg:block",
        selectedId ? "hidden" : "block"
      )}>
        <ConversationList 
            conversations={initialConversations}
            selectedId={selectedId}
            onSelect={setSelectedId}
        />
      </div>

      {/* MESSAGE THREAD - Hidden on mobile if no detail is active */}
      <div className={cn(
        "flex-1 h-full lg:block",
        !selectedId ? "hidden" : "block"
      )}>
        {selectedId && selectedConversation ? (
            <MessageThread 
                conversation={selectedConversation}
                messages={messages}
                currentUserId={session?.user?.id}
                onSendMessage={handleSendMessage}
                onBack={() => setSelectedId(null)}
                isLoading={isLoadingMessages}
            />
        ) : (
            <div className="flex-1 h-full flex flex-col items-center justify-center bg-slate-50/30 text-slate-400 p-10 text-center gap-4">
                <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center border border-slate-100 shadow-sm">
                    <MessageSquare className="w-8 h-8 opacity-20" />
                </div>
                <div className="space-y-1">
                    <p className="text-sm font-black uppercase tracking-widest text-slate-900">Espace de Discussion</p>
                    <p className="text-xs font-medium italic opacity-60 max-w-xs mx-auto">Sélectionnez un trajet pour voir les échanges en cours entre conducteurs et passagers.</p>
                </div>
            </div>
        )}
      </div>
    </div>
  );
}
