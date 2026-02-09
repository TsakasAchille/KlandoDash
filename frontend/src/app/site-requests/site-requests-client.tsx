"use client";

import { useState, useTransition } from "react";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { updateRequestStatusAction } from "./actions";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Calendar, Users, CheckCircle2, Globe } from "lucide-react";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

interface SiteRequestsClientProps {
  initialRequests: SiteTripRequest[];
  publicPending: any[];
  publicCompleted: any[];
}

export function SiteRequestsClient({ initialRequests, publicPending, publicCompleted }: SiteRequestsClientProps) {
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const handleUpdateStatus = (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    startTransition(async () => {
      // Optimistic update
      setRequests(prev => prev.map(r => (r.id === id ? { ...r, status } : r)));
      
      const result = await updateRequestStatusAction(id, status);

      if (result.success) {
        toast.success("Statut mis à jour avec succès !");
      } else {
        toast.error(result.message || "Erreur lors de la mise à jour.");
        // Revert optimistic update on failure
        setRequests(initialRequests); 
      }
      
      // No need for router.refresh() as revalidatePath in action handles it
      setUpdatingId(null);
    });
  };

  return (
    <Tabs defaultValue="requests" className="space-y-6">
      <TabsList className="bg-muted/50 p-1">
        <TabsTrigger value="requests">Demandes Clients</TabsTrigger>
        <TabsTrigger value="preview">Aperçu Public (Site)</TabsTrigger>
      </TabsList>

      <TabsContent value="requests" className="space-y-6 outline-none">
        <SiteRequestTable 
          requests={requests} 
          onUpdateStatus={handleUpdateStatus}
          updatingId={updatingId} 
        />
      </TabsContent>
      
      <TabsContent value="preview" className="space-y-8 outline-none">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Section Trajets en Direct */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 px-1">
              <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
              <h3 className="font-bold uppercase tracking-wider text-sm">Trajets en Direct sur le site</h3>
            </div>
            
            <div className="space-y-3">
              {publicPending.length > 0 ? (
                publicPending.map((trip) => (
                  <Card key={trip.id} className="border-l-4 border-l-klando-gold overflow-hidden">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-start">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2 font-bold text-sm">
                            <MapPin className="w-4 h-4 text-klando-gold" />
                            {trip.departure_city} → {trip.arrival_city}
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3.5 h-3.5" />
                              {format(new Date(trip.departure_time), "EEE d MMM 'à' HH:mm", { locale: fr })}
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-3.5 h-3.5" />
                              {trip.seats_available} places
                            </div>
                          </div>
                        </div>
                        <Badge variant="outline" className="bg-klando-gold/10 text-klando-gold border-klando-gold/20">
                          LIVE
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <div className="text-center py-10 bg-muted/20 rounded-xl border border-dashed">
                  <p className="text-sm text-muted-foreground">Aucun trajet en direct affiché</p>
                </div>
              )}
            </div>
          </div>

          {/* Section Trajets Terminés */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 px-1">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <h3 className="font-bold uppercase tracking-wider text-sm text-muted-foreground">Preuve Sociale (Terminés)</h3>
            </div>

            <div className="space-y-3">
              {publicCompleted.length > 0 ? (
                publicCompleted.map((trip) => (
                  <Card key={trip.id} className="bg-muted/30 border-dashed opacity-80">
                    <CardContent className="p-4">
                      <div className="flex justify-between items-center">
                        <div className="space-y-1">
                          <div className="text-sm font-semibold text-muted-foreground line-through decoration-muted-foreground/30">
                            {trip.departure_city} → {trip.arrival_city}
                          </div>
                          <div className="text-[10px] text-muted-foreground flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            Effectué le {format(new Date(trip.departure_time), "d MMM yyyy", { locale: fr })}
                          </div>
                        </div>
                        <Badge variant="secondary" className="bg-green-500/10 text-green-600 border-none text-[10px]">
                          TERMINÉ
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <div className="text-center py-10 bg-muted/10 rounded-xl border border-dashed">
                  <p className="text-sm text-muted-foreground text-muted-foreground/50">Aucun trajet terminé récent</p>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex gap-3 items-start">
          <div className="p-1 bg-blue-500 rounded text-white mt-0.5">
            <Globe className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-blue-900">Note d'intégration</h4>
            <p className="text-xs text-blue-700 leading-relaxed mt-1">
              Ces données proviennent des vues SQL <code className="bg-blue-100 px-1 rounded">public_pending_trips</code> et <code className="bg-blue-100 px-1 rounded">public_completed_trips</code>. 
              Elles sont exposées publiquement sur le site vitrine pour attirer les clients. Seuls les trajets avec assez de places et dont la date n'est pas passée sont affichés en "Direct".
            </p>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
}
