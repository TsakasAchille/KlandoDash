import { useState, useTransition, useEffect, useMemo, useCallback } from "react";
import { SiteTripRequest } from "@/types/site-request";
import { getAIMatchingAction } from "../actions";
import { toast } from "sonner";

export interface PublicTrip {
  id: string;
  departure_city: string;
  arrival_city: string;
  departure_time: string;
  seats_available?: number;
  polyline?: string | null;
  departure_latitude?: number | null;
  departure_longitude?: number | null;
  destination_latitude?: number | null;
  destination_longitude?: number | null;
  origin_dist?: number;
  dest_dist?: number;
}

export function useSiteRequestAI(
  selectedRequest: SiteTripRequest | null,
  publicPending: PublicTrip[],
  publicCompleted: PublicTrip[]
) {
  const [aiLoading, setAiLoading] = useState(false);
  const [localAiResult, setLocalAiResult] = useState<string | null>(null);
  const [actionMatchedTrip, setActionMatchedTrip] = useState<PublicTrip | null>(null);
  const [lastFetchedTripId, setLastFetchedTripId] = useState<string | null>(null);
  const [isAiPending, startAiTransition] = useTransition();

  // Reset local state when switching requests
  useEffect(() => {
    if (selectedRequest?.id !== lastFetchedTripId) {
      setActionMatchedTrip(null);
      setLocalAiResult(null);
      setLastFetchedTripId(null);
    }
  }, [selectedRequest?.id]);

  const handleMatchIA = useCallback(async (force = false) => {
    if (!selectedRequest) return;
    
    setAiLoading(true);
    setLastFetchedTripId(selectedRequest.id);
    
    startAiTransition(async () => {
      try {
        const res = await getAIMatchingAction(
          selectedRequest.id, 
          selectedRequest.origin_city, 
          selectedRequest.destination_city, 
          selectedRequest.desired_date,
          force
        );
        if (res.success) {
          setLocalAiResult(res.text || null);
          if (res.matchedTrip) {
            setActionMatchedTrip(res.matchedTrip as PublicTrip);
          }
        } else {
          toast.error(res.message || "Erreur IA");
        }
      } catch {
        toast.error("Erreur de connexion");
      } finally {
        setAiLoading(false);
      }
    });
  }, [selectedRequest]);

  // Auto-trigger only once per request
  useEffect(() => {
    if (selectedRequest && !aiLoading && !localAiResult && lastFetchedTripId !== selectedRequest.id) {
      handleMatchIA(false);
    }
  }, [selectedRequest?.id, aiLoading, localAiResult, lastFetchedTripId, handleMatchIA]);

  // Parsing AI result
  const { aiComment, aiMessage, matchedTripId } = useMemo(() => {
    const raw = localAiResult || selectedRequest?.ai_recommendation;
    if (!raw) return { aiComment: null, aiMessage: null, matchedTripId: null };
    
    let comment = raw;
    let message = "";
    let tripId = null;

    if (raw.includes('[MESSAGE]')) {
      const parts = raw.split('[MESSAGE]');
      comment = parts[0].replace('[COMMENTAIRE]', '').trim();
      message = parts[1]?.trim() || '';
    }

    const tripIdMatch = raw.match(/\[TRIP_ID\][:\s]*([A-Za-z0-9-]+)/i);
    if (tripIdMatch) {
      tripId = tripIdMatch[1].trim();
    } else {
      const globalMatch = raw.match(/TRIP-[A-Za-z0-9-]+/);
      if (globalMatch) tripId = globalMatch[0].trim();
    }

    return { 
      aiComment: comment.replace('[COMMENTAIRE]', '').trim(), 
      aiMessage: message,
      matchedTripId: tripId
    };
  }, [localAiResult, selectedRequest?.ai_recommendation]);

  const matchedTrip = useMemo(() => {
    // Priority to data directly returned by the server action (contains polyline & distances)
    if (actionMatchedTrip) return actionMatchedTrip;
    
    // Fallback to local search in public lists
    if (!matchedTripId) return null;
    const normalize = (id: string) => id.toUpperCase().replace('TRIP-', '');
    const target = normalize(matchedTripId);
    return publicPending.find(t => normalize(t.id) === target) || 
           publicCompleted.find(t => normalize(t.id) === target) || null;
  }, [matchedTripId, publicPending, publicCompleted, actionMatchedTrip]);

  const processedComment = useMemo(() => 
    aiComment ? aiComment.replace(/([^ \n])\n([^ \n])/g, '$1  \n$2') : "_Analyse en attente..._"
  , [aiComment]);

  return {
    aiLoading,
    isAiPending,
    aiMessage,
    matchedTrip,
    processedComment,
    handleMatchIA,
    localAiResult
  };
}
