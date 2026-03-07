-- Migration: Add Source to Site Trip Requests
-- Description: Allows distinguishing between requests from the website and those from Facebook/Social Media.

ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS source text DEFAULT 'SITE' 
CHECK (source IN ('SITE', 'FACEBOOK', 'WHATSAPP', 'IA_AGENT'));

-- Index for filtering by source
CREATE INDEX IF NOT EXISTS idx_site_trip_requests_source ON public.site_trip_requests(source);
