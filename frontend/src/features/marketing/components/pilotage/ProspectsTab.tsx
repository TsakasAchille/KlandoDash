"use client";

import { useState } from "react";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { updateRequestStatusAction, scanRequestMatchesAction } from "@/app/site-requests/actions";
import { toast } from "sonner";

interface ProspectsTabProps {
  requests: SiteTripRequest[];
  onRequestsUpdate: (newRequests: SiteTripRequest[]) => void;
  onSelectOnMap: (id: string) => void;
  onOpenIA: (id: string) => void;
}

export function ProspectsTab({ 
  requests, 
  onRequestsUpdate, 
  onSelectOnMap,
  onOpenIA 
}: ProspectsTabProps) {
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [scanningId, setScanningId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("all");

  const handleUpdateStatus = async (id: string, status: SiteTripRequestStatus) => {
    setUpdatingId(id);
    const result = await updateRequestStatusAction(id, status);
    if (result.success) {
      toast.success("Statut mis à jour.");
      onRequestsUpdate(requests.map(r => r.id === id ? { ...r, status } : r));
    }
    setUpdatingId(null);
  };

  const handleScanRequest = async (id: string) => {
    setScanningId(id);
    const result = await scanRequestMatchesAction(id, 30);
    if (result.success) {
      toast.success(`Scan terminé : ${result.count} trajets analysés.`);
    }
    setScanningId(null);
  };

  return (
    <div className="outline-none animate-in fade-in duration-500">
      <SiteRequestTable 
        requests={requests} 
        onUpdateStatus={handleUpdateStatus}
        updatingId={updatingId}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        onOpenIA={onOpenIA}
        onScan={handleScanRequest}
        onSelectOnMap={onSelectOnMap}
        scanningId={scanningId}
      />
    </div>
  );
}
