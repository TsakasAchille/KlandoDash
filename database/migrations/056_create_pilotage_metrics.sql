-- =============================================================================
-- Migration: Create Pilotage Metrics Function
-- Description: RPC function to calculate business KPIs from Cahier des charges.
-- =============================================================================

CREATE OR REPLACE FUNCTION public.get_pilotage_metrics()
RETURNS json 
LANGUAGE plpgsql
SECURITY DEFINER 
SET search_path = public
AS $$
DECLARE
    -- Activation
    activation_passenger numeric;
    activation_driver numeric;
    
    -- Retention (Repeat Rate W1)
    repeat_passenger_w1 numeric;
    repeat_driver_w1 numeric;
    
    -- Efficiency
    fill_rate numeric;
    trips_zero_booking_pct numeric;
    realized_published_ratio numeric;
    
    -- Liquidity (Match Rate)
    match_rate_demand numeric;
    match_rate_supply numeric;
    
    -- Quality
    cancel_rate_driver numeric;
    cancel_rate_passenger numeric;
    
    -- Geographical (Corridors)
    corridors_stats json;
    
    -- Helpers
    last_week_start timestamp := date_trunc('week', now() - interval '1 week');
    prev_week_start timestamp := date_trunc('week', now() - interval '2 weeks');
BEGIN
    -- 1. ACTIVATION PASSAGER (72h)
    -- Ratio des nouveaux users (créés il y a > 72h) ayant fait au moins une demande
    SELECT 
        round(
            (count(DISTINCT u.uid) FILTER (WHERE sr.id IS NOT NULL))::numeric / 
            NULLIF(count(DISTINCT u.uid), 0) * 100, 1
        ) INTO activation_passenger
    FROM users u
    LEFT JOIN site_trip_requests sr ON u.email = sr.contact_info AND sr.created_at <= u.created_at + interval '72 hours'
    WHERE u.created_at >= now() - interval '30 days'
    AND (u.role = 'passenger' OR u.role IS NULL);

    -- 2. ACTIVATION CONDUCTEUR (7 jours)
    SELECT 
        round(
            (count(DISTINCT u.uid) FILTER (WHERE t.trip_id IS NOT NULL))::numeric / 
            NULLIF(count(DISTINCT u.uid), 0) * 100, 1
        ) INTO activation_driver
    FROM users u
    LEFT JOIN trips t ON u.uid = t.driver_id AND t.created_at <= u.created_at + interval '7 days'
    WHERE u.created_at >= now() - interval '30 days'
    AND (u.role = 'driver' OR u.driver_license_url IS NOT NULL);

    -- 3. REPEAT RATE W1 (Passagers)
    -- Users ayant fait un booking en semaine N-2 et aussi en semaine N-1
    WITH active_n2 AS (
        SELECT DISTINCT user_id FROM bookings WHERE created_at >= prev_week_start AND created_at < last_week_start
    ), active_n1 AS (
        SELECT DISTINCT user_id FROM bookings WHERE created_at >= last_week_start AND created_at < date_trunc('week', now())
    )
    SELECT round(count(n1.user_id)::numeric / NULLIF(count(n2.user_id), 0) * 100, 1)
    INTO repeat_passenger_w1
    FROM active_n2 n2
    LEFT JOIN active_n1 n1 ON n2.user_id = n1.user_id;

    -- 4. REPEAT RATE W1 (Drivers)
    WITH active_n2 AS (
        SELECT DISTINCT driver_id FROM trips WHERE created_at >= prev_week_start AND created_at < last_week_start
    ), active_n1 AS (
        SELECT DISTINCT driver_id FROM trips WHERE created_at >= last_week_start AND created_at < date_trunc('week', now())
    )
    SELECT round(count(n1.driver_id)::numeric / NULLIF(count(n2.driver_id), 0) * 100, 1)
    INTO repeat_driver_w1
    FROM active_n2 n2
    LEFT JOIN active_n1 n1 ON n2.driver_id = n1.driver_id;

    -- 5. FILL RATE & ZERO BOOKING
    SELECT 
        round(avg(seats_booked::numeric / NULLIF(seats_available + seats_booked, 0)) * 100, 1),
        round(count(*) FILTER (WHERE seats_booked = 0)::numeric / NULLIF(count(*), 0) * 100, 1)
    INTO fill_rate, trips_zero_booking_pct
    FROM trips
    WHERE status != 'CANCELLED';

    -- 6. MATCH RATE (Liquidité)
    -- Demande : % de site_requests avec au moins un match trouvé
    SELECT 
        round(count(DISTINCT sr.id) FILTER (WHERE m.id IS NOT NULL)::numeric / NULLIF(count(DISTINCT sr.id), 0) * 100, 1)
    INTO match_rate_demand
    FROM site_trip_requests sr
    LEFT JOIN site_trip_request_matches m ON sr.id = m.request_id;

    -- Offre : % de trajets ayant reçu au moins 1 booking
    SELECT 
        round(count(*) FILTER (WHERE seats_booked > 0)::numeric / NULLIF(count(*), 0) * 100, 1)
    INTO match_rate_supply
    FROM trips
    WHERE status != 'CANCELLED';

    -- 7. EXECUTION (Realized / Published)
    SELECT 
        round(count(*) FILTER (WHERE status = 'COMPLETED')::numeric / NULLIF(count(*) FILTER (WHERE status IN ('COMPLETED', 'ACTIVE', 'CANCELLED')), 0) * 100, 1)
    INTO realized_published_ratio
    FROM trips;

    -- 8. CORRIDORS FOCUS
    SELECT json_agg(t) INTO corridors_stats FROM (
        SELECT 
            departure_name as origin,
            destination_name as destination,
            count(*) as trips_count,
            sum(seats_booked) as total_bookings,
            round(avg(seats_booked::numeric / NULLIF(seats_available + seats_booked, 0)) * 100, 1) as fill_rate
        FROM trips
        WHERE created_at >= now() - interval '30 days'
        GROUP BY origin, destination
        ORDER BY trips_count DESC
        LIMIT 10
    ) t;

    -- CONSTRUCTION DU RÉSULTAT FINAL
    RETURN json_build_object(
        'activation', json_build_object(
            'passenger', coalesce(activation_passenger, 0),
            'driver', coalesce(activation_driver, 0)
        ),
        'retention', json_build_object(
            'passenger_w1', coalesce(repeat_passenger_w1, 0),
            'driver_w1', coalesce(repeat_driver_w1, 0)
        ),
        'efficiency', json_build_object(
            'fill_rate', coalesce(fill_rate, 0),
            'trips_zero_booking_pct', coalesce(trips_zero_booking_pct, 0),
            'realized_published_ratio', coalesce(realized_published_ratio, 0)
        ),
        'liquidity', json_build_object(
            'match_rate_demand', coalesce(match_rate_demand, 0),
            'match_rate_supply', coalesce(match_rate_supply, 0)
        ),
        'corridors', coalesce(corridors_stats, '[]'::json)
    );
END;
$$;

GRANT EXECUTE ON FUNCTION public.get_pilotage_metrics() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_pilotage_metrics() TO service_role;
GRANT EXECUTE ON FUNCTION public.get_pilotage_metrics() TO anon;
