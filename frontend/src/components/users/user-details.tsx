"use client";

import { useState } from "react";
import { UserListItem } from "@/types/user";
import { formatDate, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star, Mail, Phone, Calendar, Shield, User, Car, Banknote, ShieldCheck } from "lucide-react";
import Image from "next/image";
import { UserTripsTable } from "./user-trips-table";
import { UserTransactionsTable } from "./user-transactions-table";

interface UserDetailsProps {
  user: UserListItem;
}

type TabValue = "trips" | "transactions";

export function UserDetails({ user }: UserDetailsProps) {
  const [activeTab, setActiveTab] = useState<TabValue>("trips");

  return (
    <div className="space-y-4 sticky top-6">
      {/* Profile Card - More compact */}
      <Card className="border-klando-gold/20 overflow-hidden">
        <div className="bg-gradient-to-r from-klando-burgundy/10 to-transparent p-4 flex items-center gap-4">
          {user.photo_url ? (
            <div className="relative w-12 h-12 flex-shrink-0">
              <Image
                src={user.photo_url}
                alt=""
                fill
                className="rounded-xl object-cover border-2 border-white shadow-sm"
              />
            </div>
          ) : (
            <div className="w-12 h-12 rounded-xl bg-klando-burgundy flex items-center justify-center text-white text-lg font-black flex-shrink-0 shadow-sm">
              {(user.display_name || "?").charAt(0).toUpperCase()}
            </div>
          )}
          <div className="min-w-0">
            <h2 className="text-base font-black uppercase tracking-tight truncate">
              {user.display_name || "Sans nom"}
            </h2>
            <p className="text-[10px] text-muted-foreground font-mono truncate">
              {user.uid}
            </p>
          </div>
        </div>
        
        <CardContent className="p-4 pt-2">
          {user.bio && (
            <p className="text-[11px] italic text-muted-foreground mb-4 line-clamp-2 leading-tight border-l-2 border-klando-gold/30 pl-2 py-0.5">
              &quot;{user.bio}&quot;
            </p>
          )}

          <div className="grid grid-cols-3 gap-2">
            {/* Status */}
            <div className={cn(
              "flex flex-col items-center justify-center py-2 rounded-lg border transition-all",
              user.is_driver_doc_validated
                ? "bg-blue-500/5 border-blue-500/20 text-blue-500"
                : "bg-gray-500/5 border-gray-500/10 text-gray-400 grayscale opacity-60"
            )}>
              <ShieldCheck className="w-4 h-4 mb-1" />
              <span className="text-[8px] font-black uppercase tracking-widest">
                {user.is_driver_doc_validated ? "Vérifié" : "Non vérif."}
              </span>
            </div>

            {/* Note */}
            <div className="flex flex-col items-center justify-center py-2 rounded-lg bg-klando-gold/5 border border-klando-gold/20 text-klando-gold">
              <div className="flex items-center gap-0.5 mb-1">
                <span className="text-xs font-black">
                  {user.rating ? user.rating.toFixed(1) : "-"}
                </span>
                <Star className="w-2.5 h-2.5 fill-current" />
              </div>
              <span className="text-[8px] font-black uppercase tracking-widest">Note</span>
            </div>

            {/* Avis */}
            <div className="flex flex-col items-center justify-center py-2 rounded-lg bg-purple-500/5 border border-purple-500/20 text-purple-400">
              <span className="text-xs font-black mb-1">
                {user.rating_count || 0}
              </span>
              <span className="text-[8px] font-black uppercase tracking-widest">Avis</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Info Card - More compact */}
      <Card className="border-border/40">
        <CardContent className="p-4 space-y-3">
          <div className="space-y-2">
            {user.email && (
              <div className="flex items-center gap-2">
                <Mail className="w-3 h-3 text-muted-foreground" />
                <span className="text-[11px] font-medium truncate">{user.email}</span>
              </div>
            )}
            {user.phone_number && (
              <div className="flex items-center gap-2">
                <Phone className="w-3 h-3 text-muted-foreground" />
                <span className="text-[11px] font-bold font-mono">{user.phone_number}</span>
              </div>
            )}
            {user.created_at && (
              <div className="flex items-center gap-2">
                <Calendar className="w-3 h-3 text-muted-foreground" />
                <span className="text-[11px] text-muted-foreground">
                  Inscrit le {formatDate(user.created_at)}
                </span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Shield className="w-3 h-3 text-muted-foreground" />
              <span className="text-[11px] uppercase font-black text-klando-gold/80">
                {user.role || "user"}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs - Sleek toggle */}
      <div className="flex bg-secondary/30 p-1 rounded-lg border border-border/40">
        <button
          onClick={() => setActiveTab("trips")}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest transition-all",
            activeTab === "trips" 
              ? "bg-white text-klando-burgundy shadow-sm border border-border/20" 
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Car className="w-3 h-3" />
          Trajets
        </button>
        <button
          onClick={() => setActiveTab("transactions")}
          className={cn(
            "flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest transition-all",
            activeTab === "transactions" 
              ? "bg-white text-klando-burgundy shadow-sm border border-border/20" 
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <Banknote className="w-3 h-3" />
          Transactions
        </button>
      </div>

      {/* Tab Content */}
      <div className="max-h-[400px] overflow-auto rounded-lg border border-border/20 scrollbar-thin">
        {activeTab === "trips" ? (
          <UserTripsTable userId={user.uid} />
        ) : (
          <UserTransactionsTable userId={user.uid} />
        )}
      </div>
    </div>
  );
}
