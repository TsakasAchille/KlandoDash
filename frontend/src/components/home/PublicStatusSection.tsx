import { Badge } from "@/components/ui/badge";
import { Globe, ArrowUpRight, ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { PublicTrip } from "@/lib/queries/stats/types";

interface PublicStatusSectionProps {
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
}

export function PublicStatusSection({ publicPending, publicCompleted }: PublicStatusSectionProps) {
  return (
    <div className="bg-gradient-to-br from-klando-gold/5 via-transparent to-transparent p-8 rounded-[2.5rem] border border-klando-gold/10 space-y-8">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-black flex items-center gap-3 uppercase tracking-tighter">
            <Globe className="w-6 h-6 text-klando-gold" />
            Statut Public (Site Vitrine)
          </h2>
          <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">Aperçu en temps réel de ce que voient les clients</p>
        </div>
        <Link href="/site-requests">
          <Badge variant="outline" className="border-klando-gold/20 text-klando-gold hover:bg-klando-gold/10 transition-colors cursor-pointer px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase">
            Gérer l&apos;affichage <ArrowUpRight className="ml-2 w-3 h-3" />
          </Badge>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Published Destinations */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 px-1">
            <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
            <h3 className="font-black uppercase tracking-widest text-[10px] text-muted-foreground">Destinations en Direct (LIVE)</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {publicPending.length > 0 ? (
              publicPending.map((trip) => (
                <div key={trip.id} className="bg-card border border-border/60 px-4 py-2.5 rounded-2xl flex items-center gap-3 shadow-sm hover:border-klando-gold/40 transition-colors group">
                  <span className="text-[11px] font-black uppercase tracking-tight">{trip.departure_city}</span>
                  <ArrowRight className="w-3 h-3 text-klando-gold group-hover:translate-x-0.5 transition-transform" />
                  <span className="text-[11px] font-black uppercase tracking-tight text-klando-gold">{trip.arrival_city}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground italic px-1">Aucun trajet publié actuellement.</p>
            )}
          </div>
        </div>

        {/* Recently Completed Destinations */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 px-1">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <h3 className="font-black uppercase tracking-widest text-[10px] text-muted-foreground">Derniers trajets terminés (PREUVE)</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {publicCompleted.length > 0 ? (
              publicCompleted.map((trip) => (
                <div key={trip.id} className="bg-green-50/5 border border-green-500/10 px-4 py-2.5 rounded-2xl flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
                  <span className="text-[11px] font-bold uppercase tracking-tight text-muted-foreground">{trip.departure_city}</span>
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500/30" />
                  <span className="text-[11px] font-bold uppercase tracking-tight text-muted-foreground">{trip.arrival_city}</span>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-600 border-none text-[8px] px-1.5 font-black">OK</Badge>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground italic px-1">Aucune preuve sociale disponible.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
