-- =====================================================
-- Vues optimisées pour le dashboard
-- Évite les jointures répétitives côté client
-- =====================================================

-- -----------------------------------------------------
-- Vue: Trajets avec infos conducteur (lecture seule)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_trips_with_driver AS
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
    t.updated_at,
    -- Driver info
    u.uid AS driver_id,
    u.display_name AS driver_name,
    u.photo_url AS driver_photo,
    u.phone_number AS driver_phone,
    u.rating AS driver_rating,
    u.rating_count AS driver_rating_count,
    u.is_driver_doc_validated AS driver_verified
FROM trips t
LEFT JOIN users u ON t.driver_id = u.uid;

-- -----------------------------------------------------
-- Vue: Réservations avec détails trajet et passager
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_bookings_detail AS
SELECT
    b.id AS booking_id,
    b.seats,
    b.status AS booking_status,
    b.created_at AS booking_date,
    -- Trip info
    t.trip_id,
    t.departure_name,
    t.destination_name,
    t.departure_schedule,
    t.passenger_price,
    -- Passenger info
    p.uid AS passenger_id,
    p.display_name AS passenger_name,
    p.phone_number AS passenger_phone,
    p.photo_url AS passenger_photo,
    -- Driver info
    d.uid AS driver_id,
    d.display_name AS driver_name,
    d.phone_number AS driver_phone
FROM bookings b
JOIN trips t ON b.trip_id = t.trip_id
JOIN users p ON b.user_id = p.uid
LEFT JOIN users d ON t.driver_id = d.uid;

-- -----------------------------------------------------
-- Vue: Statistiques par jour
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_trips_daily_stats AS
SELECT
    DATE(created_at) AS day,
    COUNT(*) AS trips_created,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS trips_completed,
    SUM(seats_booked) AS total_seats_booked,
    SUM(distance) AS total_distance,
    AVG(passenger_price) AS avg_price
FROM trips
GROUP BY DATE(created_at)
ORDER BY day DESC;

-- -----------------------------------------------------
-- Vue: Top villes de départ
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_top_departure_cities AS
SELECT
    departure_name AS city,
    COUNT(*) AS trip_count,
    SUM(seats_booked) AS total_passengers,
    AVG(distance) AS avg_distance
FROM trips
WHERE departure_name IS NOT NULL
GROUP BY departure_name
ORDER BY trip_count DESC
LIMIT 20;

-- -----------------------------------------------------
-- Vue: Top routes (départ → destination)
-- -----------------------------------------------------
CREATE OR REPLACE VIEW v_top_routes AS
SELECT
    departure_name || ' → ' || destination_name AS route,
    departure_name,
    destination_name,
    COUNT(*) AS trip_count,
    AVG(distance) AS avg_distance,
    AVG(passenger_price) AS avg_price
FROM trips
WHERE departure_name IS NOT NULL AND destination_name IS NOT NULL
GROUP BY departure_name, destination_name
ORDER BY trip_count DESC
LIMIT 20;
