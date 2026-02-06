import { getDashboardStats } from "@/lib/queries/stats";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatPrice, formatDistance } from "@/lib/utils";
import {
  BarChart3,
  Users,
  Car,
  Banknote,
  MapPin,
  UserCheck,
  CalendarPlus,
  Ticket,
  ArrowDownLeft,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";
import { RefreshButton } from "@/components/refresh-button";

export const dynamic = "force-dynamic";

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color = "text-klando-gold",
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  color?: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={`w-5 h-5 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default async function StatsPage() {
  const stats = await getDashboardStats();

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Statistiques</h1>
        </div>
        <RefreshButton />
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Trajets"
          value={stats.trips.total}
          icon={Car}
        />
        <StatCard
          title="Total Utilisateurs"
          value={stats.users.total}
          icon={Users}
        />
        <StatCard
          title="Réservations"
          value={stats.bookings.total}
          icon={Ticket}
        />
        <StatCard
          title="Transactions"
          value={stats.transactions.total}
          icon={Banknote}
          color="text-green-400"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Distance totale"
          value={formatDistance(stats.trips.totalDistance)}
          subtitle="Tous trajets confondus"
          icon={MapPin}
          color="text-blue-400"
        />
        <StatCard
          title="Places réservées"
          value={stats.trips.totalSeatsBooked}
          subtitle="Total passagers transportés"
          icon={Users}
          color="text-purple-400"
        />
        <StatCard
          title="Conducteurs vérifiés"
          value={stats.users.verifiedDrivers}
          subtitle={`${stats.users.total > 0 ? Math.round((stats.users.verifiedDrivers / stats.users.total) * 100) : 0}% des utilisateurs`}
          icon={UserCheck}
          color="text-green-400"
        />
        <StatCard
          title="Nouveaux ce mois"
          value={stats.users.newThisMonth}
          subtitle="Inscriptions récentes"
          icon={CalendarPlus}
          color="text-orange-400"
        />
      </div>

      {/* Status Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Car className="w-5 h-5 text-klando-gold" />
            Répartition des trajets par statut
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
            {stats.trips.byStatus.map(({ status, count }) => (
              <div
                key={status}
                className="flex flex-col items-center p-4 rounded-lg bg-secondary"
              >
                <span
                  className={`text-xl sm:text-2xl font-bold ${
                    status === "ACTIVE"
                      ? "text-blue-400"
                      : status === "COMPLETED"
                      ? "text-green-400"
                      : status === "ARCHIVED"
                      ? "text-gray-400"
                      : status === "CANCELLED"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                >
                  {count}
                </span>
                <span className="text-sm text-muted-foreground mt-1">
                  {status}
                </span>
                <span className="text-xs text-muted-foreground">
                  {stats.trips.total > 0 ? Math.round((count / stats.trips.total) * 100) : 0}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cash Flow */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-klando-gold" />
            Cash Flow (transactions SUCCESS)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowDownLeft className="w-5 h-5 text-green-400" />
                <p className="text-sm text-muted-foreground">Entrées</p>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-green-400">
                {formatPrice(stats.cashFlow.totalIn)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.cashFlow.countIn} transactions
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-red-500/10 border border-red-500/30">
              <div className="flex items-center justify-center gap-2 mb-2">
                <ArrowUpRight className="w-5 h-5 text-red-400" />
                <p className="text-sm text-muted-foreground">Sorties</p>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-red-400">
                {formatPrice(stats.cashFlow.totalOut)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.cashFlow.countOut} transactions
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-klando-gold/10 border border-klando-gold/30">
              <p className="text-sm text-muted-foreground mb-2">Solde</p>
              <p className={`text-xl sm:text-2xl font-bold ${stats.cashFlow.solde >= 0 ? "text-green-400" : "text-red-400"}`}>
                {stats.cashFlow.solde >= 0 ? "+" : ""}{formatPrice(stats.cashFlow.solde)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Revenue Stats (from bookings with transactions) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Banknote className="w-5 h-5 text-klando-gold" />
            Revenus (réservations avec paiement)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 sm:gap-6">
            <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <p className="text-sm text-muted-foreground mb-1">
                Payé par passagers
              </p>
              <p className="text-xl sm:text-2xl font-bold text-green-400">
                {formatPrice(stats.revenue.totalPassengerPaid)}
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-sm text-muted-foreground mb-1">
                Reversé conducteurs
              </p>
              <p className="text-xl sm:text-2xl font-bold text-blue-400">
                {formatPrice(stats.revenue.totalDriverPrice)}
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-klando-gold/10 border border-klando-gold/30">
              <p className="text-sm text-muted-foreground mb-1">
                Marge Klando
              </p>
              <p className="text-xl sm:text-2xl font-bold text-klando-gold">
                {formatPrice(stats.revenue.klandoMargin)}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                inclut 15% TVA
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-secondary">
              <p className="text-sm text-muted-foreground mb-1">
                Transactions
              </p>
              <p className="text-xl sm:text-2xl font-bold">
                {stats.revenue.transactionCount}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                bookings avec paiement
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Transaction Status Distribution */}
      {stats.transactions.byStatus.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Banknote className="w-5 h-5 text-klando-gold" />
              Répartition des transactions par statut
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              {stats.transactions.byStatus.map(({ status, count }) => (
                <div
                  key={status}
                  className="flex flex-col items-center p-4 rounded-lg bg-secondary"
                >
                  <span
                    className={`text-xl sm:text-2xl font-bold ${
                      status === "SUCCESS"
                        ? "text-green-400"
                        : status === "PENDING"
                        ? "text-yellow-400"
                        : status === "FAILED"
                        ? "text-red-400"
                        : "text-gray-400"
                    }`}
                  >
                    {count}
                  </span>
                  <span className="text-sm text-muted-foreground mt-1">
                    {status}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {stats.transactions.total > 0 ? Math.round((count / stats.transactions.total) * 100) : 0}%
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
