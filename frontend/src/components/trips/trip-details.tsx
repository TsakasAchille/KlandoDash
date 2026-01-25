"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { Trip } from "@/types/trip";
import { formatDate, formatDistance, formatPrice } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MapPin, Clock, Users, Banknote, Car, Leaf, ExternalLink, Map } from "lucide-react";

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const TripRouteMap = dynamic(
  () => import("./trip-route-map").then((mod) => mod.TripRouteMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[300px] rounded-lg bg-secondary/50 flex items-center justify-center">
        <span className="text-muted-foreground">Chargement de la carte...</span>
      </div>
    ),
  }
);

interface TripDetailsProps {
  trip: Trip;
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color = "text-klando-gold",
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50">
      <Icon className={`w-5 h-5 ${color}`} />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="font-semibold">{value}</p>
      </div>
    </div>
  );
}

export function TripDetails({ trip }: TripDetailsProps) {
  const occupationRate = Math.round(
    (trip.passengers.length / trip.total_seats) * 100
  );
  const fuelEstimate = (trip.trip_distance * 0.07).toFixed(1);
  const co2Saved = (trip.trip_distance * 0.12 * trip.passengers.length).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Route Card */}
      <Card className="border-klando-gold/30">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <MapPin className="w-5 h-5 text-klando-gold" />
            Itinéraire
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">Départ</p>
              <p className="font-semibold text-green-400">{trip.departure_city}</p>
              <p className="text-xs text-muted-foreground">{trip.departure_address}</p>
            </div>
            <div className="text-2xl text-klando-gold">→</div>
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">Arrivée</p>
              <p className="font-semibold text-red-400">{trip.destination_city}</p>
              <p className="text-xs text-muted-foreground">{trip.destination_address}</p>
            </div>
          </div>

          {/* Map */}
          {trip.trip_polyline ? (
            <TripRouteMap
              polylineString={trip.trip_polyline}
              departureName={trip.departure_city}
              destinationName={trip.destination_city}
            />
          ) : (
            <div className="w-full h-[200px] rounded-lg bg-secondary/50 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <Map className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Tracé non disponible</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          icon={Car}
          label="Distance"
          value={formatDistance(trip.trip_distance)}
        />
        <MetricCard
          icon={Clock}
          label="Départ"
          value={formatDate(trip.departure_schedule)}
        />
        <MetricCard
          icon={Users}
          label="Occupation"
          value={`${trip.passengers.length}/${trip.total_seats} (${occupationRate}%)`}
        />
        <MetricCard
          icon={Banknote}
          label="Prix/place"
          value={formatPrice(trip.price_per_seat)}
          color="text-green-400"
        />
      </div>

      {/* Environmental & Financial */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-400" />
              Impact environnemental
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">CO₂ économisé</span>
              <span className="font-semibold text-green-400">{co2Saved} kg</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Carburant estimé</span>
              <span className="font-semibold">{fuelEstimate} L</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Banknote className="w-5 h-5 text-klando-gold" />
              Informations financières
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Revenu conducteur</span>
              <span className="font-semibold">
                {formatPrice(trip.viator_income || 0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Total trajet</span>
              <span className="font-semibold text-klando-gold">
                {formatPrice(trip.price_per_seat * trip.passengers.length)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Driver & Passengers */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Users className="w-5 h-5 text-klando-gold" />
            Participants
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-2">Conducteur</p>
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 rounded-lg bg-klando-burgundy/20 border border-klando-burgundy/30 gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-klando-burgundy flex items-center justify-center text-white font-semibold flex-shrink-0">
                    {trip.driver_name.charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium truncate">{trip.driver_name}</p>
                    <p className="text-xs text-muted-foreground truncate">{trip.driver_id}</p>
                  </div>
                </div>
                <Link href={`/users?selected=${trip.driver_id}`} className="w-full sm:w-auto">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full min-h-[44px] sm:min-h-[32px] sm:w-auto"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    <span className="hidden sm:inline">Voir profil</span>
                    <span className="sm:hidden">Profil</span>
                  </Button>
                </Link>
              </div>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Passagers ({trip.passengers.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {trip.passengers.map((passengerId) => (
                  <span
                    key={passengerId}
                    className="px-3 py-1 rounded-full bg-secondary text-sm"
                  >
                    {passengerId}
                  </span>
                ))}
                {trip.passengers.length === 0 && (
                  <span className="text-muted-foreground text-sm">
                    Aucun passager
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
