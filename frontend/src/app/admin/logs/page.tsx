import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getAuditLogs, getAuditAdmins } from "@/lib/queries/admin";
import { Shield } from "lucide-react";
import { LogsClient } from "./LogsClient";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{ 
    page?: string;
    admin?: string;
    action?: string;
  }>;
}

export default async function AuditLogsPage({ searchParams }: PageProps) {
  const { page, admin, action } = await searchParams;
  const currentPage = parseInt(page || "1", 10);
  const pageSize = 50;
  const offset = (currentPage - 1) * pageSize;

  const session = await auth();
  if (!session || session.user.role !== "admin") {
    redirect("/login");
  }

  // Fetch logs with pagination and filters
  const [{ logs, totalCount }, admins] = await Promise.all([
    getAuditLogs({ 
      limit: pageSize, 
      offset,
      adminEmail: admin,
      actionType: action
    }),
    getAuditAdmins()
  ]);

  return (
    <div className="max-w-7xl mx-auto p-8 space-y-8 animate-in fade-in duration-500 pt-4">
      <LogsClient 
        initialLogs={logs} 
        admins={admins} 
        totalCount={totalCount}
        currentPage={currentPage}
        pageSize={pageSize}
      />
    </div>
  );
}
