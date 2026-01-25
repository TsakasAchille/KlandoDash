import { getUsers, getUsersStats } from "@/lib/queries/users";
import { UsersPageClient } from "./users-client";
import { Users } from "lucide-react";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function UsersPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  const [users, stats] = await Promise.all([
    getUsers(100),
    getUsersStats(),
  ]);

  // Find selected user from the list (avoid extra query)
  const initialSelectedUser = selected
    ? users.find((u) => u.uid === selected) || null
    : null;

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Utilisateurs</h1>
        </div>
      </div>

      {/* Stats responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <div className="flex flex-wrap gap-2">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground text-xs sm:text-sm">Total:</span>{" "}
            <span className="font-semibold text-xs sm:text-sm">{stats.total_users}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs sm:text-sm">
            Conducteurs vérifiés: {stats.verified_drivers}
          </div>
          <div className="px-3 py-1 rounded-full bg-klando-gold/20 text-klando-gold text-xs sm:text-sm">
            Note moy: {stats.avg_rating.toFixed(1)}★
          </div>
        </div>
      </div>

      {/* Contenu principal */}
      <UsersPageClient
        users={users}
        initialSelectedId={selected || null}
        initialSelectedUser={initialSelectedUser}
      />
    </div>
  );
}
