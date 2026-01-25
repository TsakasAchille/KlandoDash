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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-klando-gold" />
          <h1 className="text-3xl font-bold">Utilisateurs</h1>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground">Total:</span>{" "}
            <span className="font-semibold">{stats.total_users}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400">
            Conducteurs vérifiés: {stats.verified_drivers}
          </div>
          <div className="px-3 py-1 rounded-full bg-klando-gold/20 text-klando-gold">
            Note moy: {stats.avg_rating.toFixed(1)}★
          </div>
        </div>
      </div>

      <UsersPageClient
        users={users}
        initialSelectedId={selected || null}
        initialSelectedUser={initialSelectedUser}
      />
    </div>
  );
}
