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

interface SiteRequestsClientProps {
  initialRequests: SiteTripRequest[];
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
}

export function SiteRequestsClient({ initialRequests, publicPending, publicCompleted }: SiteRequestsClientProps) {
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  // Sync state with props when server re-renders
  useEffect(() => {
    setRequests(initialRequests);
  }, [initialRequests]);

  const selectedRequest = useMemo(() => 
    selectedRequestId ? requests.find(r => r.id === selectedRequestId) : null
  , [requests, selectedRequestId]);

  const aiMatching = useSiteRequestAI(selectedRequest || null, publicPending, publicCompleted);

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

  return (
    <>
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
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onOpenIA={(id) => setSelectedRequestId(id)}
          />
        </TabsContent>
        
        <TabsContent value="preview" className="space-y-8 outline-none">
          <PreviewTabs publicPending={publicPending} publicCompleted={publicCompleted} />
        </TabsContent>
      </Tabs>

      <MatchingDialog 
        isOpen={!!selectedRequestId}
        onClose={() => setSelectedRequestId(null)}
        selectedRequest={selectedRequest || null}
        {...aiMatching}
      />
    </>
  );
}
