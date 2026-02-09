-- ==============================================================================
-- Migration: Create Site Trip Requests Table
-- Description: Stores intent/requests from the website visitors.
-- Prefix 'site_' indicates data originates from the public landing page.
-- ==============================================================================

CREATE TABLE IF NOT EXISTS public.site_trip_requests (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    origin_city text NOT NULL,
    destination_city text NOT NULL,
    desired_date timestamp with time zone,
    contact_info text NOT NULL, -- Email or Phone
    status text DEFAULT 'NEW' CHECK (status IN ('NEW', 'REVIEWED', 'CONTACTED', 'IGNORED')),
    created_at timestamp with time zone DEFAULT now(),
    notes text -- To be used by admins in the dashboard
);

-- Index for performance in the dashboard
CREATE INDEX IF NOT EXISTS idx_site_trip_requests_status ON public.site_trip_requests(status);
CREATE INDEX IF NOT EXISTS idx_site_trip_requests_created_at ON public.site_trip_requests(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.site_trip_requests ENABLE ROW LEVEL SECURITY;

-- 1. Allow Anyone (anon) to insert requests from the website
CREATE POLICY "Allow public to submit requests" 
ON public.site_trip_requests 
FOR INSERT 
TO anon, authenticated
WITH CHECK (true);

-- 2. Allow only dashboard users (authenticated) to view and update them
CREATE POLICY "Allow dashboard users to manage requests" 
ON public.site_trip_requests 
FOR ALL 
TO authenticated 
USING (true)
WITH CHECK (true);

-- Grant permissions to anon for inserts
GRANT INSERT ON public.site_trip_requests TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.site_trip_requests TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;
