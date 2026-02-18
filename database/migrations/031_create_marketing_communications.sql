-- Migration: Create Marketing Communications Table
-- Description: Stores AI-generated communication ideas and social media posts.

CREATE TYPE comm_type AS ENUM ('IDEA', 'POST');
CREATE TYPE comm_platform AS ENUM ('TIKTOK', 'INSTAGRAM', 'X', 'WHATSAPP', 'GENERAL');

CREATE TABLE IF NOT EXISTS public.dash_marketing_communications (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    type comm_type NOT NULL,
    platform comm_platform DEFAULT 'GENERAL',
    title text NOT NULL,
    content text NOT NULL, -- Markdown content (post text)
    hashtags text[], -- Suggested hashtags
    visual_suggestion text, -- Description of recommended image/video
    status text DEFAULT 'PENDING',
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- Index for chronological reading
CREATE INDEX idx_marketing_comm_type ON public.dash_marketing_communications(type);
CREATE INDEX idx_marketing_comm_created_at ON public.dash_marketing_communications(created_at DESC);

-- Enable RLS
ALTER TABLE public.dash_marketing_communications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can manage marketing communications" 
ON public.dash_marketing_communications FOR ALL TO authenticated USING (true);
