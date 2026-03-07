"use client";

import { Zap, Target, TrendingUp, Users, Car, RefreshCw, CheckCircle2 } from "lucide-react";
import { KPICard } from "@/components/home/KPICard";

interface PerformanceTabProps {
  metrics: any;
}

export function PerformanceTab({ metrics }: PerformanceTabProps) {
  return (
    <div className="space-y-10 outline-none animate-in fade-in duration-500 text-left">
      <div className="space-y-6">
        <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
          <Zap className="w-4 h-4 text-klando-gold" /> Acquisition & Engagement
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard title="Activation Passager" value={`${metrics.activation.passenger}%`} icon="Users" color="blue" description="Requête sous 72h" />
          <KPICard title="Activation Conducteur" value={`${metrics.activation.driver}%`} icon="Car" color="purple" description="Trajet sous 7j" />
          <KPICard title="Repeat Passager (W1)" value={`${metrics.retention.passenger_w1}%`} icon="RefreshCw" color="green" description="Actif W N-2 → N-1" />
          <KPICard title="Repeat Conducteur (W1)" value={`${metrics.retention.driver_w1}%`} icon="RefreshCw" color="orange" description="Actif W N-2 → N-1" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
            <Target className="w-4 h-4" /> Liquidité (Match Rate)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <KPICard title="Match Rate Demande" value={`${metrics.liquidity.match_rate_demand}%`} icon="Target" color="blue" />
            <KPICard title="Match Rate Offre" value={`${metrics.liquidity.match_rate_supply}%`} icon="Car" color="purple" />
          </div>
        </div>
        <div className="space-y-6">
          <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" /> Efficacité
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <KPICard title="Fill Rate Moyen" value={`${metrics.efficiency.fill_rate}%`} icon="Users" color="green" />
            <KPICard title="Exécution (Realized)" value={`${metrics.efficiency.realized_published_ratio}%`} icon="CheckCircle2" color="blue" />
          </div>
        </div>
      </div>
    </div>
  );
}
