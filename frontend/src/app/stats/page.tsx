import { getDashboardStats } from "@/lib/queries/stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

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

      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard title="Trajets" value={stats.trips.total} icon={Car} color="blue" />
        <MiniStatCard title="Utilisateurs" value={stats.users.total} icon={Users} color="purple" />
        <MiniStatCard title="Réservations" value={stats.bookings.total} icon={Ticket} color="gold" />
        <MiniStatCard title="Transactions" value={stats.transactions.total} icon={Banknote} color="green" />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard title="Distance" value={formatDistance(stats.trips.totalDistance)} icon={MapPin} color="blue" />
        <MiniStatCard title="Passagers" value={stats.trips.totalSeatsBooked} icon={Users} color="purple" />
        <MiniStatCard title="Vérifiés" value={stats.users.verifiedDrivers} icon={UserCheck} color="green" />
        <MiniStatCard title="Nouveaux" value={stats.users.newThisMonth} icon={CalendarPlus} color="red" />
      </div>

      {/* User Persona Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Buyer Persona Summary */}
        <Card className="rounded-2xl border-none shadow-sm bg-klando-gold/10 border border-klando-gold/20 flex flex-col justify-center">
          <CardHeader className="text-center">
            <CardTitle className="font-black uppercase text-sm tracking-widest text-klando-gold">
              Profil Type (Buyer Persona)
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center space-y-4">
            <div className="w-20 h-20 rounded-full bg-klando-gold/20 flex items-center justify-center border-2 border-klando-gold/30">
              {stats.users.typicalProfile.gender === "Homme" ? (
                <User className="w-10 h-10 text-klando-gold" />
              ) : (
                <Users className="w-10 h-10 text-klando-gold" />
              )}
            </div>
            <div>
              <h3 className="text-xl font-black text-klando-dark uppercase">
                {stats.users.typicalProfile.gender === "Homme" ? "Le Jeune Actif" : "La Jeune Active"}
              </h3>
              <p className="text-xs font-medium text-muted-foreground mt-1">
                Majorité: <span className="text-klando-dark">{stats.users.typicalProfile.gender}</span>, tranche <span className="text-klando-dark">{stats.users.typicalProfile.ageGroup} ans</span>
              </p>
            </div>
            <p className="text-[10px] leading-relaxed text-muted-foreground/80 font-medium px-4">
              Ce profil représente le cœur de cible de Klando. Il privilégie la mobilité partagée pour ses trajets urbains et interurbains.
            </p>
          </CardContent>
        </Card>

        {/* Gender Distribution */}
        <Card className="rounded-2xl border-none shadow-sm bg-card/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
              <Users className="w-4 h-4 text-klando-gold" />
              Répartition par Genre
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {stats.users.demographics.gender.map(({ label, count }) => {
              const percentage = stats.users.total > 0 ? Math.round((count / stats.users.total) * 100) : 0;
              return (
                <div key={label} className="space-y-2">
                  <div className="flex justify-between items-end">
                    <span className="text-sm font-bold uppercase tracking-tight">{label}</span>
                    <span className="text-xs font-black text-muted-foreground">{count} ({percentage}%)</span>
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

        {/* Age Distribution */}
        <Card className="rounded-2xl border-none shadow-sm bg-card/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
              <CalendarPlus className="w-4 h-4 text-klando-gold" />
              Groupes d&apos;âge
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {stats.users.demographics.age.map(({ label, count }) => {
                const percentage = stats.users.total > 0 ? Math.round((count / stats.users.total) * 100) : 0;
                return (
                  <div key={label} className="flex items-center gap-4">
                    <div className="w-16 text-xs font-black text-muted-foreground uppercase">{label}</div>
                    <div className="flex-1 h-3 bg-secondary/50 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-klando-gold rounded-full transition-all duration-1000"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <div className="w-20 text-right text-[10px] font-bold">
                      {count} ({percentage}%)
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Distribution */}
      <Card className="rounded-2xl border-none shadow-sm bg-card/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
            <Car className="w-4 h-4 text-klando-gold" />
            Répartition des trajets
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {stats.trips.byStatus.map(({ status, count }) => (
              <div
                key={status}
                className="flex flex-col items-center p-4 rounded-xl bg-secondary/50 border border-border/50"
              >
                <span
                  className={`text-2xl font-black ${
                    status === "ACTIVE"
                      ? "text-blue-500"
                      : status === "COMPLETED"
                      ? "text-green-500"
                      : status === "ARCHIVED"
                      ? "text-gray-400"
                      : status === "CANCELLED"
                      ? "text-red-500"
                      : "text-yellow-500"
                  }`}
                >
                  {count}
                </span>
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mt-1">
                  {status}
                </span>
                <span className="text-[10px] text-muted-foreground/60">
                  {stats.trips.total > 0 ? Math.round((count / stats.trips.total) * 100) : 0}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cash Flow */}
      <Card className="rounded-2xl border-none shadow-sm bg-card/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
            <TrendingUp className="w-4 h-4 text-klando-gold" />
            Cash Flow (Transactions SUCCESS)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 rounded-2xl bg-green-500/5 border border-green-500/20">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowDownLeft className="w-5 h-5 text-green-500" />
                <p className="text-xs font-bold text-green-600 uppercase tracking-widest">Entrées</p>
              </div>
              <p className="text-3xl font-black text-green-500 tracking-tight">
                {formatPrice(stats.cashFlow.totalIn)}
              </p>
              <p className="text-[10px] text-green-600/60 font-medium mt-1">
                {stats.cashFlow.countIn} transactions
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-red-500/5 border border-red-500/20">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowUpRight className="w-5 h-5 text-red-500" />
                <p className="text-xs font-bold text-red-600 uppercase tracking-widest">Sorties</p>
              </div>
              <p className="text-3xl font-black text-red-500 tracking-tight">
                {formatPrice(stats.cashFlow.totalOut)}
              </p>
              <p className="text-[10px] text-red-600/60 font-medium mt-1">
                {stats.cashFlow.countOut} transactions
              </p>
            </div>
            <div className="text-center p-6 rounded-2xl bg-klando-gold/5 border border-klando-gold/20">
              <p className="text-xs font-bold text-klando-gold/80 uppercase tracking-widest mb-2">Solde Net</p>
              <p className={`text-3xl font-black tracking-tight ${stats.cashFlow.solde >= 0 ? "text-green-500" : "text-red-500"}`}>
                {stats.cashFlow.solde >= 0 ? "+" : ""}{formatPrice(stats.cashFlow.solde)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Revenue Stats */}
      <Card className="rounded-2xl border-none shadow-sm bg-card/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-black uppercase text-sm tracking-widest text-muted-foreground">
            <Banknote className="w-4 h-4 text-klando-gold" />
            Revenus (Réservations payées)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 rounded-xl bg-green-500/5 border border-green-500/10">
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
                Passagers (Payé)
              </p>
              <p className="text-xl font-black text-green-500">
                {formatPrice(stats.revenue.totalPassengerPaid)}
              </p>
            </div>
            <div className="text-center p-4 rounded-xl bg-blue-500/5 border border-blue-500/10">
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
                Conducteurs (Reversé)
              </p>
              <p className="text-xl font-black text-blue-500">
                {formatPrice(stats.revenue.totalDriverPrice)}
              </p>
            </div>
            <div className="text-center p-4 rounded-xl bg-klando-gold/10 border border-klando-gold/30">
              <p className="text-[10px] font-bold text-klando-gold uppercase tracking-wider mb-1">
                Marge Klando
              </p>
              <p className="text-2xl font-black text-klando-gold">
                {formatPrice(stats.revenue.klandoMargin)}
              </p>
              <p className="text-[9px] text-klando-gold/60 mt-1 font-medium">
                TVA 15% incluse
              </p>
            </div>
            <div className="text-center p-4 rounded-xl bg-secondary/50 border border-border/50">
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">
                Volume
              </p>
              <p className="text-xl font-black">
                {stats.revenue.transactionCount}
              </p>
              <p className="text-[9px] text-muted-foreground mt-1">
                réservations
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}