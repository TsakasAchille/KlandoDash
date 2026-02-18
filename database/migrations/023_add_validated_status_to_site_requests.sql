-- Migration: Add 'VALIDATED' status to site_trip_requests
-- Description: Adds 'VALIDATED' to the allowed statuses for site trip requests.

ALTER TABLE public.site_trip_requests DROP CONSTRAINT IF EXISTS site_trip_requests_status_check;

ALTER TABLE public.site_trip_requests 
ADD CONSTRAINT site_trip_requests_status_check 
CHECK (status IN ('NEW', 'REVIEWED', 'CONTACTED', 'IGNORED', 'VALIDATED'));
