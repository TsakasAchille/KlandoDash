import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingMessagesAction } from "@/app/marketing/actions/messaging";
import { MessagingTab } from "@/features/marketing/components/tabs/MessagingTab";
import { MarketingMessage } from "@/app/marketing/types";
import { MessageCircle, Sparkles, Send } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function MessagingPage() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) {
    redirect("/login");
  }

  const msgResult = await getMarketingMessagesAction();
  const messages = (msgResult.success ? msgResult.data : []) as MarketingMessage[];

  return (
    <div className="max-w-[1600px] mx-auto flex flex-col h-[calc(100vh-3rem)] px-4 sm:px-6 lg:px-8 pt-0 relative">
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
            isScanning={false} // Le scan peut être ajouté via une action client si besoin
            sendingMessageId={null}
            onScan={() => {}}
            onSendMessage={() => {}} // Ces handlers seront gérés par le composant lui-même ou des actions
          />
        </div>
      </div>
    </div>
  );
}
