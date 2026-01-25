-- =====================================================
-- TEST: Requêtes trips pour le frontend
-- Exécuter dans Supabase SQL Editor
-- =====================================================

-- -----------------------------------------------------
-- TEST 1: Liste des trajets (tableau principal)
-- Colonnes: trip_id, departure, destination, date, distance, places, prix, status
-- -----------------------------------------------------
SELECT
    'TEST 1: Liste trips' AS test_name,
    COUNT(*) AS total_rows
FROM trips;

SELECT
    trip_id,
    departure_name,
    destination_name,
    departure_schedule,
    distance,
    seats_available,
    seats_published,
    passenger_price,
    status,
    driver_id
FROM trips
ORDER BY departure_schedule DESC
LIMIT 10;

-- -----------------------------------------------------
-- TEST 2: Détail d'un trajet avec conducteur
-- Simule getTripDetail()
-- -----------------------------------------------------
SELECT
    'TEST 2: Detail trip avec driver' AS test_name;

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
    -- Driver info
    u.uid AS driver_id,
    u.display_name AS driver_name,
    u.photo_url AS driver_photo,
    u.phone_number AS driver_phone,
    u.rating AS driver_rating,
    u.rating_count AS driver_rating_count
FROM trips t
LEFT JOIN users u ON t.driver_id = u.uid
LIMIT 5;

-- -----------------------------------------------------
-- TEST 3: Statistiques globales
-- Simule getTripsStats()
-- -----------------------------------------------------
SELECT
    'TEST 3: Stats globales' AS test_name;

SELECT
    COUNT(*) AS total_trips,
    COUNT(*) FILTER (WHERE status = 'ACTIVE') AS active_trips,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_trips,
    COUNT(*) FILTER (WHERE status = 'PENDING') AS pending_trips,
    COUNT(*) FILTER (WHERE status = 'CANCELLED') AS cancelled_trips,
    COALESCE(SUM(distance), 0) AS total_distance_km,
    COALESCE(SUM(seats_booked), 0) AS total_seats_booked,
    COALESCE(AVG(passenger_price), 0) AS avg_price
FROM trips;

-- -----------------------------------------------------
-- TEST 4: Répartition par statut
-- Pour le pie chart
-- -----------------------------------------------------
SELECT
    'TEST 4: Répartition par statut' AS test_name;

SELECT
    status,
    COUNT(*) AS count
FROM trips
GROUP BY status
ORDER BY count DESC;

-- -----------------------------------------------------
-- TEST 5: Trajets à venir
-- Simule getUpcomingTrips()
-- -----------------------------------------------------
SELECT
    'TEST 5: Trajets à venir' AS test_name;

SELECT
    t.trip_id,
    t.departure_name,
    t.destination_name,
    t.departure_schedule,
    t.seats_available,
    t.passenger_price,
    u.display_name AS driver_name
FROM trips t
LEFT JOIN users u ON t.driver_id = u.uid
WHERE t.departure_schedule > NOW()
  AND t.status IN ('ACTIVE', 'PENDING')
ORDER BY t.departure_schedule ASC
LIMIT 10;

-- -----------------------------------------------------
-- TEST 6: Top routes (départ → destination)
-- Pour les stats
-- -----------------------------------------------------
SELECT
    'TEST 6: Top routes' AS test_name;

SELECT
    departure_name || ' → ' || destination_name AS route,
    COUNT(*) AS trip_count,
    AVG(distance) AS avg_distance,
    AVG(passenger_price) AS avg_price
FROM trips
WHERE departure_name IS NOT NULL
  AND destination_name IS NOT NULL
GROUP BY departure_name, destination_name
ORDER BY trip_count DESC
LIMIT 10;

-- -----------------------------------------------------
-- TEST 7: Vérifier les données manquantes
-- Important pour éviter les erreurs frontend
-- -----------------------------------------------------
SELECT
    'TEST 7: Données manquantes' AS test_name;

SELECT
    COUNT(*) FILTER (WHERE departure_name IS NULL) AS missing_departure_name,
    COUNT(*) FILTER (WHERE destination_name IS NULL) AS missing_destination_name,
    COUNT(*) FILTER (WHERE departure_schedule IS NULL) AS missing_schedule,
    COUNT(*) FILTER (WHERE distance IS NULL) AS missing_distance,
    COUNT(*) FILTER (WHERE passenger_price IS NULL) AS missing_price,
    COUNT(*) FILTER (WHERE driver_id IS NULL) AS missing_driver,
    COUNT(*) FILTER (WHERE status IS NULL) AS missing_status
FROM trips;

-- -----------------------------------------------------
-- TEST 8: Vérifier la jointure driver
-- Combien de trips ont un driver valide?
-- -----------------------------------------------------
SELECT
    'TEST 8: Jointure driver' AS test_name;

SELECT
    COUNT(*) AS total_trips,
    COUNT(u.uid) AS trips_with_valid_driver,
    COUNT(*) - COUNT(u.uid) AS trips_without_driver
FROM trips t
LEFT JOIN users u ON t.driver_id = u.uid;

-- -----------------------------------------------------
-- TEST 9: Performance check - EXPLAIN
-- Vérifie que les index sont utilisés
-- -----------------------------------------------------
SELECT
    'TEST 9: Index usage check' AS test_name;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    trip_id,
    departure_name,
    destination_name,
    departure_schedule,
    status
FROM trips
WHERE status = 'ACTIVE'
ORDER BY departure_schedule DESC
LIMIT 50;

-- -----------------------------------------------------
-- TEST 10: Passagers par trajet (bookings)
-- -----------------------------------------------------
SELECT
    'TEST 10: Bookings par trip' AS test_name;

SELECT
    t.trip_id,
    t.departure_name,
    t.destination_name,
    t.seats_published,
    t.seats_booked,
    COUNT(b.id) AS booking_count,
    COALESCE(SUM(b.seats), 0) AS total_booked_seats
FROM trips t
LEFT JOIN bookings b ON t.trip_id = b.trip_id
GROUP BY t.trip_id, t.departure_name, t.destination_name, t.seats_published, t.seats_booked
HAVING COUNT(b.id) > 0
ORDER BY booking_count DESC
LIMIT 10;
