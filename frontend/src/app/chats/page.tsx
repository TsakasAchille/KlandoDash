import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getRecentConversations } from "@/lib/queries/chats/get-chats";
import { ChatsClient } from "./chats-client";

export const dynamic = "force-dynamic";

export default async function ChatsPage() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "support")) {
    redirect("/login");
  }

  const conversations = await getRecentConversations();

  return (
    <div className="max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-8 h-full flex flex-col gap-6">
      <header className="flex-none text-left">
        <h1 className="text-3xl font-black tracking-tight uppercase text-slate-900">
          Modération des Échanges
        </h1>
        <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em] mt-1">Supervision du chat inter-utilisateurs</p>
      </header>

      <div className="flex-1 min-h-0">
        <ChatsClient initialConversations={conversations} />
      </div>
    </div>
  );
}
