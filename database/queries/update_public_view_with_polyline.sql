-- ==============================================================================
-- Update: public_pending_trips View
-- Description: Adds polyline and coordinates to the public view for website maps.
-- Execute this in the Supabase SQL Editor.
-- ==============================================================================

CREATE OR REPLACE VIEW public.public_pending_trips AS
SELECT
    trip_id AS id,
    departure_name AS departure_city,
    destination_name AS arrival_city,
    departure_schedule AS departure_time,
    seats_available,
    polyline,
    destination_latitude,
    destination_longitude
FROM
    public.trips
WHERE
    status = 'PENDING'
    AND departure_schedule > NOW()
    AND seats_available > 0;

-- Ensure permissions are still active
GRANT SELECT ON public.public_pending_trips TO anon;
GRANT SELECT ON public.public_pending_trips TO authenticated;
