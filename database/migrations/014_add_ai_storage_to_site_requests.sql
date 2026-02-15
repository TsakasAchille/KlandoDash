-- ==============================================================================
-- Migration: Add AI Storage to Site Trip Requests
-- Description: Adds columns to store AI recommendations and their last update time.
-- ==============================================================================

ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS ai_recommendation TEXT,
ADD COLUMN IF NOT EXISTS ai_updated_at TIMESTAMPTZ;

-- Optional: Index for filtering requests with/without recommendations
CREATE INDEX IF NOT EXISTS idx_site_trip_requests_ai_updated_at ON public.site_trip_requests(ai_updated_at);
