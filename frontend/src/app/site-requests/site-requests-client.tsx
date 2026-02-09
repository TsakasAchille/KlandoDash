"use client";

import { useState } from "react";
import { SiteTripRequest, SiteTripRequestStatus } from "@/types/site-request";
import { SiteRequestTable } from "@/components/site-requests/site-request-table";
import { updateSiteTripRequest } from "@/lib/queries/site-requests";
import { useRouter } from "next/navigation";
import { toast } from "sonner"; // Assuming sonner is used, if not I'll check

interface SiteRequestsClientProps {
  initialRequests: SiteTripRequest[];
}

export function SiteRequestsClient({ initialRequests }: SiteRequestsClientProps) {
  const [requests, setRequests] = useState<SiteTripRequest[]>(initialRequests);
  const router = useRouter();

  const handleUpdateStatus = async (id: string, status: SiteTripRequestStatus) => {
    const success = await updateSiteTripRequest(id, { status });
    
    if (success) {
      setRequests(prev => 
        prev.map(r => r.id === id ? { ...r, status } : r)
      );
      toast.success("Statut mis à jour avec succès");
      router.refresh();
    } else {
      toast.error("Erreur lors de la mise à jour du statut");
    }
  };

  return (
    <div className="space-y-6">
      <SiteRequestTable 
        requests={requests} 
        onUpdateStatus={handleUpdateStatus} 
      />
    </div>
  );
}
