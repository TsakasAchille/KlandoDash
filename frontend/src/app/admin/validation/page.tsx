import { getUsers } from "@/lib/queries/users";
import { ValidationClient } from "./validation-client";
import { ShieldCheck } from "lucide-react";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{
    page?: string;
    status?: string;
  }>;
}

export default async function ValidationPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const currentPage = Number(params.page) || 1;
  const pageSize = 10;
  const statusFilter = params.status || "pending";

  const { users: pendingUsers, totalCount } = await getUsers(currentPage, pageSize, {
    verified: statusFilter
  });

  return (
    <div className="container mx-auto py-6 space-y-8 pt-4">
      <ValidationClient 
        pendingUsers={pendingUsers} 
        totalCount={totalCount}
        currentPage={currentPage}
        pageSize={pageSize}
        currentStatus={statusFilter}
      />
    </div>
  );
}
