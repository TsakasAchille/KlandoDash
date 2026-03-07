-- Migration: Add Type to Site Trip Requests
-- Description: Distinguishes between Passenger demands and Driver offers from external sources.

ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS request_type text DEFAULT 'PASSENGER' 
CHECK (request_type IN ('PASSENGER', 'DRIVER'));

-- Index for filtering
CREATE INDEX IF NOT EXISTS idx_site_trip_requests_type ON public.site_trip_requests(request_type);
