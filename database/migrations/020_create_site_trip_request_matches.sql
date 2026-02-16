-- ==============================================================================
-- Migration: Create Site Trip Request Matches Table
-- Description: Persists scanning results between client requests and available trips.
-- ==============================================================================

CREATE TABLE IF NOT EXISTS public.site_trip_request_matches (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    request_id uuid NOT NULL REFERENCES public.site_trip_requests(id) ON DELETE CASCADE,
    trip_id text NOT NULL REFERENCES public.trips(trip_id) ON DELETE CASCADE,
    proximity_score double precision, -- Total distance from origin + distance from destination
    origin_distance double precision,
    destination_distance double precision,
    created_at timestamp with time zone DEFAULT now(),
    
    -- Unicité pour éviter les doublons pour une même paire demande/trajet
    UNIQUE(request_id, trip_id)
);

-- Index pour la performance
CREATE INDEX IF NOT EXISTS idx_matches_request_id ON public.site_trip_request_matches(request_id);
CREATE INDEX IF NOT EXISTS idx_matches_trip_id ON public.site_trip_request_matches(trip_id);

-- Enable RLS
ALTER TABLE public.site_trip_request_matches ENABLE ROW LEVEL SECURITY;

-- Allow dashboard users to view and manage matches
CREATE POLICY "Allow dashboard users to manage matches" 
ON public.site_trip_request_matches 
FOR ALL 
TO authenticated 
USING (true)
WITH CHECK (true);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.site_trip_request_matches TO authenticated;
GRANT SELECT ON public.site_trip_request_matches TO service_role;

-- Commentaire de succès
DO $$ 
BEGIN 
    RAISE NOTICE 'Table site_trip_request_matches créée avec succès';
END $$;
