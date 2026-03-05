"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { MessagingTab } from "@/features/marketing/components/tabs/MessagingTab";
import { MarketingMessage } from "@/app/marketing/types";
import { generateMessagingSuggestionsAction, sendMessageAction } from "@/app/marketing/actions/messaging";
import { MessageCircle } from "lucide-react";

interface MessagingClientProps {
  initialMessages: MarketingMessage[];
}

export function MessagingClient({ initialMessages }: MessagingClientProps) {
  const router = useRouter();
  const [messages, setMessages] = useState<MarketingMessage[]>(initialMessages);
  const [isScanning, setIsScanning] = useState(false);
  const [sendingId, setSendingId] = useState<string | null>(null);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  const handleScan = async () => {
    setIsScanning(true);
    try {
      const res = await generateMessagingSuggestionsAction();
      if (res.success) {
        toast.success(`${res.count} nouvelles opportunités identifiées.`);
        router.refresh();
      }
    } catch (error) {
      toast.error("Erreur lors du scan IA");
    } finally {
      setIsScanning(false);
    }
  };

  const handleSendMessage = async (id: string) => {
    setSendingId(id);
    try {
      const res = await sendMessageAction(id) as any;
      if (res.success) {
        if (res.via === 'WHATSAPP_LINK') {
          toast.success("Prêt pour WhatsApp");
        } else {
          toast.success("Email envoyé !");
        }
        router.refresh();
      } else {
        toast.error(res.message || "Échec de l'envoi");
      }
    } catch (error) {
      toast.error("Erreur lors de l'envoi");
    } finally {
      setSendingId(null);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full py-6">
      {/* Header simple pour l'espace dédié */}
      <div className="flex items-center justify-between bg-white/50 p-4 rounded-[2rem] border border-slate-200 backdrop-blur-sm shadow-sm shrink-0">
        <div className="flex items-center gap-4 pl-4">
          <div className="p-2.5 bg-green-50 rounded-2xl text-green-600 border border-green-100 shadow-sm">
            <MessageCircle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black uppercase tracking-tight text-slate-900 italic">Messagerie Directe</h1>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Email & WhatsApp Business</p>
          </div>
        </div>
        
        <div className="hidden md:flex items-center gap-6 px-8 border-l border-slate-200">
          <div className="flex flex-col">
            <span className="text-lg font-black text-slate-900 leading-none">{messages.filter(m => m.status === 'DRAFT').length}</span>
            <span className="text-[8px] font-black uppercase text-slate-400 tracking-tighter">Brouillons</span>
          </div>
          <div className="flex flex-col">
            <span className="text-lg font-black text-green-600 leading-none">{messages.filter(m => m.status === 'SENT').length}</span>
            <span className="text-[8px] font-black uppercase text-slate-400 tracking-tighter">Envoyés</span>
          </div>
        </div>
      </div>

      <div className="flex-1 min-h-0">
        <MessagingTab 
          messages={messages}
          isScanning={isScanning}
          sendingMessageId={sendingId}
          onScan={handleScan}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
}
