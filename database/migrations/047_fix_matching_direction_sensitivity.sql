-- Migration: Fix Direction Sensitivity in Trip Matching
-- Description: Ensures matching only returns trips going in the same direction as the passenger.

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
    v_radius_meters := p_radius_km * 1000.0;

    SELECT 
        ST_SetSRID(ST_MakePoint(origin_lng, origin_lat), 4326)::geography,
        ST_SetSRID(ST_MakePoint(destination_lng, destination_lat), 4326)::geography
    INTO r_origin, r_dest
    FROM public.site_trip_requests 
    WHERE id = p_request_id;

    IF r_origin IS NULL OR r_dest IS NULL THEN RETURN; END IF;

    RETURN QUERY
    SELECT 
        t.trip_id, 
        t.departure_name, 
        t.destination_name, 
        t.departure_schedule, 
        t.seats_available,
        -- endpoint distances
        ST_Distance(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) / 1000.0 as origin_dist_km,
        ST_Distance(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography) / 1000.0 as dest_dist_km,
        -- score
        (ST_Distance(r_origin, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography)) + 
         ST_Distance(r_dest, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography))) / 1000.0 as score,
        CASE 
            WHEN ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, v_radius_meters)
                 AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, v_radius_meters)
            THEN 'EXACT_MATCH'
            ELSE 'WAYPOINT_MATCH'
        END as match_type
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        -- 1. Proximity Check
        AND ST_DWithin(r_origin, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography), v_radius_meters)
        AND ST_DWithin(r_dest, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography), v_radius_meters)
        -- 2. DIRECTION SENSITIVITY CHECK (CRITICAL)
        -- The origin must appear BEFORE the destination on the driver's path
        AND (
            t.route_geog IS NULL OR -- Fallback if no polyline
            ST_LineLocatePoint(t.route_geog::geometry, r_origin::geometry) < ST_LineLocatePoint(t.route_geog::geometry, r_dest::geometry)
        )
    ORDER BY 
        score ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
