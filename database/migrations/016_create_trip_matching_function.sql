-- ==============================================================================
-- Migration: Create Trip Matching Function
-- Description: Finds trips near a request's origin and destination using 
--              Haversine formula for distance calculation in kilometers.
-- ==============================================================================

-- Function to calculate distance between two points in km
CREATE OR REPLACE FUNCTION public.haversine_distance(
    lat1 double precision, lon1 double precision,
    lat2 double precision, lon2 double precision
) RETURNS double precision AS $$
DECLARE
    R double precision := 6371; -- Earth radius in km
    dLat double precision := radians(lat2 - lat1);
    dLon double precision := radians(lon2 - lon1);
    a double precision;
    c double precision;
BEGIN
    a := sin(dLat/2) * sin(dLat/2) +
         cos(radians(lat1)) * cos(radians(lat2)) *
         sin(dLon/2) * sin(dLon/2);
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    RETURN R * c;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to find matching trips for a request
-- Usage: SELECT * FROM find_matching_trips('request-uuid', 5.0); -- 5km radius
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
    -- Get request coordinates
    SELECT origin_lat, origin_lng, destination_lat, destination_lng
    INTO r_origin_lat, r_origin_lng, r_dest_lat, r_dest_lng
    FROM public.site_trip_requests
    WHERE id = p_request_id;

    -- If coordinates are missing, we can't do proximity matching
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
        public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) as origin_dist,
        public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude) as dest_dist,
        (public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) + 
         public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude)) as score
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        AND public.haversine_distance(r_origin_lat, r_origin_lng, t.departure_latitude, t.departure_longitude) <= p_radius_km
        AND public.haversine_distance(r_dest_lat, r_dest_lng, t.destination_latitude, t.destination_longitude) <= p_radius_km
    ORDER BY 
        score ASC;
END;
$$ LANGUAGE plpgsql STABLE;
