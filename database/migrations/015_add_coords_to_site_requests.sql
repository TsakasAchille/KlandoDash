-- ==============================================================================
-- Migration: Add Coordinates to Site Trip Requests
-- Description: Adds latitude and longitude columns to store geocoded locations
--              for better proximity matching with available trips.
-- ==============================================================================

ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS origin_lat double precision,
ADD COLUMN IF NOT EXISTS origin_lng double precision,
ADD COLUMN IF NOT EXISTS destination_lat double precision,
ADD COLUMN IF NOT EXISTS destination_lng double precision;

-- Index for spatial queries if needed (PostGIS would be better but let's start simple)
-- If PostGIS is not available, we use basic B-tree or just standard columns.
