import { auth } from "@/lib/auth";
import { getHomeSummary } from "@/lib/queries/stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatPrice, cn, formatDate } from "@/lib/utils";
import Link from "next/link";
import { 
  Car, 
  Users, 
  Ticket, 
  Banknote, 
  ArrowRight, 
  Clock, 
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  UserPlus,
  ArrowUpRight,
  ArrowDownLeft,
  Globe
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";

export const dynamic = "force-dynamic";

function KPICard({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  href,
  description
}: { 
  title: string; 
  value: string | number; 
  icon: any; 
  color: "blue" | "purple" | "red" | "green";
  href: string;
  description?: string;
}) {
  const themes = {
    blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
    purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
    red: "text-red-500 bg-red-500/10 border-red-500/20",
    green: "text-green-500 bg-green-500/10 border-green-500/20",
  };

  return (
    <Link href={href} className="block group">
      <Card className="h-full border-none shadow-sm hover:shadow-xl transition-all duration-500 bg-card/80 backdrop-blur-md overflow-hidden relative">
        {/* Glow Effect - No sharp edges */}
        <div className={cn(
          "absolute -top-12 -right-12 w-40 h-40 blur-3xl opacity-[0.15] transition-all duration-1000 group-hover:opacity-30 group-hover:scale-150 z-0",
          themes[color].split(' ')[1]
        )} />
        
        <CardContent className="pt-6 relative z-10">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">{title}</p>
              <h3 className="text-3xl font-black tracking-tighter group-hover:text-klando-gold transition-colors">{value}</h3>
              {description && <p className="text-[10px] text-muted-foreground font-semibold italic">{description}</p>}
            </div>
            {/* Floating Icon Box */}
            <div className={cn(
              "p-3.5 rounded-2xl border transition-all duration-500 group-hover:rotate-12 group-hover:shadow-lg",
              themes[color]
            )}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-6 flex items-center text-[10px] font-black text-klando-gold opacity-0 group-hover:opacity-100 transition-all transform translate-x-[-10px] group-hover:translate-x-0">
            GÉRER LE MODULE <ArrowRight className="ml-1.5 w-3 h-3" />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

export default async function Home() {
  const session = await auth();
  const summary = await getHomeSummary();

  const activeTrips = summary.trips.byStatus.find(s => s.status === 'ACTIVE')?.count || 0;

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-16 px-4 sm:px-6 lg:px-8 animate-in fade-in duration-700">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border/40 pb-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-black tracking-tight uppercase bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">Tableau de Bord</h1>
          <p className="text-sm text-muted-foreground font-medium">
            Bonjour, <span className="text-klando-gold font-bold text-base ml-1">{session?.user?.name?.split(' ')[0] || 'Admin'}</span>. Ravi de vous revoir.
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="Trajets Live" 
          value={activeTrips} 
          icon={Car} 
          color="blue"
          href="/trips?status=ACTIVE"
          description={`${summary.trips.total} au total`}
        />
        <KPICard 
          title="Utilisateurs" 
          value={summary.users.total} 
          icon={Users} 
          color="purple"
          href="/users"
          description={`+${summary.users.newThisMonth} ce mois-ci`}
        />
        <KPICard 
          title="Support" 
          value={summary.recentTickets.filter(t => t.status === 'OPEN').length} 
          icon={AlertCircle} 
          color="red"
          href="/support"
          description="Tickets ouverts"
        />
        <KPICard 
          title="Marge Brute" 
          value={formatPrice(summary.revenue.klandoMargin)} 
          icon={TrendingUp} 
          color="green"
          href="/stats"
          description="Trajets payés"
        />
      </div>

      {/* Public Status Section */}
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
              Gérer l'affichage <ArrowUpRight className="ml-2 w-3 h-3" />
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
              {summary.publicPending.length > 0 ? (
                summary.publicPending.map((trip: any) => (
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
              {summary.publicCompleted.length > 0 ? (
                summary.publicCompleted.map((trip: any) => (
                  <div key={trip.id} className="bg-green-500/5 border border-green-500/10 px-4 py-2.5 rounded-2xl flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
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

      {/* Main Activity */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black flex items-center gap-2 uppercase tracking-widest">
            <Clock className="w-5 h-5 text-klando-gold" />
            Trajets Récents
          </h2>
          <Link href="/trips" className="text-[10px] font-black hover:text-klando-gold transition-colors tracking-widest text-muted-foreground underline underline-offset-4">TOUT VOIR</Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {summary.recentTrips.map((trip) => (
            <Link key={trip.trip_id} href={`/trips?selected=${trip.trip_id}`}>
              <div className="p-5 rounded-2xl bg-card border border-border/40 hover:border-klando-gold/40 transition-all duration-300 group h-full flex flex-col justify-between shadow-sm hover:shadow-md">
                <div>
                  <div className="flex justify-between items-start mb-4">
                    <span className={cn(
                      "text-[9px] font-black px-2.5 py-1 rounded-lg",
                      trip.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-500' : 'bg-secondary text-muted-foreground'
                    )}>
                      {trip.status}
                    </span>
                    <p className="text-[9px] font-mono text-muted-foreground/60 tracking-tighter">#{trip.trip_id.slice(-6)}</p>
                  </div>
                  <div className="flex items-center gap-3 mb-6">
                    <div className="flex flex-col flex-1 min-w-0">
                      <p className="font-black text-sm truncate uppercase tracking-tight">{trip.departure_city}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-1 h-1 rounded-full bg-klando-gold" />
                        <p className="text-[11px] text-muted-foreground truncate font-medium">{trip.destination_city}</p>
                      </div>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-secondary/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <ArrowRight className="w-4 h-4 text-klando-gold" />
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2.5 pt-4 border-t border-border/30">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-secondary to-secondary/30 flex items-center justify-center text-[11px] font-black border border-border/50 text-klando-gold">
                    {trip.driver_name.charAt(0)}
                  </div>
                  <div className="min-w-0">
                    <p className="text-[10px] font-black text-foreground truncate">{trip.driver_name}</p>
                    <p className="text-[8px] text-muted-foreground font-bold tracking-widest uppercase">Conducteur</p>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* New Members - Table Style UI Improvement */}
      <div className="space-y-6 pt-4">
        <h2 className="text-lg font-black flex items-center gap-2 uppercase tracking-widest">
          <UserPlus className="w-5 h-5 text-purple-500" />
          Nouveaux Membres
        </h2>
        <div className="bg-card rounded-3xl border border-border/40 overflow-hidden shadow-sm">
          <div className="divide-y divide-border/20">
            {summary.recentUsers.map((user) => (
              <Link key={user.uid} href={`/users?selected=${user.uid}`} className="block hover:bg-secondary/20 transition-all duration-300 group">
                <div className="flex items-center justify-between p-5 px-8">
                  <div className="flex items-center gap-6">
                    <div className="relative">
                      <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-secondary to-card overflow-hidden flex-shrink-0 flex items-center justify-center border border-border/50 group-hover:border-klando-gold/50 transition-colors shadow-inner">
                        {user.photo_url ? (
                          <img src={user.photo_url} alt="" className="w-full h-full object-cover" />
                        ) : (
                          <span className="text-lg font-black text-klando-gold">{(user.display_name || '?').charAt(0)}</span>
                        )}
                      </div>
                      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-card rounded-full" />
                    </div>
                    <div>
                      <p className="font-black text-sm uppercase tracking-tight group-hover:text-klando-gold transition-colors">{user.display_name || 'Sans nom'}</p>
                      <p className="text-[11px] text-muted-foreground mt-1 font-medium">{user.email}</p>
                    </div>
                  </div>
                  
                  <div className="hidden md:flex items-center gap-12">
                    <div className="text-right space-y-1">
                      <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Rôle</p>
                      <span className="text-[10px] font-black uppercase bg-secondary px-3 py-1 rounded-lg border border-border/50">
                        {user.role}
                      </span>
                    </div>
                    <div className="text-right space-y-1">
                      <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Inscription</p>
                      <p className="text-[11px] font-bold">{user.created_at ? formatDate(user.created_at) : '-'}</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-secondary/50 flex items-center justify-center group-hover:bg-klando-gold group-hover:text-white transition-all">
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
