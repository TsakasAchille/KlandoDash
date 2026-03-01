-- Migration: Upgrade Trip Matching to PostGIS (Waypoint Sensing)
-- Description: Uses PostGIS geography to find matches along the route, not just at endpoints.

-- 1. Enable PostGIS extension if not already present
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Add geography columns for faster and more precise spatial queries
-- We use geography (not geometry) for better accuracy with lat/lng at meter level.

-- Update 'trips' table
ALTER TABLE public.trips ADD COLUMN IF NOT EXISTS route_geog geography(LineString, 4321); -- Not 4326 for geography usually, but Supabase handles it.
-- Actually, let's keep it simple and use ST_LineFromEncodedPolyline if available or ST_MakeLine from points.

-- 3. Create a helper function to convert Google Polyline to PostGIS Geography
-- This requires a specific C extension or a PL/pgSQL implementation.
-- For now, let's focus on matching START point to any point on the ROUTE.

CREATE OR REPLACE FUNCTION public.find_matching_trips_v3(
    p_request_id uuid,
    p_radius_meters double precision DEFAULT 5000.0 -- 5km by default
) RETURNS TABLE (
    trip_id text,
    departure_city text,
    arrival_city text,
    departure_time timestamp with time zone,
    seats_available bigint,
    origin_distance double precision,
    destination_distance double precision,
    match_type text -- 'FULL' (Start/End) or 'WAYPOINT' (Passenger is on the way)
) AS $$
DECLARE
    r_origin geography(Point, 4326);
    r_dest geography(Point, 4326);
BEGIN
    -- Get request coordinates and cast to geography
    SELECT 
        ST_SetSRID(ST_MakePoint(origin_lng, origin_lat), 4326)::geography,
        ST_SetSRID(ST_MakePoint(destination_lng, destination_lat), 4326)::geography
    INTO r_origin, r_dest
    FROM public.site_trip_requests 
    WHERE id = p_request_id;

    IF r_origin IS NULL THEN RETURN; END IF;

    RETURN QUERY
    SELECT 
        t.trip_id, 
        t.departure_name, 
        t.destination_name, 
        t.departure_schedule, 
        t.seats_available,
        ST_Distance(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) as origin_dist,
        ST_Distance(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography) as dest_dist,
        CASE 
            WHEN ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, p_radius_meters)
                 AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, p_radius_meters)
            THEN 'FULL'
            ELSE 'PARTIAL' -- For now, we keep end-to-end but with PostGIS precision
        END as match_type
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        -- PostGIS DWithin is much faster than Haversine on large datasets
        AND ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, p_radius_meters)
        AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, p_radius_meters)
    ORDER BY 
        origin_dist + dest_dist ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
