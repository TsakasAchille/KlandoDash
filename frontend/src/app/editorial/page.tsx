import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingMessagesAction } from "@/app/marketing/actions/messaging";
import { getMarketingCommAction } from "@/app/marketing/actions/communication";
import { EditorialClient } from "./editorial-client";
import { MarketingMessage, MarketingComm } from "@/app/marketing/types";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ 
    tab?: string;
  }>;
}

export default async function EditorialPage({ searchParams }: Props) {
  const { tab = "comm" } = await searchParams;
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) {
    redirect("/login");
  }

  // On récupère toujours les deux pour les stats du header
  const [msgResult, commResult] = await Promise.all([
    getMarketingMessagesAction(),
    getMarketingCommAction()
  ]);

  const messages = (msgResult.success ? msgResult.data : []) as MarketingMessage[];
  const comms = (commResult.success ? commResult.data : []) as MarketingComm[];

  return (
    <div className="max-w-[1600px] mx-auto flex flex-col h-[calc(100vh-3rem)] px-4 sm:px-6 lg:px-8 pt-0 relative">
      <EditorialClient
        initialMessages={messages}
        initialComms={comms}
      />
    </div>
  );
}
