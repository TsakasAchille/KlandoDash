-- Migration: Upgrade Trip Matching to PostGIS (V3)
-- Description: Uses PostGIS geography for high precision and performance.
--              Matches passengers where both start and end are within radius of driver's start and end.

-- 1. Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Add geography columns for indexing (if not using dynamic casting)
-- For this small/medium scale, dynamic casting ST_MakePoint is very fast.
-- But let's add indexes on existing lat/lng if they don't exist.
CREATE INDEX IF NOT EXISTS idx_trips_departure_coords ON public.trips USING GIST (ST_SetSRID(ST_MakePoint(departure_longitude, departure_latitude), 4326)::geography);
CREATE INDEX IF NOT EXISTS idx_trips_destination_coords ON public.trips USING GIST (ST_SetSRID(ST_MakePoint(destination_longitude, destination_latitude), 4326)::geography);

-- 3. Redefine the main matching function
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
    total_proximity_score double precision,
    match_type text
) AS $$
DECLARE
    r_origin geography(Point, 4326);
    r_dest geography(Point, 4326);
    v_radius_meters double precision;
BEGIN
    -- Convert KM to meters for PostGIS geography
    v_radius_meters := p_radius_km * 1000.0;

    -- Get request coordinates and cast to geography
    SELECT 
        ST_SetSRID(ST_MakePoint(origin_lng, origin_lat), 4326)::geography,
        ST_SetSRID(ST_MakePoint(destination_lng, destination_lat), 4326)::geography
    INTO r_origin, r_dest
    FROM public.site_trip_requests 
    WHERE id = p_request_id;

    -- Safety check
    IF r_origin IS NULL OR r_dest IS NULL THEN 
        RETURN; 
    END IF;

    RETURN QUERY
    SELECT 
        t.trip_id, 
        t.departure_name, 
        t.destination_name, 
        t.departure_schedule, 
        t.seats_available,
        -- Distance in Meters (ST_Distance on geography returns meters)
        ST_Distance(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) / 1000.0 as origin_dist_km,
        ST_Distance(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography) / 1000.0 as dest_dist_km,
        -- Total score (lower is better)
        (ST_Distance(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) + 
         ST_Distance(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography)) / 1000.0 as score,
        'STRICT_ENDPOINTS'::text as match_type
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        -- BOTH points must be within radius
        AND ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, v_radius_meters)
        AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, v_radius_meters)
    ORDER BY 
        score ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 4. Permissions
GRANT EXECUTE ON FUNCTION public.find_matching_trips(uuid, double precision) TO authenticated;
GRANT EXECUTE ON FUNCTION public.find_matching_trips(uuid, double precision) TO service_role;

-- 5. Notify
NOTIFY pgrst, 'reload schema';
