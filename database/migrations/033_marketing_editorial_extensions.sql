-- Migration: Add scheduling and Assets for Editorial
-- Description: Supports calendar scheduling and asset management.

ALTER TABLE public.dash_marketing_communications 
ADD COLUMN IF NOT EXISTS scheduled_at timestamptz;

CREATE TABLE IF NOT EXISTS public.dash_marketing_assets (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    file_url text NOT NULL,
    file_name text,
    file_type text, -- 'IMAGE', 'VIDEO'
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- Index for calendar performance
CREATE INDEX IF NOT EXISTS idx_marketing_comm_scheduled ON public.dash_marketing_communications(scheduled_at);

-- RLS for assets
ALTER TABLE public.dash_marketing_assets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can manage assets" 
ON public.dash_marketing_assets FOR ALL TO authenticated USING (true);
