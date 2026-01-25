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
} from "lucide-react";

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
          title="Prix moyen/trajet"
          value={formatPrice(stats.revenue.avgTripPrice)}
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
          subtitle={`${Math.round((stats.users.verifiedDrivers / stats.users.total) * 100)}% des utilisateurs`}
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
                  {Math.round((count / stats.trips.total) * 100)}%
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Revenue Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Banknote className="w-5 h-5 text-klando-gold" />
            Revenus
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
            <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/30">
              <p className="text-sm text-muted-foreground mb-1">
                Total passagers (brut)
              </p>
              <p className="text-xl sm:text-2xl font-bold text-green-400">
                {formatPrice(stats.revenue.totalPassengerPrice)}
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-sm text-muted-foreground mb-1">
                Total conducteurs (net)
              </p>
              <p className="text-xl sm:text-2xl font-bold text-blue-400">
                {formatPrice(stats.revenue.totalDriverPrice)}
              </p>
            </div>
            <div className="text-center p-4 rounded-lg bg-klando-gold/10 border border-klando-gold/30">
              <p className="text-sm text-muted-foreground mb-1">
                Commission Klando
              </p>
              <p className="text-xl sm:text-2xl font-bold text-klando-gold">
                {formatPrice(stats.revenue.totalPassengerPrice - stats.revenue.totalDriverPrice)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
