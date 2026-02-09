"use client";

import { useState } from "react";
import { UserListItem } from "@/types/user";
import { formatDate, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star, Mail, Phone, Calendar, Shield, User, Car, Banknote, ShieldCheck } from "lucide-react";
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
            {user.bio && (
              <p className="text-sm italic text-muted-foreground mt-1 max-w-[250px] line-clamp-3">
                "{user.bio}"
              </p>
            )}
            <p className="text-[10px] sm:text-xs text-muted-foreground break-all mt-1">{user.uid}</p>

            <div className="flex items-center justify-center gap-3 sm:gap-6 mt-6 w-full">
              {/* Profil Vérifié */}
              <div 
                className={cn(
                  "flex flex-col items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full border transition-all",
                  user.is_driver_doc_validated
                    ? "bg-blue-500/10 border-blue-500/30 text-blue-500"
                    : "bg-gray-500/5 border-gray-500/10 text-gray-400 grayscale opacity-50"
                )}
                title={user.is_driver_doc_validated ? "Documents validés" : "Non vérifié"}
              >
                <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6 mb-1" />
                <span className="text-[10px] sm:text-xs font-medium leading-none text-center px-1">
                  {user.is_driver_doc_validated ? "Vérifié" : "Non vérif."}
                </span>
              </div>

              {/* Note Moyenne */}
              <div className="flex flex-col items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-klando-gold/10 border border-klando-gold/30 text-klando-gold">
                <div className="flex items-center gap-0.5 mb-1">
                  <span className="text-sm sm:text-lg font-bold leading-none">
                    {user.rating ? user.rating.toFixed(1) : "-"}
                  </span>
                  <Star className="w-3 h-3 sm:w-4 sm:h-4 fill-current" />
                </div>
                <span className="text-[10px] sm:text-xs font-medium leading-none text-center">Note</span>
              </div>

              {/* Nombre d'avis */}
              <div className="flex flex-col items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-400">
                <span className="text-sm sm:text-lg font-bold leading-none mb-1">
                  {user.rating_count || 0}
                </span>
                <span className="text-[10px] sm:text-xs font-medium leading-none text-center">Avis</span>
              </div>
            </div>
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
              <User className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <span className="text-sm">
                Genre: <span className="font-medium">{user.gender || "Non spécifié"}</span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <span className="text-sm">
                Né(e) le: <span className="font-medium">{user.birth ? formatDate(user.birth) : "Non spécifié"}</span>
              </span>
            </div>
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
