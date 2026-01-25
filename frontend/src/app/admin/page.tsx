import { getDashUsers } from "@/lib/queries/admin";
import { AdminPageClient } from "./admin-client";
import { Shield } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const users = await getDashUsers();

  const stats = {
    total: users.length,
    admins: users.filter((u) => u.role === "admin").length,
    active: users.filter((u) => u.active).length,
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Administration</h1>
        </div>
      </div>

      {/* Stats responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <div className="flex flex-wrap gap-2">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground text-xs sm:text-sm">Total:</span>{" "}
            <span className="font-semibold text-xs sm:text-sm">{stats.total}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-klando-gold/20 text-klando-gold text-xs sm:text-sm">
            Admins: {stats.admins}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs sm:text-sm">
            Actifs: {stats.active}
          </div>
        </div>
      </div>

      <AdminPageClient users={users} />
    </div>
  );
}
