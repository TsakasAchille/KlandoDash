"use client";

import Link from "next/link";
import { X, User, Users, MapPin, Calendar, Car, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TripMapItem } from "@/types/trip";
import { formatDate, formatPrice } from "@/lib/utils";
import { cn } from "@/lib/utils";

// Badge de statut
const statusStyles: Record<string, string> = {
  ACTIVE: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  COMPLETED: "bg-green-500/20 text-green-400 border-green-500/30",
  PENDING: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  CANCELLED: "bg-red-500/20 text-red-400 border-red-500/30",
  ARCHIVED: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};

interface TripMapPopupProps {
  trip: TripMapItem;
  onClose: () => void;
}

export function TripMapPopup({ trip, onClose }: TripMapPopupProps) {
  return (
    <Card className="absolute top-4 right-4 w-80 z-[1000] bg-klando-dark border-gray-700 shadow-xl">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-klando-gold">
            Détails du trajet
          </CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 text-white">
        {/* Itinéraire */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-green-500 flex-shrink-0" />
            <span className="text-sm text-white truncate">{trip.departure_name || "N/A"}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-red-500 flex-shrink-0" />
            <span className="text-sm text-white truncate">{trip.destination_name || "N/A"}</span>
          </div>
        </div>

        {/* Infos */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-xs text-white">{formatDate(trip.departure_schedule || "")}</span>
          </div>
          <div className="flex items-center gap-2">
            <Car className="w-4 h-4 text-gray-400" />
            <span className="text-white">{trip.seats_available || 0}/{trip.seats_published || 0} places</span>
          </div>
        </div>

        {/* Prix + Status */}
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-klando-gold">
            {formatPrice(trip.passenger_price || 0)}
          </span>
          <span
            className={cn(
              "px-2 py-1 text-xs rounded border",
              statusStyles[trip.status || "ACTIVE"] || statusStyles.ACTIVE
            )}
          >
            {trip.status || "N/A"}
          </span>
        </div>

        {/* Conducteur */}
        {trip.driver && (
          <div className="border-t border-gray-700 pt-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center overflow-hidden">
                  {trip.driver.photo_url ? (
                    <img
                      src={trip.driver.photo_url}
                      alt={trip.driver.display_name || ""}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-xs text-white">
                      {trip.driver.display_name?.charAt(0) || "?"}
                    </span>
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{trip.driver.display_name || "N/A"}</p>
                  <p className="text-xs text-gray-400">
                    {trip.driver.rating ? `⭐ ${trip.driver.rating.toFixed(1)}` : "N/A"}
                  </p>
                </div>
              </div>
              <Link href={`/users?selected=${trip.driver.uid}`}>
                <Button variant="outline" size="sm" className="text-xs border-gray-600 text-black hover:bg-klando-burgundy hover:border-klando-burgundy hover:text-white">
                  <User className="w-3 h-3 mr-1" />
                  Profil
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Passagers */}
        {trip.passengers.length > 0 && (
          <div className="border-t border-gray-700 pt-3">
            <p className="text-sm text-white mb-2">
              <Users className="w-4 h-4 inline mr-1" />
              {trip.passengers.length} passager(s)
            </p>
            <div className="flex flex-wrap gap-2">
              {trip.passengers.map((p) => (
                <Link key={p.uid} href={`/users?selected=${p.uid}`}>
                  <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center overflow-hidden cursor-pointer hover:ring-2 ring-klando-gold transition-all">
                    {p.photo_url ? (
                      <img
                        src={p.photo_url}
                        alt={p.display_name || ""}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-[10px] text-white">
                        {p.display_name?.charAt(0) || "?"}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="border-t border-gray-700 pt-3">
          <Link href={`/trips?selected=${trip.trip_id}`}>
            <Button className="w-full bg-klando-burgundy hover:bg-klando-burgundy/80 text-white">
              <ExternalLink className="w-4 h-4 mr-2" />
              Voir page trajet
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
