"use client";

import { useState, useTransition, useEffect, useMemo } from "react";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { updateRequestStatusAction } from "./actions";
import { toast } from "sonner";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSiteRequestAI, PublicTrip } from "./hooks/useSiteRequestAI";
import { MatchingDialog } from "./components/MatchingDialog";
import { PreviewTabs } from "./components/PreviewTabs";
import { SiteRequestsMap } from "./components/SiteRequestsMap";
import { TripMapItem } from "@/types/trip";
import { useRouter, useSearchParams } from "next/navigation";
import { scanRequestMatchesAction } from "./actions";
import { ScanResultsDialog } from "./components/ScanResultsDialog";

interface SiteRequestsClientProps {
  initialRequests: SiteTripRequest[];
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
  tripsForMap: TripMapItem[];
}

export function SiteRequestsClient({ initialRequests, publicPending, publicCompleted, tripsForMap }: SiteRequestsClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get("tab") || "requests";

  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(searchParams.get("id") || null);
  const [aiDialogOpenId, setAiDialogOpenId] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  // SCAN STATE
  const [scanningId, setScanningId] = useState<string | null>(null);

  // Sync state with props when server re-renders
  useEffect(() => {
    setRequests(initialRequests);
  }, [initialRequests]);

  const handleScan = async (id: string) => {
    setScanningId(id);
    try {
      // On scanne large (30km) pour remplir les onglets 5/10/15
      const result = await scanRequestMatchesAction(id, 30);
      if (result.success) {
        toast.success(`Scan terminé : ${result.count} trajets analysés.`);
      }
    } catch (error) {
      toast.error("Erreur lors du scan.");
    } finally {
      setScanningId(null);
    }
  };

  const handleTabChange = (value: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set("tab", value);
    router.replace(url.pathname + url.search, { scroll: false });
  };

  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) : null
  , [requests, selectedRequestId]);

  const aiRequest = useMemo(() => 
    aiDialogOpenId ? requests.find(r => r.id === aiDialogOpenId) : null
  , [requests, aiDialogOpenId]);

  const aiMatching = useSiteRequestAI(aiRequest || null, publicPending, publicCompleted);

  const handleUpdateStatus = (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    startTransition(async () => {
      setRequests(prev => prev.map(r => (r.id === id ? { ...r, status } : r)));
      const result = await updateRequestStatusAction(id, status);
      if (!result.success) {
        toast.error(result.message || "Erreur lors de la mise à jour.");
        setRequests(initialRequests); 
      }
      setUpdatingId(null);
    });
  };

  const handleSelectRequestOnMap = (id: string) => {
    setSelectedRequestId(id);
    const url = new URL(window.location.href);
    if (id) url.searchParams.set("id", id);
    else url.searchParams.delete("id");
    router.replace(url.pathname + url.search, { scroll: false });
  };

  return (
    <>
      <Tabs value={tabParam} onValueChange={handleTabChange} className="space-y-6">
        <TabsList className="bg-muted/50 p-1">
          <TabsTrigger value="requests">Demandes Clients</TabsTrigger>
          <TabsTrigger value="map">Carte Interactive</TabsTrigger>
          <TabsTrigger value="preview">Aperçu Public (Site)</TabsTrigger>
        </TabsList>

        <TabsContent value="requests" className="space-y-6 outline-none">
          <SiteRequestTable 
            requests={requests} 
            onUpdateStatus={handleUpdateStatus}
            updatingId={updatingId}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onOpenIA={(id) => setAiDialogOpenId(id)}
            onScan={handleScan}
            scanningId={scanningId}
          />
        </TabsContent>

        <TabsContent value="map" className="space-y-6 outline-none">
          <SiteRequestsMap 
            requests={requests}
            trips={tripsForMap}
            selectedRequestId={selectedRequestId}
            onSelectRequest={handleSelectRequestOnMap}
            onScan={handleScan}
            scanningId={scanningId}
          />
        </TabsContent>
        
        <TabsContent value="preview" className="space-y-8 outline-none">
          <PreviewTabs publicPending={publicPending} publicCompleted={publicCompleted} />
        </TabsContent>
      </Tabs>

      <MatchingDialog 
        isOpen={!!aiDialogOpenId}
        onClose={() => setAiDialogOpenId(null)}
        selectedRequest={aiRequest || null}
        {...aiMatching}
      />
    </>
  );
}
