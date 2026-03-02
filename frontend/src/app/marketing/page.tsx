import { 
  getSiteTripRequestsStats, 
} from "@/lib/queries/site-requests";
import { getMarketingInsightsAction } from "./actions/intelligence";
import { MarketingClient } from "./marketing-client";
import { CircleDot, CheckCircle, Globe, ShieldCheck, TrendingUp, Zap } from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function MarketingPage() {
  const session = await auth();
  if (!session || (session.user.role !== "admin" && session.user.role !== "marketing")) {
    redirect("/login");
  }

  // On ne charge QUE ce qui est vital pour l'affichage immédiat (Stats + Premier onglet)
  const stats = await getSiteTripRequestsStats();

  const pendingCount = 0; // Temporairement désactivé

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <MiniStatCard title="Prospects" value={stats.total} icon="Globe" color="purple" />
        <MiniStatCard title="Nouveaux" value={stats.new} icon="CircleDot" color="red" />
        <MiniStatCard title="À Traiter (IA)" value={pendingCount} icon="Zap" color="gold" />
        <MiniStatCard title="Matchs Validés" value={stats.validated} icon="ShieldCheck" color="green" />
        <MiniStatCard title="Contactés" value={stats.contacted} icon="CheckCircle" color="blue" />
      </div>

      <MarketingClient 
        // Les données seront chargées de manière différée (Smart Loading)
      />
    </div>
  );
}
