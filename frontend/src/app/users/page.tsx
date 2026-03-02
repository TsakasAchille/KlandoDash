import { getUsers, getUserById, getUsersStats } from "@/lib/queries/users";
import { UsersPageClient } from "./users-client";
import { Users, ShieldCheck, Star, CalendarPlus } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ 
    selected?: string;
    page?: string;
    role?: string;
    verified?: string;
    search?: string;
    gender?: string;
    minRating?: string;
    isNew?: string;
  }>;
}

export default async function UsersPage({ searchParams }: Props) {
  const { selected, page, role, verified, search, gender, minRating, isNew } = await searchParams;
  const currentPage = parseInt(page || "1", 10);
  const pageSize = 10;

  const [{ users, totalCount }, stats, initialSelectedUser] = await Promise.all([
    getUsers(currentPage, pageSize, {
      role,
      verified,
      search,
      gender,
      minRating: minRating ? parseFloat(minRating) : undefined,
      isNew: isNew === "true",
    }),
    getUsersStats(),
    selected ? getUserById(selected) : null,
  ]);

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>
{/* Stats */}
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
  <MiniStatCard 
    title="Total" 
    value={stats.total_users} 
    icon="Users" 
    color="purple" 
  />
  <MiniStatCard 
    title="Vérifiés" 
    value={stats.verified_drivers} 
    icon="ShieldCheck" 
    color="green" 
  />
  <MiniStatCard 
    title="Note Moyenne" 
    value={stats.avg_rating.toFixed(1)} 
    icon="Star" 
    color="gold" 
  />
  <MiniStatCard 
    title="Nouveaux" 
    value={stats.new_this_month} 
    icon="UserPlus" 
    color="blue" 
    description="Inscrits ce mois-ci"
  />
</div>


      {/* Contenu principal */}
      <UsersPageClient
        users={users}
        totalCount={totalCount}
        currentPage={currentPage}
        pageSize={pageSize}
        initialSelectedId={selected || null}
        initialSelectedUser={initialSelectedUser}
      />
    </div>
  );
}