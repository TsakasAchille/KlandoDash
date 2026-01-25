"use client";

import { UserListItem } from "@/types/user";
import { formatDate } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Star, Mail, Phone, Calendar, Shield, User } from "lucide-react";
import { UserTripsTable } from "./user-trips-table";

interface UserDetailsProps {
  user: UserListItem;
}

export function UserDetails({ user }: UserDetailsProps) {
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
                className="w-20 h-20 rounded-full object-cover mb-4"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-klando-burgundy flex items-center justify-center text-white text-2xl font-semibold mb-4">
                {(user.display_name || "?").charAt(0).toUpperCase()}
              </div>
            )}
            <h2 className="text-xl font-bold">{user.display_name || "Sans nom"}</h2>
            <p className="text-sm text-muted-foreground">{user.uid}</p>

            {user.rating && (
              <div className="flex items-center gap-1 mt-2">
                <Star className="w-5 h-5 fill-klando-gold text-klando-gold" />
                <span className="font-semibold">{user.rating.toFixed(1)}</span>
                <span className="text-muted-foreground text-sm">
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
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="w-5 h-5 text-klando-gold" />
            Informations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {user.email && (
            <div className="flex items-center gap-3">
              <Mail className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm truncate">{user.email}</span>
            </div>
          )}
          {user.phone_number && (
            <div className="flex items-center gap-3">
              <Phone className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">{user.phone_number}</span>
            </div>
          )}
          {user.created_at && (
            <div className="flex items-center gap-3">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm">
                Inscrit le {formatDate(user.created_at)}
              </span>
            </div>
          )}
          <div className="flex items-center gap-3">
            <Shield className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm">
              Rôle: <span className="font-medium">{user.role || "user"}</span>
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Trips Card */}
      <UserTripsTable userId={user.uid} />
    </div>
  );
}
