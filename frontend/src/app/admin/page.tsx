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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-klando-gold" />
          <h1 className="text-3xl font-bold">Administration</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground">Total:</span>{" "}
            <span className="font-semibold">{stats.total}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-klando-gold/20 text-klando-gold">
            Admins: {stats.admins}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400">
            Actifs: {stats.active}
          </div>
        </div>
      </div>

      <AdminPageClient users={users} />
    </div>
  );
}
