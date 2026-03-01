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
    <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500">
      <header className="flex justify-between items-center border-b border-slate-200 pb-6">
        <div className="text-left">
          <h1 className="text-2xl font-black text-slate-900 uppercase tracking-tight flex items-center gap-3">
            <Shield className="w-7 h-7 text-klando-gold" />
            Journaux d&apos;Audit
          </h1>
          <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">Historique des actions administratives</p>
        </div>
      </header>

      <LogsClient initialLogs={logs} admins={admins} />
    </div>
  );
}
