-- ==============================================================================
-- Migration: Add Polyline to Site Trip Requests
-- Description: Adds a polyline column to store the intended route for 
--              visualizing client requests on the map.
-- ==============================================================================

ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS polyline text;
