import { auth } from "@/lib/auth";
import { getHomeSummary } from "@/lib/queries/stats";
import { formatPrice } from "@/lib/utils";
import { 
  Car, 
  Users, 
  AlertCircle,
  TrendingUp,
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { KPICard } from "@/components/home/KPICard";
import { PublicStatusSection } from "@/components/home/PublicStatusSection";
import { RecentTripsSection } from "@/components/home/RecentTripsSection";
import { RecentUsersSection } from "@/components/home/RecentUsersSection";

export const dynamic = "force-dynamic";

export default async function Home() {
  const session = await auth();
  const summary = await getHomeSummary();

  const activeTrips = summary.trips.byStatus.find(s => s.status === 'ACTIVE')?.count || 0;

  return (
    <div className="max-w-7xl mx-auto space-y-10 pb-16 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-700 pt-10 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>
      
      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="Trajets Live" 
          value={activeTrips} 
          icon="Car" 
          color="blue"
          href="/trips?status=ACTIVE"
          description={`${summary.trips.total} au total`}
        />
        <KPICard 
          title="Utilisateurs" 
          value={summary.users.total} 
          icon="Users" 
          color="purple"
          href="/users"
          description={`+${summary.users.newThisMonth} ce mois-ci`}
        />
        <KPICard 
          title="Support" 
          value={summary.recentTickets.filter(t => t.status === 'OPEN').length} 
          icon="AlertCircle" 
          color="red"
          href="/support"
          description="Tickets ouverts"
        />
        <KPICard 
          title="Marge Brute" 
          value={formatPrice(summary.revenue.klandoMargin)} 
          icon="TrendingUp" 
          color="green"
          href="/stats"
          description="Trajets payés"
        />
      </div>

      {/* Public Status Section */}
      <PublicStatusSection 
        publicPending={summary.publicPending} 
        publicCompleted={summary.publicCompleted} 
      />

      {/* Main Activity */}
      <RecentTripsSection trips={summary.recentTrips} />

      {/* New Members */}
      <RecentUsersSection users={summary.recentUsers} />
    </div>
  );
}
