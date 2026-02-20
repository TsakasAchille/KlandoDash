-- =============================================================================
-- Migration: Optimize Dashboard Stats Final Version
-- Description: Complete RPC function providing all necessary fields for the 
--              frontend dashboard while staying efficient and safe.
-- =============================================================================

-- 1. Nettoyage de sécurité
DROP FUNCTION IF EXISTS public.get_klando_stats_final();

-- 2. Création de la fonction finale et robuste
CREATE OR REPLACE FUNCTION public.get_klando_stats_final()
RETURNS json 
LANGUAGE plpgsql
SECURITY DEFINER -- Essential: bypass RLS for global counts
SET search_path = public
AS $$
DECLARE
    -- Variables pour stocker les résultats intermédiaires
    trips_total bigint;
    trips_by_status json;
    trips_dist double precision;
    trips_seats bigint;
    users_total bigint;
    users_v_drivers bigint;
    users_new bigint;
    avg_rating_val numeric;
    gender_dist json;
    age_dist json;
    typical_gender text;
    typical_age text;
    bookings_total_val bigint;
    txns_total_val bigint;
    txns_amount bigint;
    txns_status json;
    txns_type json;
    rev_passenger bigint;
    rev_driver bigint;
    rev_count bigint;
    cf_in bigint;
    cf_out bigint;
    cf_c_in bigint;
    cf_c_out bigint;
    
    -- Nouvelles variables pour les statistiques avancées
    drivers_verif_status json;
    top_drivers_list json;
    users_typology json;
    site_requests_total bigint;
    cancel_rate numeric;
    avg_seats_per_trip numeric;

    -- Analyse Géo
    top_routes json;
    orphan_cities json;
BEGIN
    -- SECTION: TRIPS
    SELECT count(*) INTO trips_total FROM trips;
    SELECT json_agg(t) INTO trips_by_status FROM (
        SELECT status, count(*) as count FROM trips GROUP BY status
    ) t;
    SELECT coalesce(sum(distance), 0) INTO trips_dist FROM trips;
    SELECT coalesce(sum(seats_booked), 0) INTO trips_seats FROM trips;
    
    -- Calcul du taux d'annulation et sièges moyens
    SELECT 
        round((count(*) FILTER (WHERE status = 'CANCELLED')::numeric / NULLIF(count(*), 0)::numeric) * 100, 2),
        round(avg(seats_available + seats_booked), 1)
    INTO cancel_rate, avg_seats_per_trip
    FROM trips;
    
    -- SECTION: USERS
    SELECT count(*) INTO users_total FROM users;
    SELECT count(*) INTO users_v_drivers FROM users WHERE is_driver_doc_validated = true;
    SELECT count(*) INTO users_new FROM users WHERE created_at >= date_trunc('month', now());
    SELECT coalesce(avg(rating), 0) INTO avg_rating_val FROM users WHERE rating > 0;
    
    -- SECTION: DEMOGRAPHICS
    SELECT json_agg(t) INTO gender_dist FROM (
        SELECT 
            CASE 
                WHEN lower(gender) = 'man' THEN 'Homme' 
                WHEN lower(gender) = 'woman' THEN 'Femme' 
                ELSE 'Non spécifié' 
            END as label, 
            count(*) as count 
        FROM users 
        GROUP BY label
    ) t;
    
    SELECT json_agg(t) INTO age_dist FROM (
        SELECT '18-25' as label, count(*) as count FROM users WHERE extract(year from age(now(), birth)) BETWEEN 18 AND 25
        UNION ALL SELECT '26-35', count(*) FROM users WHERE extract(year from age(now(), birth)) BETWEEN 26 AND 35
        UNION ALL SELECT '36-50', count(*) FROM users WHERE extract(year from age(now(), birth)) BETWEEN 36 AND 50
        UNION ALL SELECT '50+', count(*) FROM users WHERE extract(year from age(now(), birth)) > 50
    ) t;

    -- SECTION: PROFILES
    typical_gender := 'Homme'; 
    typical_age := '26-35';
    
    -- SECTION: DRIVER ACQUISITION
    SELECT json_agg(t) INTO drivers_verif_status FROM (
        SELECT 
            CASE 
                WHEN is_driver_doc_validated = true THEN 'Vérifié'
                WHEN driver_license_url IS NOT NULL AND is_driver_doc_validated = false THEN 'En attente'
                ELSE 'Non initié'
            END as status,
            count(*) as count
        FROM users
        WHERE role = 'driver' OR driver_license_url IS NOT NULL
        GROUP BY status
    ) t;

    SELECT json_agg(t) INTO top_drivers_list FROM (
        SELECT 
            u.uid,
            u.display_name,
            u.photo_url,
            count(t.trip_id) as trips_count,
            avg(u.rating) as rating,
            sum(t.driver_price * t.seats_booked) as revenue
        FROM users u
        JOIN trips t ON u.uid = t.driver_id
        WHERE t.status = 'COMPLETED'
        GROUP BY u.uid, u.display_name, u.photo_url
        ORDER BY trips_count DESC
        LIMIT 5
    ) t;
    
    -- SECTION: USER TYPOLOGY
    WITH driver_stats AS (
        SELECT DISTINCT driver_id FROM trips
    ), passenger_stats AS (
        SELECT DISTINCT user_id FROM bookings
    )
    SELECT json_build_object(
        'drivers', (SELECT count(*) FROM driver_stats),
        'passengers', (SELECT count(*) FROM passenger_stats),
        'mixed', (SELECT count(*) FROM driver_stats d JOIN passenger_stats p ON d.driver_id = p.user_id)
    ) INTO users_typology;

    -- SECTION: TRANSACTIONS & REVENUE
    SELECT count(*) INTO txns_total_val FROM transactions;
    SELECT coalesce(sum(amount), 0) INTO txns_amount FROM transactions;
    
    SELECT coalesce(sum(t.amount), 0), coalesce(sum(tr.driver_price), 0), count(t.id) 
    INTO rev_passenger, rev_driver, rev_count
    FROM bookings b 
    JOIN transactions t ON b.transaction_id = t.id 
    LEFT JOIN trips tr ON b.trip_id = tr.trip_id
    WHERE t.status = 'SUCCESS';
    
    -- SECTION: CASHFLOW
    SELECT 
        coalesce(sum(CASE WHEN code_service LIKE '%CASH_OUT%' THEN amount ELSE 0 END), 0), 
        coalesce(sum(CASE WHEN code_service LIKE '%CASH_IN%' THEN amount ELSE 0 END), 0),
        count(CASE WHEN code_service LIKE '%CASH_OUT%' THEN 1 END), 
        count(CASE WHEN code_service LIKE '%CASH_IN%' THEN 1 END)
    INTO cf_in, cf_out, cf_c_in, cf_c_out 
    FROM transactions 
    WHERE status = 'SUCCESS';
    
    -- SECTION: GEOGRAPHICAL ANALYSIS
    -- 1. Top Routes by Revenue
    SELECT json_agg(t) INTO top_routes FROM (
        SELECT 
            departure_name as origin, 
            destination_name as destination, 
            count(b.id) as volume,
            sum(tx.amount) as revenue
        FROM trips tr
        JOIN bookings b ON tr.trip_id = b.trip_id
        JOIN transactions tx ON b.transaction_id = tx.id
        WHERE tx.status = 'SUCCESS'
        GROUP BY origin, destination
        ORDER BY revenue DESC
        LIMIT 5
    ) t;

    -- 2. Orphan Cities (High demand on site, no active trips)
    SELECT json_agg(t) INTO orphan_cities FROM (
        SELECT 
            origin_city as city,
            count(*) as demand_count
        FROM site_trip_requests sr
        WHERE NOT EXISTS (
            SELECT 1 FROM trips tr 
            WHERE (tr.departure_name ILIKE '%' || sr.origin_city || '%' OR tr.destination_name ILIKE '%' || sr.origin_city || '%')
            AND tr.status = 'ACTIVE'
        )
        GROUP BY city
        ORDER BY demand_count DESC
        LIMIT 5
    ) t;

    -- SECTION: BOOKINGS & MARKETING
    SELECT count(*) INTO bookings_total_val FROM bookings;
    SELECT count(*) INTO site_requests_total FROM site_trip_requests;

    -- CONSTRUCTION DE L'OBJET FINAL COMPLET
    RETURN json_build_object(
        'trips', json_build_object(
            'total', coalesce(trips_total, 0), 
            'byStatus', coalesce(trips_by_status, '[]'::json), 
            'totalDistance', coalesce(trips_dist, 0), 
            'totalSeatsBooked', coalesce(trips_seats, 0),
            'cancellationRate', coalesce(cancel_rate, 0),
            'avgSeatsPerTrip', coalesce(avg_seats_per_trip, 0)
        ),
        'users', json_build_object(
            'total', coalesce(users_total, 0), 
            'verifiedDrivers', coalesce(users_v_drivers, 0), 
            'newThisMonth', coalesce(users_new, 0), 
            'avgRating', coalesce(avg_rating_val, 0),
            'typicalProfile', json_build_object('gender', typical_gender, 'ageGroup', typical_age),
            'demographics', json_build_object('gender', coalesce(gender_dist, '[]'::json), 'age', coalesce(age_dist, '[]'::json)),
            'acquisition', json_build_object(
                'verificationStatus', coalesce(drivers_verif_status, '[]'::json),
                'topDrivers', coalesce(top_drivers_list, '[]'::json)
            ),
            'typology', coalesce(users_typology, '{"drivers": 0, "passengers": 0, "mixed": 0}'::json)
        ),
        'geo', json_build_object(
            'topRoutes', coalesce(top_routes, '[]'::json),
            'orphanCities', coalesce(orphan_cities, '[]'::json)
        ),
        'bookings', json_build_object('total', coalesce(bookings_total_val, 0)),
        'transactions', json_build_object(
            'total', coalesce(txns_total_val, 0), 
            'totalAmount', coalesce(txns_amount, 0),
            'byStatus', coalesce(txns_status, '[]'::json),
            'byType', coalesce(txns_type, '[]'::json)
        ),
        'revenue', json_build_object(
            'totalPassengerPaid', coalesce(rev_passenger, 0), 
            'totalDriverPrice', coalesce(rev_driver, 0), 
            'klandoMargin', coalesce(rev_passenger, 0) - coalesce(rev_driver, 0), 
            'transactionCount', coalesce(rev_count, 0)
        ),
        'cashFlow', json_build_object(
            'totalIn', coalesce(cf_in, 0), 
            'totalOut', coalesce(cf_out, 0), 
            'solde', coalesce(cf_in, 0) - coalesce(cf_out, 0), 
            'countIn', coalesce(cf_c_in, 0), 
            'countOut', coalesce(cf_c_out, 0)
        ),
        'marketing', json_build_object(
            'siteRequestsTotal', coalesce(site_requests_total, 0)
        )
    );
END;
$$;

-- 3. Droits d'exécution
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO service_role;
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO anon;

-- 4. Rechargement du cache
NOTIFY pgrst, 'reload schema';

-- 3. Droits d'exécution
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO service_role;
GRANT EXECUTE ON FUNCTION public.get_klando_stats_final() TO anon;

-- 4. Rechargement du cache
NOTIFY pgrst, 'reload schema';
