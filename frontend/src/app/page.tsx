import { auth } from "@/lib/auth";
import { getHomeSummary } from "@/lib/queries/stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  ArrowDownLeft
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
    blue: "text-blue-500 bg-blue-500",
    purple: "text-purple-500 bg-purple-500",
    red: "text-red-500 bg-red-500",
    green: "text-green-500 bg-green-500",
  };

  return (
    <Link href={href} className="block group">
      <Card className="h-full border-none shadow-sm hover:shadow-md transition-all duration-300 bg-card overflow-hidden relative group">
        <div className={cn(
          "absolute -top-6 -right-6 w-32 h-32 rounded-full opacity-[0.08] transition-transform duration-700 group-hover:scale-150 z-0",
          themes[color].split(' ')[1]
        )} />
        
        <CardContent className="pt-6 relative z-10">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">{title}</p>
              <h3 className="text-3xl font-black group-hover:text-klando-gold transition-colors">{value}</h3>
              {description && <p className="text-[10px] text-muted-foreground font-medium">{description}</p>}
            </div>
            <div className={cn(
              "p-3 rounded-2xl shadow-sm border border-white/5",
              themes[color].split(' ')[1],
              "bg-opacity-10"
            )}>
              <Icon className={cn("w-5 h-5", themes[color].split(' ')[0])} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-[9px] font-black text-klando-gold opacity-0 group-hover:opacity-100 transition-all transform translate-y-2 group-hover:translate-y-0">
            GÉRER <ArrowRight className="ml-1 w-3 h-3" />
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
    <div className="max-w-7xl mx-auto space-y-10 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase">Dashboard</h1>
          <p className="text-sm text-muted-foreground font-medium italic">
            Bonjour, <span className="text-klando-gold not-italic font-bold">{session?.user?.name?.split(' ')[0] || 'Admin'}</span>.
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
          description="Tickets à traiter"
        />
        <KPICard 
          title="Marge Brute" 
          value={formatPrice(summary.revenue.klandoMargin)} 
          icon={TrendingUp} 
          color="green"
          href="/stats"
          description="Total cumulé"
        />
      </div>

      {/* Main Activity: Trips only for a cleaner look */}
      <div className="space-y-4">
        <h2 className="text-sm font-black flex items-center gap-2 uppercase tracking-widest text-muted-foreground/80">
          <Clock className="w-4 h-4 text-klando-gold" />
          Derniers Trajets
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {summary.recentTrips.map((trip) => (
            <Link key={trip.trip_id} href={`/trips?selected=${trip.trip_id}`}>
              <div className="p-5 rounded-2xl bg-card border border-border/50 hover:border-klando-gold/50 transition-all group h-full flex flex-col justify-between shadow-sm">
                <div>
                  <div className="flex justify-between items-start mb-4">
                    <span className={cn(
                      "text-[9px] font-black px-2 py-0.5 rounded-full",
                      trip.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-500' : 'bg-gray-500/10 text-gray-500'
                    )}>
                      {trip.status}
                    </span>
                    <p className="text-[9px] font-mono text-muted-foreground">#{trip.trip_id.slice(-6)}</p>
                  </div>
                  <div className="flex items-center gap-3 mb-5">
                    <div className="flex flex-col flex-1 min-w-0">
                      <p className="font-bold text-sm truncate uppercase tracking-tight">{trip.departure_city}</p>
                      <p className="text-xs text-muted-foreground truncate italic">{trip.destination_city}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-klando-gold transition-colors" />
                  </div>
                </div>
                <div className="flex items-center gap-2 pt-3 border-t border-border/40">
                  <div className="w-7 h-7 rounded-full bg-secondary flex items-center justify-center text-[10px] font-bold text-muted-foreground">
                    {trip.driver_name.charAt(0)}
                  </div>
                  <p className="text-[10px] font-bold text-muted-foreground/80">{trip.driver_name}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Row 2: Users (Full Width List) */}
      <div className="space-y-4 pt-4">
        <h2 className="text-sm font-black flex items-center gap-2 uppercase tracking-widest text-muted-foreground/80">
          <UserPlus className="w-4 h-4 text-purple-500" />
          Nouveaux Membres
        </h2>
        <div className="bg-card rounded-2xl border border-border/50 overflow-hidden shadow-sm">
          <div className="divide-y divide-border/40">
            {summary.recentUsers.map((user) => (
              <Link key={user.uid} href={`/users?selected=${user.uid}`} className="block hover:bg-secondary/30 transition-colors p-4 px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-5">
                    <div className="w-10 h-10 rounded-full bg-secondary overflow-hidden flex-shrink-0 flex items-center justify-center border border-border/50 shadow-inner">
                      {user.photo_url ? (
                        <img src={user.photo_url} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <span className="text-sm font-bold text-klando-gold">{(user.display_name || '?').charAt(0)}</span>
                      )}
                    </div>
                    <div>
                      <p className="font-bold text-sm leading-none uppercase tracking-tight">{user.display_name || 'Sans nom'}</p>
                      <p className="text-[10px] text-muted-foreground mt-1.5">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <span className="text-[10px] font-black uppercase tracking-widest bg-secondary px-4 py-1.5 rounded-full text-muted-foreground border border-border/20">
                      {user.role}
                    </span>
                    <ArrowRight className="w-4 h-4 text-muted-foreground/30" />
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