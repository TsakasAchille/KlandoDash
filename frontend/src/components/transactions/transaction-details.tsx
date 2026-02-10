"use client";

import Link from "next/link";
import { TransactionWithBooking, getCashDirection } from "@/types/transaction";
import { formatDate, formatPrice, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Banknote,
  User,
  Phone,
  Mail,
  Calendar,
  ArrowUpRight,
  ArrowDownLeft,
  Car,
  MapPin,
  ExternalLink,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle,
} from "lucide-react";

interface TransactionDetailsProps {
  transaction: TransactionWithBooking;
}

const statusConfig: Record<string, { icon: React.ElementType; color: string; label: string }> = {
  SUCCESS: { icon: CheckCircle, color: "text-green-400", label: "Succès" },
  PENDING: { icon: Clock, color: "text-yellow-400", label: "En attente" },
  FAILED: { icon: XCircle, color: "text-red-400", label: "Échoué" },
  CANCELLED: { icon: XCircle, color: "text-gray-400", label: "Annulé" },
};

function InfoRow({
  icon: Icon,
  label,
  value,
  color = "text-muted-foreground",
}: {
  icon: React.ElementType;
  label: string;
  value: string | React.ReactNode;
  color?: string;
}) {
  return (
    <div className="flex items-center gap-3 py-2">
      <Icon className={`w-4 h-4 ${color}`} />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground">{label}</p>
        <div className="font-medium truncate">{value}</div>
      </div>
    </div>
  );
}

export function TransactionDetails({ transaction }: TransactionDetailsProps) {
  const direction = getCashDirection(transaction.code_service);
  const statusInfo = statusConfig[transaction.status || ""] || statusConfig.PENDING;
  const StatusIcon = statusInfo.icon;

  // Calcul marge si booking lié
  const hasBooking = !!transaction.booking;
  const driverPrice = transaction.booking?.trip?.driver_price ?? 0;
  const passengerPaid = transaction.amount ?? 0;
  const margin = passengerPaid - driverPrice;

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="border-klando-gold/30">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center gap-2">
              <Banknote className="w-5 h-5 text-klando-gold" />
              Transaction
            </CardTitle>
            <div className="flex items-center gap-2">
              {direction === "CASH_OUT" ? (
                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-500/20 text-green-400 text-sm">
                  <ArrowDownLeft className="w-4 h-4" />
                  Entrée
                </div>
              ) : direction === "CASH_IN" ? (
                <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-sm">
                  <ArrowUpRight className="w-4 h-4" />
                  Sortie
                </div>
              ) : null}
              <div className={cn("flex items-center gap-1 px-2 py-1 rounded-full text-sm",
                transaction.status === "SUCCESS" ? "bg-green-500/20" :
                transaction.status === "PENDING" ? "bg-yellow-500/20" : "bg-red-500/20"
              )}>
                <StatusIcon className={cn("w-4 h-4", statusInfo.color)} />
                <span className={statusInfo.color}>{statusInfo.label}</span>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-6">
            <span className={cn(
              "text-4xl font-bold",
              direction === "CASH_OUT" ? "text-green-400" :
              direction === "CASH_IN" ? "text-red-400" : "text-klando-gold"
            )}>
              {direction === "CASH_OUT" ? "+" : direction === "CASH_IN" ? "-" : ""}
              {formatPrice(transaction.amount ?? 0)}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">ID Transaction</p>
              <p className="font-mono text-xs truncate">{transaction.id}</p>
            </div>
            <div>
              <p className="text-muted-foreground">ID Intech</p>
              <p className="font-mono text-xs truncate">{transaction.intech_transaction_id || "-"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Type</p>
              <p>{transaction.type || "-"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Service</p>
              <p className="text-xs">{transaction.code_service || "-"}</p>
            </div>
          </div>
          {transaction.msg && (
            <div className="mt-4 p-3 rounded-lg bg-secondary/50">
              <p className="text-xs text-muted-foreground mb-1">Message</p>
              <p className="text-sm">{transaction.msg}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="w-5 h-5 text-klando-gold" />
            Utilisateur
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow
            icon={User}
            label="Nom"
            value={
              <Link
                href={`/users?selected=${transaction.user_id}`}
                className="text-klando-gold hover:underline flex items-center gap-1"
              >
                {transaction.user?.display_name || "Inconnu"}
                <ExternalLink className="w-3 h-3" />
              </Link>
            }
            color="text-klando-gold"
          />
          <InfoRow icon={Phone} label="Téléphone" value={transaction.phone || transaction.user?.phone || "-"} />
          <InfoRow icon={Mail} label="Email" value={transaction.user?.email || "-"} />
          <InfoRow icon={Calendar} label="Date" value={formatDate(transaction.created_at || "")} />
        </CardContent>
      </Card>

      {/* Booking / Trip Card */}
      {hasBooking ? (
        <Card className="border-green-500/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Car className="w-5 h-5 text-green-400" />
              Réservation liée
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <MapPin className="w-5 h-5 text-green-400" />
              <div className="flex-1">
                <p className="font-medium">
                  {transaction.booking?.trip?.departure_name || "?"} → {transaction.booking?.trip?.destination_name || "?"}
                </p>
                <Link
                  href={`/trips?selected=${transaction.booking?.trip_id}`}
                  className="text-sm text-klando-gold hover:underline flex items-center gap-1"
                >
                  Voir le trajet
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
            </div>

            {/* Marge Klando */}
            <div className="grid grid-cols-3 gap-4 p-4 rounded-lg bg-secondary/50">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Payé passager</p>
                <p className="text-lg font-semibold text-green-400">{formatPrice(passengerPaid)}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Prix conducteur</p>
                <p className="text-lg font-semibold text-blue-400">{formatPrice(driverPrice)}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Marge Klando</p>
                <p className="text-lg font-semibold text-klando-gold">{formatPrice(margin)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-yellow-500/30">
          <CardContent className="py-6">
            <div className="flex items-center gap-3 text-yellow-400">
              <AlertTriangle className="w-5 h-5" />
              <div>
                <p className="font-medium">Transaction hors trajet</p>
                <p className="text-sm text-muted-foreground">
                  Cette transaction n&apos;est pas liée à une réservation (top-up, remboursement, etc.)
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dates Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Calendar className="w-5 h-5 text-klando-gold" />
            Historique
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Créée le</p>
              <p>{formatDate(transaction.created_at || "")}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Mise à jour</p>
              <p>{transaction.updated_at ? formatDate(transaction.updated_at) : "-"}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
