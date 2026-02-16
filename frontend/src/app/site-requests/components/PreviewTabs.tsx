"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar, CheckCircle2 } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { PublicTrip } from "../hooks/useSiteRequestAI";

interface PreviewTabsProps {
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
}

export function PreviewTabs({ publicPending, publicCompleted }: PreviewTabsProps) {
  return (
    <div className="grid md:grid-cols-2 gap-8">
      <div className="space-y-4">
        <div className="flex items-center gap-2 px-1">
          <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
          <h3 className="font-bold uppercase tracking-wider text-sm">Trajets en Direct sur le site</h3>
        </div>
        <div className="space-y-3">
          {publicPending.map((trip) => (
            <Card key={trip.id} className="border-l-4 border-l-klando-gold overflow-hidden">
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 font-bold text-sm">
                      <MapPin className="w-4 h-4 text-klando-gold" />
                      {trip.departure_city} → {trip.arrival_city}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground font-bold">
                      <Calendar className="w-3.5 h-3.5" />
                      {format(new Date(trip.departure_time), "EEE d MMM 'à' HH:mm", { locale: fr })}
                    </div>
                  </div>
                  <Badge variant="outline" className="bg-klando-gold/10 text-klando-gold border-klando-gold/20">LIVE</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      <div className="space-y-4">
        <div className="flex items-center gap-2 px-1">
          <CheckCircle2 className="w-4 h-4 text-green-500" />
          <h3 className="font-bold uppercase tracking-wider text-sm text-muted-foreground">Preuve Sociale (Terminés)</h3>
        </div>
        <div className="space-y-3">
          {publicCompleted.map((trip) => (
            <Card key={trip.id} className="bg-muted/30 border-dashed opacity-80">
              <CardContent className="p-4">
                <div className="flex justify-between items-center">
                  <div className="text-sm font-semibold text-muted-foreground italic">
                    {trip.departure_city} → {trip.arrival_city}
                  </div>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-600 text-[10px]">TERMINÉ</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
