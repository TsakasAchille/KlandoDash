import { getUsers, getUserById, getUsersStats } from "@/lib/queries/users";
import { UsersPageClient } from "./users-client";
import { Users, ShieldCheck, Star } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function UsersPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  const [users, stats, initialSelectedUser] = await Promise.all([
    getUsers(100),
    getUsersStats(),
    selected ? getUserById(selected) : null,
  ]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <Users className="w-8 h-8 text-klando-gold" />
            Utilisateurs
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Annuaire et gestion des membres Klando
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total_users} 
          icon={Users} 
          color="purple" 
        />
        <MiniStatCard 
          title="Vérifiés" 
          value={stats.verified_drivers} 
          icon={ShieldCheck} 
          color="green" 
        />
        <MiniStatCard 
          title="Note Moyenne" 
          value={stats.avg_rating.toFixed(1)} 
          icon={Star} 
          color="gold" 
        />
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