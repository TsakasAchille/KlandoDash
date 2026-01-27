"use client";

import { useState } from "react";
import { UserListItem } from "@/types/user";
import { formatDate, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star, Mail, Phone, Calendar, Shield, User, Car, Banknote } from "lucide-react";
import { UserTripsTable } from "./user-trips-table";
import { UserTransactionsTable } from "./user-transactions-table";

interface UserDetailsProps {
  user: UserListItem;
}

type TabValue = "trips" | "transactions";

export function UserDetails({ user }: UserDetailsProps) {
  const [activeTab, setActiveTab] = useState<TabValue>("trips");

  return (
    <div className="space-y-4">
      {/* Profile Card */}
      <Card className="border-klando-gold/30">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center text-center">
            {user.photo_url ? (
              <img
                src={user.photo_url}
                alt=""
                className="w-16 h-16 sm:w-20 sm:h-20 rounded-full object-cover mb-4"
              />
            ) : (
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-klando-burgundy flex items-center justify-center text-white text-xl sm:text-2xl font-semibold mb-4">
                {(user.display_name || "?").charAt(0).toUpperCase()}
              </div>
            )}
            <h2 className="text-lg sm:text-xl font-bold">{user.display_name || "Sans nom"}</h2>
            <p className="text-xs sm:text-sm text-muted-foreground break-all">{user.uid}</p>

            {user.rating && (
              <div className="flex items-center gap-1 mt-2">
                <Star className="w-4 h-4 sm:w-5 sm:h-5 fill-klando-gold text-klando-gold" />
                <span className="font-semibold text-sm sm:text-base">{user.rating.toFixed(1)}</span>
                <span className="text-muted-foreground text-xs sm:text-sm">
                  ({user.rating_count || 0} avis)
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base sm:text-lg flex items-center gap-2">
            <User className="w-4 h-4 sm:w-5 sm:h-5 text-klando-gold" />
            Informations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {user.email && (
              <div className="flex items-center gap-3">
                <Mail className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <span className="text-sm truncate break-all">{user.email}</span>
              </div>
            )}
            {user.phone_number && (
              <div className="flex items-center gap-3">
                <Phone className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <span className="text-sm">{user.phone_number}</span>
              </div>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {user.created_at && (
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <span className="text-sm">
                  Inscrit le {formatDate(user.created_at)}
                </span>
              </div>
            )}
            <div className="flex items-center gap-3">
              <Shield className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <span className="text-sm">
                Rôle: <span className="font-medium">{user.role || "user"}</span>
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === "trips" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("trips")}
          className={cn(
            "flex items-center gap-2",
            activeTab === "trips" && "bg-klando-burgundy hover:bg-klando-burgundy/90"
          )}
        >
          <Car className="w-4 h-4" />
          Trajets
        </Button>
        <Button
          variant={activeTab === "transactions" ? "default" : "outline"}
          size="sm"
          onClick={() => setActiveTab("transactions")}
          className={cn(
            "flex items-center gap-2",
            activeTab === "transactions" && "bg-klando-burgundy hover:bg-klando-burgundy/90"
          )}
        >
          <Banknote className="w-4 h-4" />
          Transactions
        </Button>
      </div>

      {/* Tab Content */}
      {activeTab === "trips" ? (
        <UserTripsTable userId={user.uid} />
      ) : (
        <UserTransactionsTable userId={user.uid} />
      )}
    </div>
  );
}
