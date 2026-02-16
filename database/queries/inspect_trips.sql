-- ==============================================================================
-- Requêtes d'inspection des trajets (Trips)
-- Utilisation : Copier-coller dans l'éditeur SQL de Supabase
-- ==============================================================================

-- 1. Voir les 50 derniers trajets (tous statuts confondus)
SELECT 
    trip_id, 
    departure_name, 
    destination_name, 
    departure_schedule, 
    status,
    seats_available,
    created_at
FROM public.trips
ORDER BY created_at DESC
LIMIT 50;

-- 2. Chercher un trajet spécifique par son ID (avec ou sans préfixe TRIP-)
-- Remplacez l'ID ci-dessous par celui que vous cherchez
SELECT 
    trip_id, 
    departure_name, 
    destination_name, 
    status,
    polyline IS NOT NULL as has_polyline
FROM public.trips 
WHERE trip_id IN ('TRIP-1771178498501765', '1771178498501765');

-- 3. Voir uniquement les trajets que l'IA prend en compte (ACTIVE ou PENDING)
SELECT 
    trip_id, 
    departure_name, 
    destination_name, 
    departure_schedule,
    status
FROM public.trips
WHERE status IN ('ACTIVE', 'PENDING')
  AND departure_schedule > NOW()
ORDER BY departure_schedule ASC;

-- 4. Compter les trajets par statut pour voir l'état de la base
SELECT status, count(*) 
FROM public.trips 
GROUP BY status;
