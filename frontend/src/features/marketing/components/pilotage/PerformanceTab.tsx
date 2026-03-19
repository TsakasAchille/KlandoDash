"use client";

import { Zap, Target, TrendingUp, Users, Car, RefreshCw, CheckCircle2, Info } from "lucide-react";
import { KPICard } from "@/components/home/KPICard";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface PerformanceTabProps {
  metrics: any;
}

function MetricInfo({ title, details }: { title: string; details: React.ReactNode }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="p-1 hover:bg-slate-100 rounded-full transition-colors text-muted-foreground/40 hover:text-klando-gold active:scale-95">
          <Info className="w-3.5 h-3.5" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80 bg-slate-900 border-white/10 text-white p-4 rounded-2xl shadow-2xl backdrop-blur-xl">
        <div className="space-y-3">
          <h4 className="text-[10px] font-black uppercase tracking-widest text-klando-gold border-b border-white/5 pb-2">
            Logique Technique : {title}
          </h4>
          <div className="text-[11px] leading-relaxed space-y-2 text-slate-300 font-medium">
            {details}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

export function PerformanceTab({ metrics }: PerformanceTabProps) {
  return (
    <div className="space-y-10 outline-none animate-in fade-in duration-500 text-left">
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
            <Zap className="w-4 h-4 text-klando-gold" /> Acquisition & Engagement
          </h2>
          <MetricInfo 
            title="Acquisition" 
            details={
              <div className="space-y-2">
                <p><span className="text-white font-bold">Activation Passager :</span> Nouveaux inscrits ayant fait une demande sur le site sous 72h. (Tables: <code className="text-blue-400">users</code>, <code className="text-blue-400">site_trip_requests</code>)</p>
                <p><span className="text-white font-bold">Activation Conducteur :</span> Nouveaux inscrits ayant publié un trajet sous 7j. (Tables: <code className="text-blue-400">users</code>, <code className="text-blue-400">trips</code>)</p>
                <p><span className="text-white font-bold">Retention (Repeat) :</span> Utilisateurs actifs en Semaine N-2 ayant réitéré en Semaine N-1. (Tables: <code className="text-blue-400">bookings</code>, <code className="text-blue-400">trips</code>)</p>
              </div>
            }
          />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard title="Activation Passager" value={`${metrics.activation.passenger}%`} icon="Users" color="blue" description="Requête sous 72h" />
          <KPICard title="Activation Conducteur" value={`${metrics.activation.driver}%`} icon="Car" color="purple" description="Trajet sous 7j" />
          <KPICard title="Repeat Passager (W1)" value={`${metrics.retention.passenger_w1}%`} icon="RefreshCw" color="green" description="Actif W N-2 → N-1" />
          <KPICard title="Repeat Conducteur (W1)" value={`${metrics.retention.driver_w1}%`} icon="RefreshCw" color="orange" description="Actif W N-2 → N-1" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
              <Target className="w-4 h-4" /> Liquidité (Match Rate)
            </h2>
            <MetricInfo 
              title="Liquidité" 
              details={
                <div className="space-y-2">
                  <p><span className="text-white font-bold">Match Rate Demande :</span> % de demandes site ayant trouvé au moins un trajet correspondant. (Tables: <code className="text-blue-400">site_trip_requests</code>, <code className="text-blue-400">site_trip_request_matches</code>)</p>
                  <p><span className="text-white font-bold">Match Rate Offre :</span> % de trajets publiés ayant reçu au moins une réservation. (Table: <code className="text-blue-400">trips</code>, Column: <code className="text-emerald-400">seats_booked</code>)</p>
                </div>
              }
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <KPICard title="Match Rate Demande" value={`${metrics.liquidity.match_rate_demand}%`} icon="Target" color="blue" />
            <KPICard title="Match Rate Offre" value={`${metrics.liquidity.match_rate_supply}%`} icon="Car" color="purple" />
          </div>
        </div>
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-black uppercase tracking-[0.2em] text-muted-foreground/60 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" /> Efficacité
            </h2>
            <MetricInfo 
              title="Efficacité" 
              details={
                <div className="space-y-2">
                  <p><span className="text-white font-bold">Fill Rate :</span> Moyenne du remplissage des trajets terminés. Formula: <code className="text-emerald-400">booked / (available + booked)</code>. (Table: <code className="text-blue-400">trips</code>)</p>
                  <p><span className="text-white font-bold">Exécution :</span> Ratio trajets <code className="text-emerald-400">COMPLETED</code> sur total publiés (hors annulés). (Table: <code className="text-blue-400">trips</code>)</p>
                </div>
              }
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <KPICard title="Fill Rate Moyen" value={`${metrics.efficiency.fill_rate}%`} icon="Users" color="green" />
            <KPICard title="Exécution (Realized)" value={`${metrics.efficiency.realized_published_ratio}%`} icon="CheckCircle2" color="blue" />
          </div>
        </div>
      </div>
    </div>
  );
}
