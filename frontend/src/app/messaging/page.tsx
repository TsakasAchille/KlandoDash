import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getMarketingMessagesAction } from "@/app/marketing/actions/messaging";
import { MessagingClient } from "./messaging-client";
import { MarketingMessage } from "@/app/marketing/types";

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
      <MessagingClient initialMessages={messages} />
    </div>
  );
}
