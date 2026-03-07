-- Migration: Smart Driver Search for AI Hub
-- Description: Allows finding historical drivers based on geographic proximity of both origin and destination.

CREATE OR REPLACE FUNCTION public.find_drivers_by_proximity(
    p_orig_lat double precision,
    p_orig_lng double precision,
    p_dest_lat double precision,
    p_dest_lng double precision,
    p_threshold_km double precision DEFAULT 15.0
) RETURNS TABLE (
    uid uuid,
    display_name text,
    photo_url text,
    phone_number text,
    rating double precision,
    matched_trip jsonb
) AS $$
DECLARE
    v_orig geography;
    v_dest geography;
BEGIN
    v_orig := ST_SetSRID(ST_MakePoint(p_orig_lng, p_orig_lat), 4326)::geography;
    v_dest := ST_SetSRID(ST_MakePoint(p_dest_lng, p_dest_lat), 4326)::geography;

    RETURN QUERY
    SELECT DISTINCT ON (u.uid)
        u.uid,
        u.display_name,
        u.photo_url,
        u.phone_number,
        u.rating,
        jsonb_build_object(
            'departure', t.departure_name,
            'destination', t.destination_name,
            'date', t.departure_schedule,
            'dist_orig_km', round((ST_Distance(v_orig, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) / 1000.0)::numeric, 1),
            'dist_dest_km', round((ST_Distance(v_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography) / 1000.0)::numeric, 1)
        ) as matched_trip
    FROM trips t
    JOIN users u ON t.driver_id = u.uid
    WHERE 
        -- Comparaison Départ -> Départ
        ST_DWithin(v_orig, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography, p_threshold_km * 1000)
        -- ET Comparaison Arrivée -> Arrivée
        AND ST_DWithin(v_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography, p_threshold_km * 1000)
    ORDER BY u.uid, (ST_Distance(v_orig, ST_SetSRID(ST_MakePoint(t.departure_longitude, t.departure_latitude), 4326)::geography) + 
                      ST_Distance(v_dest, ST_SetSRID(ST_MakePoint(t.destination_longitude, t.destination_latitude), 4326)::geography)) ASC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
