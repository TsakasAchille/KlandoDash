-- ==============================================================================
-- Test Script: PostGIS Matching Engine Verification (V4 - Waypoint & Direction)
-- Description: Creates a sandbox environment to validate direction sensitivity 
--              and waypoint sensing logic.
-- ==============================================================================

DO $$ 
DECLARE
    v_req_id uuid := '00000000-0000-0000-0000-000000000001';
BEGIN
    -- 1. CLEANUP PREVIOUS TEST DATA
    DELETE FROM public.site_trip_requests WHERE id = v_req_id;
    DELETE FROM public.trips WHERE trip_id LIKE 'TEST-TRIP-%';

    -- 2. CREATE A MOCK REQUEST (Dakar -> Thiès)
    INSERT INTO public.site_trip_requests (id, origin_city, destination_city, origin_lat, origin_lng, destination_lat, destination_lng, status)
    VALUES (v_req_id, 'Dakar', 'Thiès', 14.7167, -17.4677, 14.7910, -16.9359, 'NEW');

    -- 3. CREATE VARIOUS TRIPS TO TEST EDGE CASES
    
    -- Trip A: Perfect Match (Same direction, same endpoints)
    INSERT INTO public.trips (trip_id, departure_name, destination_name, departure_latitude, departure_longitude, destination_latitude, destination_longitude, status, departure_schedule, polyline)
    VALUES ('TEST-TRIP-A', 'Dakar', 'Thiès', 14.7167, -17.4677, 14.7910, -16.9359, 'PENDING', now() + interval '1 day', 'encoded_polyline_here');

    -- Trip B: Opposite Direction (Thiès -> Dakar) - SHOULD NOT MATCH
    INSERT INTO public.trips (trip_id, departure_name, destination_name, departure_latitude, departure_longitude, destination_latitude, destination_longitude, status, departure_schedule, polyline)
    VALUES ('TEST-TRIP-B', 'Thiès', 'Dakar', 14.7910, -16.9359, 14.7167, -17.4677, 'PENDING', now() + interval '1 day', 'encoded_polyline_here');

    -- Trip C: Long Route (Dakar -> Saint-Louis) passing through Thiès - WAYPOINT MATCH
    -- Note: This requires a valid route_geog. In real life, the trigger will handle this.
    INSERT INTO public.trips (trip_id, departure_name, destination_name, departure_latitude, departure_longitude, destination_latitude, destination_longitude, status, departure_schedule, polyline)
    VALUES ('TEST-TRIP-C', 'Dakar', 'Saint-Louis', 14.7167, -17.4677, 16.0179, -16.4896, 'PENDING', now() + interval '1 day', 'encoded_polyline_here');

    -- Trip D: Too far away (> 5km) - SHOULD NOT MATCH
    INSERT INTO public.trips (trip_id, departure_name, destination_name, departure_latitude, departure_longitude, destination_latitude, destination_longitude, status, departure_schedule, polyline)
    VALUES ('TEST-TRIP-D', 'Mbour', 'Kaolack', 14.4220, -16.9634, 14.1444, -16.0733, 'PENDING', now() + interval '1 day', 'encoded_polyline_here');

    RAISE NOTICE 'Test environment prepared for request %', v_req_id;
END $$;

-- 4. RUN THE ACTUAL MATCHING QUERY
SELECT 
    trip_id, 
    match_type, 
    origin_distance as dist_start, 
    destination_distance as dist_end,
    departure_city || ' -> ' || arrival_city as route
FROM public.find_matching_trips('00000000-0000-0000-0000-000000000001', 5.0);

-- EXPECTED RESULTS:
-- TEST-TRIP-A: EXACT_MATCH (Score low)
-- TEST-TRIP-C: WAYPOINT_MATCH (If Thiès is on the route)
-- TEST-TRIP-B: Discarded (Wrong direction)
-- TEST-TRIP-D: Discarded (Too far)
