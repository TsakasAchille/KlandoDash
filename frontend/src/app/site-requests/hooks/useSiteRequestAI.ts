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

  // Reset matched trip when changing selection
  useEffect(() => {
    setActionMatchedTrip(null);
    setLastFetchedTripId(null);
    setLocalAiResult(null);
  }, [selectedRequest?.id]);

  // Sync local AI result when data updates from server
  useEffect(() => {
    if (selectedRequest?.ai_recommendation) {
      setLocalAiResult(selectedRequest.ai_recommendation);
    }
  }, [selectedRequest?.ai_recommendation]);

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
          console.log("Server Matched Trip Data:", res.matchedTrip);
          if (res.matchedTrip) {
            setActionMatchedTrip(res.matchedTrip as PublicTrip);
          }
        } else {
          toast.error(res.message || "Erreur IA");
        }
      } catch {
        toast.error("Erreur de connexion IA");
      } finally {
        setAiLoading(false);
      }
    });
  }, [selectedRequest]);

  // Auto-trigger AI if opening a request with no analysis
  useEffect(() => {
    if (selectedRequest && !selectedRequest.ai_recommendation && !aiLoading && !localAiResult) {
      handleMatchIA(false);
    }
  }, [selectedRequest, aiLoading, localAiResult, handleMatchIA]);

  // Also trigger fetch if we have an AI recommendation but haven't fetched details yet
  useEffect(() => {
    if (selectedRequest?.ai_recommendation && !aiLoading && lastFetchedTripId !== selectedRequest.id) {
      handleMatchIA(false); // This will use cache but fetch the trip details
    }
  }, [selectedRequest?.id, selectedRequest?.ai_recommendation, aiLoading, lastFetchedTripId, handleMatchIA]);

  // Parsing AI result
  const { aiComment, aiMessage, matchedTripId } = useMemo(() => {
    const raw = localAiResult || selectedRequest?.ai_recommendation;
    if (!raw) return { aiComment: null, aiMessage: null, matchedTripId: null };
    
    let comment = raw;
    let message = null;
    let tripId = null;

    if (raw.includes('[MESSAGE]')) {
      const parts = raw.split('[MESSAGE]');
      comment = parts[0].replace('[COMMENTAIRE]', '').trim();
      message = parts[1]?.trim() || '';
    }

    if (comment.includes('[TRIP_ID]')) {
      const parts = comment.split('[TRIP_ID]');
      comment = parts[0].trim();
      const tripIdPart = parts[1]?.split('\n')[0]?.trim();
      tripId = tripIdPart && tripIdPart !== 'NONE' ? tripIdPart : null;
    } else if (raw.includes('[TRIP_ID]')) {
      const tripIdMatch = raw.match(/\[TRIP_ID\]\s*([A-Z0-9-]+)/);
      tripId = tripIdMatch?.[1] && tripIdMatch[1] !== 'NONE' ? tripIdMatch[1] : null;
    }

    console.log("AI Raw Analysis:", raw.substring(0, 100) + "...");
    console.log("Structured TripID Found:", tripId);

    // Fallback: If still no tripId, try to find a pattern like TRIP-XXXX in the comment
    if (!tripId || tripId === 'NONE') {
      const fallbackMatch = comment.match(/TRIP-[A-Z0-9]+/i);
      if (fallbackMatch) {
        tripId = fallbackMatch[0].toUpperCase().trim();
        console.log("Fallback TripID Found in Text:", tripId);
      }
    }

    return { 
      aiComment: comment.replace('[COMMENTAIRE]', '').trim(), 
      aiMessage: message,
      matchedTripId: tripId
    };
  }, [localAiResult, selectedRequest?.ai_recommendation]);

  const matchedTrip = useMemo(() => {
    if (actionMatchedTrip) {
      console.log("Using trip from ActionMatchedTrip:", actionMatchedTrip.id);
      return actionMatchedTrip;
    }
    if (!matchedTripId) return null;
    
    const found = publicPending.find(t => t.id === matchedTripId) || 
                  publicCompleted.find(t => t.id === matchedTripId);
    
    console.log("Search for TripID", matchedTripId, "in public lists:", found ? "FOUND" : "NOT FOUND");
    return found || null;
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
