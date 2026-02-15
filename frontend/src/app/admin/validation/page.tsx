import { getUsers } from "@/lib/queries/users";
import { ValidationClient } from "./validation-client";
import { ShieldCheck } from "lucide-react";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: {
    page?: string;
    status?: string;
  };
}

export default async function ValidationPage({ searchParams }: PageProps) {
  const currentPage = Number(searchParams.page) || 1;
  const pageSize = 10;
  const statusFilter = searchParams.status || "pending";

  const { users: pendingUsers, totalCount } = await getUsers(currentPage, pageSize, {
    verified: statusFilter
  });

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-tight flex items-center gap-3">
            <ShieldCheck className="w-8 h-8 text-klando-gold" />
            Validation Conducteurs
          </h1>
          <p className="text-muted-foreground mt-1">
            Gérez les documents d&apos;identité et permis de conduire des membres.
          </p>
        </div>
      </div>

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
