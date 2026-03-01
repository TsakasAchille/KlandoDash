-- Migration: Add Polyline Decoder and Route-based Matching
-- Description: Decodes Google Polylines to PostGIS Geography and enables waypoint sensing.

-- 1. Function to decode Google Encoded Polylines to PostGIS Geometry
-- Based on standard algorithms for decoding Google's polyline format.
CREATE OR REPLACE FUNCTION public.decode_polyline(polyline_str text)
RETURNS geometry AS $$
DECLARE
    len int := length(polyline_str);
    idx int := 1;
    lat int := 0;
    lng int := 0;
    res_lat int;
    res_lng int;
    shift int;
    result int;
    byte int;
    points geometry[];
BEGIN
    WHILE idx <= len LOOP
        -- Latitude
        shift := 0;
        result := 0;
        LOOP
            byte := ascii(substring(polyline_str, idx, 1)) - 63;
            idx := idx + 1;
            result := result | ((byte & 31) << shift);
            shift := shift + 5;
            EXIT WHEN byte < 32;
        END LOOP;
        res_lat := CASE WHEN (result & 1) != 0 THEN ~(result >> 1) ELSE (result >> 1) END;
        lat := lat + res_lat;

        -- Longitude
        shift := 0;
        result := 0;
        LOOP
            byte := ascii(substring(polyline_str, idx, 1)) - 63;
            idx := idx + 1;
            result := result | ((byte & 31) << shift);
            shift := shift + 5;
            EXIT WHEN byte < 32;
        END LOOP;
        res_lng := CASE WHEN (result & 1) != 0 THEN ~(result >> 1) ELSE (result >> 1) END;
        lng := lng + res_lng;

        points := array_append(points, ST_SetSRID(ST_MakePoint(lng * 1e-5, lat * 1e-5), 4326));
    END LOOP;

    RETURN ST_MakeLine(points);
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;

-- 2. Update existing trips to populate route_geog
-- Note: route_geog was added in previous migration
UPDATE public.trips 
SET route_geog = decode_polyline(polyline)::geography 
WHERE polyline IS NOT NULL AND route_geog IS NULL;

-- 3. Advanced Matching Function: Waypoint Sensing (V4)
-- We must DROP before CREATE OR REPLACE because the return signature changed (match_type added)
DROP FUNCTION IF EXISTS public.find_matching_trips(uuid, double precision);

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
        -- Distance to start/end for scoring
        ST_Distance(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) / 1000.0 as origin_dist_km,
        ST_Distance(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography) / 1000.0 as dest_dist_km,
        -- Weighted score (prefer start-to-start matches over waypoint matches)
        (ST_Distance(r_origin, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography)) + 
         ST_Distance(r_dest, COALESCE(t.route_geog, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography))) / 1000.0 as score,
        CASE 
            WHEN ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, v_radius_meters)
                 AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, v_radius_meters)
            THEN 'EXACT_MATCH'
            WHEN ST_DWithin(r_origin, t.route_geog, v_radius_meters) 
                 AND ST_DWithin(r_dest, t.route_geog, v_radius_meters)
            THEN 'WAYPOINT_MATCH'
            ELSE 'PARTIAL'
        END as match_type
    FROM 
        public.trips t
    WHERE 
        t.status = 'PENDING'
        AND t.departure_schedule > now()
        AND t.seats_available > 0
        -- Match if passenger's origin AND destination are near the driver's route
        AND (
            (ST_DWithin(r_origin, t.route_geog, v_radius_meters) AND ST_DWithin(r_dest, t.route_geog, v_radius_meters))
            OR 
            (ST_DWithin(r_origin, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, v_radius_meters)
             AND ST_DWithin(r_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, v_radius_meters))
        )
    ORDER BY 
        score ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
