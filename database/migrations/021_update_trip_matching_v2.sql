-- ==============================================================================
-- Migration: Update Trip Matching Logic (V2 - Direction Sensitive)
-- Description: Ensures matching finds trips where departure is near departure
--              AND arrival is near arrival (prevents inverted matches).
-- ==============================================================================

-- 1. Redefinition of the matching function with strict directional checks
CREATE OR REPLACE FUNCTION public.find_matching_trips(
    p_request_id uuid,
    p_radius_km double precision DEFAULT 5.0
) RETURNS TABLE (
    trip_id text,
    departure_city text,
    arrival_city text,
    departure_time timestamp with time zone,
    seats_available bigint,
    origin_distance double precision,
    destination_distance double precision,
    total_proximity_score double precision
) AS $$
DECLARE
    r_origin_lat double precision;
    r_origin_lng double precision;
    r_dest_lat double precision;
    r_dest_lng double precision;
BEGIN
    -- Get request coordinates from site_trip_requests
    SELECT origin_lat, origin_lng, destination_lat, destination_lng
    INTO r_origin_lat, r_origin_lng, r_dest_lat, r_dest_lng
    FROM public.site_trip_requests 
    WHERE id = p_request_id;

    -- Safety check: return nothing if coordinates are missing
    IF r_origin_lat IS NULL OR r_dest_lat IS NULL THEN 
        RETURN; 
    END IF;

    RETURN QUERY
    SELECT 
        t.trip_id, 
        t.departure_name, 
        t.destination_name, 
        t.departure_schedule, 
        t.seats_available,
        -- Distance between Client Origin and Trip Origin
        public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) as origin_dist,
        -- Distance between Client Destination and Trip Destination
        public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude) as dest_dist,
        -- Cumulative score (lower is better)
        (public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) + 
         public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude)) as score
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        -- CRITICAL: Both points must be within radius to be a valid match
        -- This prevents "inverted" matches (Start matched with End)
        AND public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) <= p_radius_km
        AND public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude) <= p_radius_km
    ORDER BY 
        score ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 2. Grant permissions
GRANT EXECUTE ON FUNCTION public.find_matching_trips(uuid, double precision) TO authenticated;
GRANT EXECUTE ON FUNCTION public.find_matching_trips(uuid, double precision) TO service_role;

-- 3. Notify schema reload
NOTIFY pgrst, 'reload schema';

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'Fonction find_matching_trips (V2) mise à jour avec succès.';
END $$;
