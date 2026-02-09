-- ==============================================================================
-- Migration: Create Public View for Completed Trips
-- Description: Creates a secure view to expose only necessary COMPLETED trip data
--              for social proof on the landing page.
-- ==============================================================================

-- 1. Create the View
CREATE OR REPLACE VIEW public.public_completed_trips AS
SELECT
    trip_id AS id,
    departure_name AS departure_city,
    destination_name AS arrival_city,
    departure_schedule AS departure_time
FROM
    public.trips
WHERE
    status = 'COMPLETED'
ORDER BY
    departure_schedule DESC
LIMIT 10;

-- 2. Grant Permissions
GRANT SELECT ON public.public_completed_trips TO anon;
GRANT SELECT ON public.public_completed_trips TO authenticated;
