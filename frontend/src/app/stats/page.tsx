import { getDashboardStats } from "@/lib/queries/stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatPrice, formatDistance } from "@/lib/utils";
import {
  BarChart3,
  Users,
  User,
  Car,
  Banknote,
  MapPin,
  UserCheck,
  CalendarPlus,
  Ticket,
  TrendingUp,
  ArrowDownLeft,
  ArrowUpRight,
  ShieldCheck,
  UserPlus,
  XCircle,
  LayoutGrid,
  PieChart as PieChartIcon
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";
import { StatsCharts } from "@/app/stats/stats-charts";

export const dynamic = "force-dynamic";

export default async function StatsPage() {
  const stats = await getDashboardStats();

  return (
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-klando-gold" />
            Statistiques
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Analyse globale et performance de la plateforme
          </p>
        </div>
        <RefreshButton />
      </div>

      <Tabs defaultValue="overview" className="space-y-8">
        <TabsList className="bg-secondary/50 p-1 h-auto grid grid-cols-2 md:grid-cols-4 gap-2">
          <TabsTrigger value="overview" className="data-[state=active]:bg-klando-gold data-[state=active]:text-black font-bold uppercase text-[10px] tracking-widest py-3">
            <LayoutGrid className="w-4 h-4 mr-2" />
            Vue d'Ensemble
          </TabsTrigger>
          <TabsTrigger value="drivers" className="data-[state=active]:bg-klando-gold data-[state=active]:text-black font-bold uppercase text-[10px] tracking-widest py-3">
            <Car className="w-4 h-4 mr-2" />
            Conducteurs
          </TabsTrigger>
          <TabsTrigger value="users" className="data-[state=active]:bg-klando-gold data-[state=active]:text-black font-bold uppercase text-[10px] tracking-widest py-3">
            <Users className="w-4 h-4 mr-2" />
            Utilisateurs
          </TabsTrigger>
          <TabsTrigger value="finances" className="data-[state=active]:bg-klando-gold data-[state=active]:text-black font-bold uppercase text-[10px] tracking-widest py-3">
            <Banknote className="w-4 h-4 mr-2" />
            Finances
          </TabsTrigger>
        </TabsList>

        {/* --- TAB: OVERVIEW --- */}
        <TabsContent value="overview" className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MiniStatCard title="Trajets" value={stats.trips.total} icon={Car} color="blue" />
            <MiniStatCard title="Utilisateurs" value={stats.users.total} icon={Users} color="purple" />
            <MiniStatCard title="Réservations" value={stats.bookings.total} icon={Ticket} color="gold" />
            <MiniStatCard title="Transactions" value={stats.transactions.total} icon={Banknote} color="green" />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MiniStatCard title="Distance" value={formatDistance(stats.trips.totalDistance)} icon={MapPin} color="blue" />
            <MiniStatCard title="Intentions Site" value={stats.marketing?.siteRequestsTotal || 0} icon={UserPlus} color="gold" />
            <MiniStatCard title="Taux Annulation" value={`${stats.trips.cancellationRate || 0}%`} icon={XCircle} color="red" />
            <MiniStatCard title="Nouveaux" value={stats.users.newThisMonth} icon={CalendarPlus} color="purple" />
          </div>

          <Card className="rounded-2xl border-none shadow-sm bg-card/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                <Car className="w-4 h-4 text-klando-gold" />
                Répartition des trajets par statut
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {stats.trips.byStatus.map(({ status, count }) => (
                  <div key={status} className="flex flex-col items-center p-4 rounded-xl bg-secondary/50 border border-border/50">
                    <span className={`text-2xl font-black ${
                      status === "ACTIVE" ? "text-blue-500" : 
                      status === "COMPLETED" ? "text-green-500" : 
                      status === "CANCELLED" ? "text-red-500" : "text-yellow-500"
                    }`}>
                      {count}
                    </span>
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mt-1">{status}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- TAB: DRIVERS --- */}
        <TabsContent value="drivers" className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="rounded-2xl border-none shadow-sm bg-card/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                  <ShieldCheck className="w-4 h-4 text-klando-gold" />
                  Pipeline de Vérification
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[300px] flex items-center justify-center">
                 <StatsCharts type="verification" data={stats.users.acquisition?.verificationStatus || []} />
              </CardContent>
            </Card>

            <Card className="rounded-2xl border-none shadow-sm bg-card/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                  <LayoutGrid className="w-4 h-4 text-klando-gold" />
                  Performance Moyenne
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col justify-center h-[300px] space-y-6">
                <div className="text-center">
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 mb-2">Sièges par trajet</p>
                  <p className="text-5xl font-black text-klando-gold">{stats.trips.avgSeatsPerTrip || 0}</p>
                </div>
                <div className="text-center">
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 mb-2">Note moyenne conducteurs</p>
                  <p className="text-5xl font-black text-blue-500">{stats.users.avgRating?.toFixed(1) || 0}</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="rounded-2xl border-none shadow-sm bg-card/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                <ShieldCheck className="w-4 h-4 text-klando-gold" />
                Top Conducteurs (Performance)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-border/40">
                      <th className="py-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground">Conducteur</th>
                      <th className="py-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-center">Trajets</th>
                      <th className="py-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-center">Note</th>
                      <th className="py-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-right">CA Généré</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/20">
                    {(stats.users.acquisition?.topDrivers || []).map((driver) => (
                      <tr key={driver.uid} className="hover:bg-white/5 transition-colors">
                        <td className="py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center overflow-hidden border border-border">
                              {driver.photo_url ? (
                                <img src={driver.photo_url} alt="" className="w-full h-full object-cover" />
                              ) : (
                                <User className="w-4 h-4 text-muted-foreground" />
                              )}
                            </div>
                            <span className="text-sm font-bold">{driver.display_name}</span>
                          </div>
                        </td>
                        <td className="py-3 text-center"><span className="text-sm font-black">{driver.trips_count}</span></td>
                        <td className="py-3 text-center"><span className="text-sm font-bold text-klando-gold">★ {Number(driver.rating).toFixed(1)}</span></td>
                        <td className="py-3 text-right"><span className="text-sm font-black text-green-500">{formatPrice(driver.revenue)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- TAB: USERS & DEMOGRAPHICS --- */}
        <TabsContent value="users" className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Market Typology */}
            <Card className="rounded-2xl border-none shadow-sm bg-card/50 lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                  <PieChartIcon className="w-4 h-4 text-klando-gold" />
                  Équilibre du Marché
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[300px] flex items-center justify-center">
                 <StatsCharts type="typology" data={stats.users.typology} />
              </CardContent>
            </Card>

            {/* Gender Distribution (RESTORED) */}
            <Card className="rounded-2xl border-none shadow-sm bg-card/50 lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                  <Users className="w-4 h-4 text-klando-gold" />
                  Répartition par Genre
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6 pt-4">
                {stats.users.demographics.gender.map(({ label, count }) => {
                  const percentage = stats.users.total > 0 ? Math.round((count / stats.users.total) * 100) : 0;
                  return (
                    <div key={label} className="space-y-2">
                      <div className="flex justify-between items-end">
                        <span className="text-xs font-bold uppercase tracking-tight">{label}</span>
                        <span className="text-[10px] font-black text-muted-foreground">{count} ({percentage}%)</span>
                      </div>
                      <div className="h-2 w-full bg-secondary/50 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-1000 ${
                            label === "Homme" ? "bg-blue-500" : label === "Femme" ? "bg-pink-500" : "bg-gray-400"
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Age Distribution (RESTORED) */}
            <Card className="rounded-2xl border-none shadow-sm bg-card/50 lg:col-span-1">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                  <CalendarPlus className="w-4 h-4 text-klando-gold" />
                  Groupes d&apos;âge
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {stats.users.demographics.age.map(({ label, count }) => {
                  const percentage = stats.users.total > 0 ? Math.round((count / stats.users.total) * 100) : 0;
                  return (
                    <div key={label} className="flex items-center gap-4">
                      <div className="w-16 text-[10px] font-black text-muted-foreground uppercase">{label}</div>
                      <div className="flex-1 h-2.5 bg-secondary/50 rounded-full overflow-hidden">
                        <div className="h-full bg-klando-gold rounded-full transition-all duration-1000" style={{ width: `${percentage}%` }} />
                      </div>
                      <div className="w-16 text-right text-[10px] font-bold">{count}</div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Buyer Persona */}
            <Card className="rounded-2xl border-none shadow-sm bg-klando-gold/10 border border-klando-gold/20 flex flex-col justify-center p-6">
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 rounded-full bg-klando-gold/20 flex items-center justify-center border-2 border-klando-gold/30 shrink-0">
                  {stats.users.typicalProfile.gender === "Homme" ? <User className="w-12 h-12 text-klando-gold" /> : <Users className="w-12 h-12 text-klando-gold" />}
                </div>
                <div>
                  <h3 className="text-xl font-black text-klando-dark uppercase leading-tight">
                    {stats.users.typicalProfile.gender === "Homme" ? "Le Jeune Actif" : "La Jeune Active"}
                  </h3>
                  <p className="text-sm font-bold text-muted-foreground mt-1">
                    Majorité: <span className="text-klando-dark">{stats.users.typicalProfile.gender}</span>, tranche <span className="text-klando-dark">{stats.users.typicalProfile.ageGroup} ans</span>
                  </p>
                  <p className="text-xs mt-3 text-muted-foreground/80 font-medium">
                    Ce profil représente le cœur de cible de Klando. Il privilégie la mobilité partagée pour ses trajets urbains et interurbains.
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="rounded-2xl border-none shadow-sm bg-card/50 p-6 flex items-center justify-center">
               <div className="text-center">
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60 mb-2">Total Utilisateurs</p>
                  <p className="text-6xl font-black text-purple-500 tracking-tighter">{stats.users.total}</p>
                  <p className="text-[10px] font-bold text-muted-foreground mt-2">Croissance continue</p>
               </div>
            </Card>
          </div>
        </TabsContent>

        {/* --- TAB: FINANCES --- */}
        <TabsContent value="finances" className="space-y-8 animate-in fade-in zoom-in-95 duration-300">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-8 rounded-2xl bg-green-500/5 border border-green-500/20">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowDownLeft className="w-5 h-5 text-green-500" />
                <p className="text-xs font-bold text-green-600 uppercase tracking-widest">Entrées</p>
              </div>
              <p className="text-4xl font-black text-green-500 tracking-tight">{formatPrice(stats.cashFlow.totalIn)}</p>
            </div>
            <div className="text-center p-8 rounded-2xl bg-red-500/5 border border-red-500/20">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowUpRight className="w-5 h-5 text-red-500" />
                <p className="text-xs font-bold text-red-600 uppercase tracking-widest">Sorties</p>
              </div>
              <p className="text-4xl font-black text-red-500 tracking-tight">{formatPrice(stats.cashFlow.totalOut)}</p>
            </div>
            <div className="text-center p-8 rounded-2xl bg-klando-gold/5 border border-klando-gold/20">
              <p className="text-xs font-bold text-klando-gold/80 uppercase tracking-widest mb-2">Solde Net</p>
              <p className={`text-4xl font-black tracking-tight ${stats.cashFlow.solde >= 0 ? "text-green-500" : "text-red-500"}`}>
                {stats.cashFlow.solde >= 0 ? "+" : ""}{formatPrice(stats.cashFlow.solde)}
              </p>
            </div>
          </div>

          <Card className="rounded-2xl border-none shadow-sm bg-card/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
                <Banknote className="w-4 h-4 text-klando-gold" />
                Détail des Revenus (Réservations payées)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center p-4 rounded-xl bg-green-500/5 border border-green-500/10">
                  <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">Passagers (Payé)</p>
                  <p className="text-xl font-black text-green-500">{formatPrice(stats.revenue.totalPassengerPaid)}</p>
                </div>
                <div className="text-center p-4 rounded-xl bg-blue-500/5 border border-blue-500/10">
                  <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">Conducteurs (Reversé)</p>
                  <p className="text-xl font-black text-blue-500">{formatPrice(stats.revenue.totalDriverPrice)}</p>
                </div>
                <div className="text-center p-6 rounded-xl bg-klando-gold/10 border border-klando-gold/30">
                  <p className="text-[10px] font-bold text-klando-gold uppercase tracking-wider mb-1">Marge Klando</p>
                  <p className="text-3xl font-black text-klando-gold">{formatPrice(stats.revenue.klandoMargin)}</p>
                </div>
                <div className="text-center p-4 rounded-xl bg-secondary/50 border border-border/50">
                  <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">Volume</p>
                  <p className="text-xl font-black">{stats.revenue.transactionCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
