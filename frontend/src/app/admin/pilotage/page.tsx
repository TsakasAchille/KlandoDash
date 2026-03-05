import { getPilotageMetrics } from "@/lib/queries/stats/get-pilotage-metrics";
import { KPICard } from "@/components/home/KPICard";
import { 
  Rocket, 
  RefreshCw, 
  Target, 
  Zap, 
  Map, 
  CheckCircle2,
  TrendingUp,
  AlertTriangle
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RefreshButton } from "@/components/refresh-button";

export const dynamic = "force-dynamic";

export default async function PilotagePage() {
  const metrics = await getPilotageMetrics();

  if (!metrics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-muted-foreground">Erreur lors du chargement des données de pilotage.</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-10 pb-16 px-4 sm:px-6 lg:px-8 pt-6 relative">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black tracking-tighter uppercase italic text-klando-gold flex items-center gap-3">
            <Rocket className="w-8 h-8" />
            Cockpit de Pilotage
          </h1>
          <p className="text-sm text-muted-foreground font-medium uppercase tracking-widest mt-1">
            Performance & Liquidité (Cahier des charges)
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* BLOC 1: ACTIVATION & RÉTENTION */}
      <div className="space-y-6">
        <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
          <Zap className="w-4 h-4" />
          Acquisition & Rétention
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard 
            title="Activation Passager" 
            value={`${metrics.activation.passenger}%`} 
            icon="Users" 
            color="blue"
            description="Requête sous 72h"
          />
          <KPICard 
            title="Activation Conducteur" 
            value={`${metrics.activation.driver}%`} 
            icon="Car" 
            color="purple"
            description="Trajet sous 7j"
          />
          <KPICard 
            title="Repeat Passager (W1)" 
            value={`${metrics.retention.passenger_w1}%`} 
            icon="RefreshCw" 
            color="green"
            description="Actif Semaine N-2 → N-1"
          />
          <KPICard 
            title="Repeat Conducteur (W1)" 
            value={`${metrics.retention.driver_w1}%`} 
            icon="RefreshCw" 
            color="orange"
            description="Actif Semaine N-2 → N-1"
          />
        </div>
      </div>

      {/* BLOC 2: LIQUIDITÉ & EFFICACITÉ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Liquidité (Match Rate)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card className="bg-background/40 backdrop-blur-sm border-klando-gold/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Match Rate Demande</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-black italic text-klando-gold">{metrics.liquidity.match_rate_demand}%</div>
                <p className="text-[9px] font-medium text-muted-foreground mt-1 uppercase tracking-tighter">Requêtes trouvant un trajet</p>
              </CardContent>
            </Card>
            <Card className="bg-background/40 backdrop-blur-sm border-klando-gold/20">
              <CardHeader className="pb-2">
                <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Match Rate Offre</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-black italic text-klando-gold">{metrics.liquidity.match_rate_supply}%</div>
                <p className="text-[9px] font-medium text-muted-foreground mt-1 uppercase tracking-tighter">Trajets avec ≥ 1 résa</p>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Efficacité Opérationnelle
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card className="bg-background/40 backdrop-blur-sm border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Fill Rate Moyen</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-black italic text-foreground">{metrics.efficiency.fill_rate}%</div>
                <p className="text-[9px] font-medium text-muted-foreground mt-1 uppercase tracking-tighter">Occupation des sièges</p>
              </CardContent>
            </Card>
            <Card className="bg-background/40 backdrop-blur-sm border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Exécution (Realized)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-black italic text-foreground">{metrics.efficiency.realized_published_ratio}%</div>
                <p className="text-[9px] font-medium text-muted-foreground mt-1 uppercase tracking-tighter">Ratio Réalisés / Publiés</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* BLOC 3: CORRIDORS PRIORITAIRES */}
      <div className="space-y-6">
        <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
          <Map className="w-4 h-4" />
          Corridors Prioritaires (30 derniers jours)
        </h2>
        <div className="bg-background/40 backdrop-blur-sm border rounded-xl overflow-hidden shadow-2xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-muted/50 text-[10px] font-black uppercase tracking-widest border-b">
                <th className="px-6 py-4">Axe (Origine → Destination)</th>
                <th className="px-6 py-4 text-center">Trajets</th>
                <th className="px-6 py-4 text-center">Réservations</th>
                <th className="px-6 py-4 text-center">Fill Rate</th>
                <th className="px-6 py-4 text-right">Performance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {metrics.corridors.map((corridor: any, idx: number) => (
                <tr key={idx} className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 font-black italic text-sm text-foreground">
                      <span className="text-klando-gold">{corridor.origin}</span>
                      <span className="text-muted-foreground/30">→</span>
                      <span>{corridor.destination}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center font-bold text-sm">{corridor.trips_count}</td>
                  <td className="px-6 py-4 text-center font-bold text-sm text-klando-gold">{corridor.total_bookings}</td>
                  <td className="px-6 py-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-klando-gold transition-all" 
                          style={{ width: `${corridor.fill_rate}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-black italic">{corridor.fill_rate}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {corridor.fill_rate > 50 ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-black uppercase text-green-600 bg-green-500/10 px-2 py-1 rounded">
                        <CheckCircle2 className="w-3 h-3" /> Optimal
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] font-black uppercase text-orange-600 bg-orange-500/10 px-2 py-1 rounded">
                        <AlertTriangle className="w-3 h-3" /> À booster
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
