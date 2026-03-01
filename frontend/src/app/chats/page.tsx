import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getInternalMessages } from "@/lib/queries/chats/get-chats";
import { ChatsClient } from "./chats-client";

export const dynamic = "force-dynamic";

export default async function ChatsPage() {
  const session = await auth();
  if (!session) {
    redirect("/login");
  }

  const initialMessages = await getInternalMessages();

  return (
    <div className="max-w-[1400px] mx-auto p-4 sm:p-6 lg:p-8 h-full flex flex-col gap-6 pt-4">
      <div className="flex-1 min-h-0">
        <ChatsClient initialMessages={initialMessages} />
      </div>
    </div>
  );
}
