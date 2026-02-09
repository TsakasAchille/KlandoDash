-- ==============================================================================
-- Migration: Create Public View for Website Integration
-- Description: Creates a secure view to expose only necessary PENDING trip data
--              for the landing page/website, preventing exposure of sensitive columns.
-- ==============================================================================

-- 1. Create the View
CREATE OR REPLACE VIEW public.public_pending_trips AS
SELECT
    trip_id AS id,
    departure_name AS departure_city,
    destination_name AS arrival_city,
    departure_schedule AS departure_time,
    seats_available
FROM
    public.trips
WHERE
    status = 'PENDING'
    AND departure_schedule > NOW()
    AND seats_available > 0;

-- 2. Grant Permissions
-- Allow anonymous users (and authenticated ones) to SELECT from this view
GRANT SELECT ON public.public_pending_trips TO anon;
GRANT SELECT ON public.public_pending_trips TO authenticated;

-- Note: Since 'trips' has RLS enabled, the user querying this view must also
-- satisfy the RLS policy of the 'trips' table.
-- Existing policy allows reading 'PENDING' trips, so this works perfectly.
