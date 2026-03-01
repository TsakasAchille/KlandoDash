import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingEmailsAction } from "@/app/marketing/actions/mailing";
import { getMarketingCommAction } from "@/app/marketing/actions/communication";
import { EditorialClient } from "./editorial-client";
import { PenTool, CheckCircle, Calendar as CalendarIcon, Hash } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MarketingEmail, MarketingComm } from "@/app/marketing/types";
import { cn } from "@/lib/utils";

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

  // On récupère toujours les deux pour les stats du header, 
  // mais on pourrait optimiser ici plus tard avec une requête de comptage légère.
  const [emailResult, commResult] = await Promise.all([
    getMarketingEmailsAction(),
    getMarketingCommAction()
  ]);

  const emails = (emailResult.success ? emailResult.data : []) as MarketingEmail[];
  const comms = (commResult.success ? commResult.data : []) as MarketingComm[];

  return (
    <div className="max-w-[1600px] mx-auto flex flex-col h-[calc(100vh-3rem)] px-4 sm:px-6 lg:px-8 pt-0 relative">
      <EditorialClient
        initialEmails={emails}
        initialComms={comms}
      />
    </div>
  );
}
