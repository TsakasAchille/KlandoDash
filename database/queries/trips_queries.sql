-- =====================================================
-- Requêtes optimisées pour la table trips
-- Éviter SELECT * - toujours spécifier les colonnes
-- =====================================================

-- -----------------------------------------------------
-- 1. Liste des trajets pour le dashboard (pagination)
-- -----------------------------------------------------
-- Colonnes nécessaires uniquement, avec pagination
CREATE OR REPLACE FUNCTION get_trips_list(
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0,
    p_status TEXT DEFAULT NULL
)
RETURNS TABLE (
    trip_id TEXT,
    departure_name TEXT,
    destination_name TEXT,
    departure_schedule TIMESTAMPTZ,
    distance FLOAT,
    seats_available BIGINT,
    seats_published BIGINT,
    passenger_price BIGINT,
    status TEXT,
    driver_id TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.trip_id,
        t.departure_name,
        t.destination_name,
        t.departure_schedule,
        t.distance,
        t.seats_available,
        t.seats_published,
        t.passenger_price,
        t.status,
        t.driver_id
    FROM trips t
    WHERE (p_status IS NULL OR t.status = p_status)
    ORDER BY t.departure_schedule DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------
-- 2. Détail d'un trajet avec infos conducteur
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_trip_detail(p_trip_id TEXT)
RETURNS TABLE (
    -- Trip info
    trip_id TEXT,
    departure_name TEXT,
    departure_description TEXT,
    departure_latitude FLOAT,
    departure_longitude FLOAT,
    destination_name TEXT,
    destination_description TEXT,
    destination_latitude FLOAT,
    destination_longitude FLOAT,
    departure_schedule TIMESTAMPTZ,
    distance FLOAT,
    polyline TEXT,
    seats_available BIGINT,
    seats_published BIGINT,
    seats_booked BIGINT,
    passenger_price BIGINT,
    driver_price BIGINT,
    status TEXT,
    auto_confirmation BOOLEAN,
    created_at TIMESTAMPTZ,
    -- Driver info
    driver_id TEXT,
    driver_name TEXT,
    driver_photo TEXT,
    driver_rating NUMERIC,
    driver_rating_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.trip_id,
        t.departure_name,
        t.departure_description,
        t.departure_latitude,
        t.departure_longitude,
        t.destination_name,
        t.destination_description,
        t.destination_latitude,
        t.destination_longitude,
        t.departure_schedule,
        t.distance,
        t.polyline,
        t.seats_available,
        t.seats_published,
        t.seats_booked,
        t.passenger_price,
        t.driver_price,
        t.status,
        t.auto_confirmation,
        t.created_at,
        u.uid,
        u.display_name,
        u.photo_url,
        u.rating,
        u.rating_count
    FROM trips t
    LEFT JOIN users u ON t.driver_id = u.uid
    WHERE t.trip_id = p_trip_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------
-- 3. Compteurs pour le dashboard
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_trips_stats()
RETURNS TABLE (
    total_trips BIGINT,
    active_trips BIGINT,
    completed_trips BIGINT,
    total_distance FLOAT,
    total_seats_booked BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE status = 'ACTIVE')::BIGINT,
        COUNT(*) FILTER (WHERE status = 'COMPLETED')::BIGINT,
        COALESCE(SUM(distance), 0)::FLOAT,
        COALESCE(SUM(seats_booked), 0)::BIGINT
    FROM trips;
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------
-- 4. Trajets à venir (pour calendrier/planning)
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_upcoming_trips(
    p_limit INT DEFAULT 20
)
RETURNS TABLE (
    trip_id TEXT,
    departure_name TEXT,
    destination_name TEXT,
    departure_schedule TIMESTAMPTZ,
    seats_available BIGINT,
    passenger_price BIGINT,
    driver_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.trip_id,
        t.departure_name,
        t.destination_name,
        t.departure_schedule,
        t.seats_available,
        t.passenger_price,
        u.display_name
    FROM trips t
    LEFT JOIN users u ON t.driver_id = u.uid
    WHERE t.departure_schedule > NOW()
      AND t.status IN ('ACTIVE', 'PENDING')
    ORDER BY t.departure_schedule ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------
-- 5. Recherche de trajets par ville
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION search_trips_by_city(
    p_departure TEXT DEFAULT NULL,
    p_destination TEXT DEFAULT NULL,
    p_date DATE DEFAULT NULL,
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    trip_id TEXT,
    departure_name TEXT,
    destination_name TEXT,
    departure_schedule TIMESTAMPTZ,
    distance FLOAT,
    seats_available BIGINT,
    passenger_price BIGINT,
    driver_name TEXT,
    driver_rating NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.trip_id,
        t.departure_name,
        t.destination_name,
        t.departure_schedule,
        t.distance,
        t.seats_available,
        t.passenger_price,
        u.display_name,
        u.rating
    FROM trips t
    LEFT JOIN users u ON t.driver_id = u.uid
    WHERE t.status = 'ACTIVE'
      AND t.seats_available > 0
      AND (p_departure IS NULL OR t.departure_name ILIKE '%' || p_departure || '%')
      AND (p_destination IS NULL OR t.destination_name ILIKE '%' || p_destination || '%')
      AND (p_date IS NULL OR DATE(t.departure_schedule) = p_date)
    ORDER BY t.departure_schedule ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- -----------------------------------------------------
-- 6. Trajets d'un conducteur
-- -----------------------------------------------------
CREATE OR REPLACE FUNCTION get_driver_trips(
    p_driver_id TEXT,
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    trip_id TEXT,
    departure_name TEXT,
    destination_name TEXT,
    departure_schedule TIMESTAMPTZ,
    seats_booked BIGINT,
    seats_published BIGINT,
    passenger_price BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.trip_id,
        t.departure_name,
        t.destination_name,
        t.departure_schedule,
        t.seats_booked,
        t.seats_published,
        t.passenger_price,
        t.status
    FROM trips t
    WHERE t.driver_id = p_driver_id
    ORDER BY t.departure_schedule DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;
