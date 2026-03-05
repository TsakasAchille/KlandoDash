-- =============================================================================
-- Migration: CRM Opportunities & User Intelligence
-- Description: Functions to detect actionable growth opportunities (unmatched demand, empty trips).
-- =============================================================================

-- 1. Create a view for a 360° User Profile (CRM style)
CREATE OR REPLACE VIEW public.crm_user_intelligence AS
WITH user_stats AS (
    SELECT 
        u.uid,
        count(DISTINCT t.trip_id) as total_trips_driver,
        count(DISTINCT b.id) as total_bookings_passenger,
        max(t.created_at) as last_trip_date,
        max(b.created_at) as last_booking_date
    FROM users u
    LEFT JOIN trips t ON u.uid = t.driver_id
    LEFT JOIN bookings b ON u.uid = b.user_id
    GROUP BY u.uid
),
user_intentions AS (
    SELECT 
        contact_info,
        count(*) as total_requests,
        json_agg(json_build_object('origin', origin_city, 'dest', destination_city, 'date', desired_date)) as recent_intents
    FROM site_trip_requests
    GROUP BY contact_info
)
SELECT 
    u.uid,
    u.display_name,
    u.email,
    u.phone_number,
    u.role,
    u.gender,
    u.rating,
    u.is_driver_doc_validated,
    u.created_at as signup_date,
    COALESCE(s.total_trips_driver, 0) as total_trips_driver,
    COALESCE(s.total_bookings_passenger, 0) as total_bookings_passenger,
    GREATEST(s.last_trip_date, s.last_booking_date, u.created_at) as last_active_date,
    i.total_requests as website_intents_count,
    i.recent_intents,
    CASE 
        WHEN s.total_trips_driver > 10 THEN 'TOP_DRIVER'
        WHEN s.total_bookings_passenger > 10 THEN 'TOP_PASSENGER'
        WHEN s.total_trips_driver = 0 AND s.total_bookings_passenger = 0 AND i.total_requests > 0 THEN 'PROSPECT'
        WHEN GREATEST(s.last_trip_date, s.last_booking_date) < now() - interval '30 days' THEN 'CHURN_RISK'
        ELSE 'ACTIVE'
    END as crm_tag
FROM users u
LEFT JOIN user_stats s ON u.uid = s.uid
LEFT JOIN user_intentions i ON u.email = i.contact_info OR u.phone_number = i.contact_info;

-- 2. Function to get actionable CRM opportunities
CREATE OR REPLACE FUNCTION public.get_crm_opportunities()
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    unmatched_demand json;
    empty_trips json;
    retention_alerts json;
BEGIN
    -- A. Unmatched Demand: Corridors with requests but no pending trips in the next 7 days
    SELECT json_agg(t) INTO unmatched_demand FROM (
        SELECT 
            sr.origin_city,
            sr.destination_city,
            count(*) as request_count,
            min(sr.desired_date) as earliest_date,
            json_agg(json_build_object('name', u.display_name, 'contact', sr.contact_info)) as potential_passengers
        FROM site_trip_requests sr
        LEFT JOIN users u ON sr.contact_info = u.email OR sr.contact_info = u.phone_number
        WHERE sr.desired_date >= now()
        AND NOT EXISTS (
            SELECT 1 FROM trips t 
            WHERE t.departure_name ILIKE '%' || sr.origin_city || '%'
            AND t.destination_name ILIKE '%' || sr.destination_city || '%'
            AND t.status = 'PENDING'
            AND t.departure_schedule >= now()
        )
        GROUP BY sr.origin_city, sr.destination_city
        ORDER BY request_count DESC
        LIMIT 5
    ) t;

    -- B. Empty Trips: Active trips with 0 bookings departing in less than 48h
    SELECT json_agg(t) INTO empty_trips FROM (
        SELECT 
            t.trip_id,
            t.departure_name,
            t.destination_name,
            t.departure_schedule,
            t.seats_available,
            u.display_name as driver_name,
            u.phone_number as driver_contact
        FROM trips t
        JOIN users u ON t.driver_id = u.uid
        WHERE t.status = 'PENDING'
        AND t.departure_schedule BETWEEN now() AND now() + interval '48 hours'
        AND t.seats_booked = 0
        ORDER BY t.departure_schedule ASC
        LIMIT 5
    ) t;

    -- C. Retention: Top drivers who haven't posted in 14 days
    SELECT json_agg(t) INTO retention_alerts FROM (
        SELECT 
            u.uid,
            u.display_name,
            u.phone_number,
            max(t.created_at) as last_trip_date,
            count(t.trip_id) as total_lifetime_trips
        FROM users u
        JOIN trips t ON u.uid = t.driver_id
        GROUP BY u.uid, u.display_name, u.phone_number
        HAVING max(t.created_at) < now() - interval '14 days'
        AND count(t.trip_id) > 5
        ORDER BY total_lifetime_trips DESC
        LIMIT 5
    ) t;

    RETURN json_build_object(
        'unmatched_demand', COALESCE(unmatched_demand, '[]'::json),
        'empty_trips', COALESCE(empty_trips, '[]'::json),
        'retention_alerts', COALESCE(retention_alerts, '[]'::json)
    );
END;
$$;

GRANT SELECT ON public.crm_user_intelligence TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_crm_opportunities() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_crm_opportunities() TO service_role;
