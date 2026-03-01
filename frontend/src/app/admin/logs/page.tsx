import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getAuditLogs, getAuditAdmins } from "@/lib/queries/admin";
import { Shield } from "lucide-react";
import { LogsClient } from "./LogsClient";

export const dynamic = "force-dynamic";

export default async function AuditLogsPage() {
  const session = await auth();
  if (!session || session.user.role !== "admin") {
    redirect("/login");
  }

  // Fetch all potential logs and admins for the filters
  const [logs, admins] = await Promise.all([
    getAuditLogs({ limit: 500 }),
    getAuditAdmins()
  ]);

  return (
    <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500 pt-4">
      <LogsClient initialLogs={logs} admins={admins} />
    </div>
  );
}
