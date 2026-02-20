import { 
  getSiteTripRequests, 
  getSiteTripRequestsStats, 
  getPublicPendingTrips, 
  getPublicCompletedTrips,
  getMarketingFlowStats
} from "@/lib/queries/site-requests";
import { getTripsForMap } from "@/lib/queries/trips";
import { getStoredRecommendationsAction } from "@/app/admin/ai/actions";
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
  const [stats, recoResult, insightResult] = await Promise.all([
    getSiteTripRequestsStats(),
    getStoredRecommendationsAction(),
    getMarketingInsightsAction(),
  ]);

  const recommendations = recoResult.success ? recoResult.data : [];
  const insights = insightResult.success ? insightResult.data : [];
  const pendingCount = recommendations.filter((r: any) => r.status === 'PENDING').length;

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1 text-left">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-klando-gold" />
            Marketing & Radar
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Intelligence analytique et détection d&apos;opportunités
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <MiniStatCard title="Prospects" value={stats.total} icon={Globe} color="purple" />
        <MiniStatCard title="Nouveaux" value={stats.new} icon={CircleDot} color="red" />
        <MiniStatCard title="À Traiter (IA)" value={pendingCount} icon={Zap} color="gold" />
        <MiniStatCard title="Matchs Validés" value={stats.validated} icon={ShieldCheck} color="green" />
        <MiniStatCard title="Contactés" value={stats.contacted} icon={CheckCircle} color="blue" />
      </div>

      <MarketingClient 
        initialRecommendations={recommendations}
        initialInsights={insights}
        // Les autres données seront chargées de manière différée (Smart Loading)
      />
    </div>
  );
}
