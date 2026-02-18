-- Migration: Add Marketing Comments and Visual Linking
-- Description: Supports comments and links between communications/emails and assets.

-- Add asset linking to communications
ALTER TABLE public.dash_marketing_communications 
ADD COLUMN IF NOT EXISTS asset_id uuid REFERENCES public.dash_marketing_assets(id),
ADD COLUMN IF NOT EXISTS image_url text;

-- Add asset linking to emails (already has image_url)
ALTER TABLE public.dash_marketing_emails 
ADD COLUMN IF NOT EXISTS asset_id uuid REFERENCES public.dash_marketing_assets(id);

-- Create Comments table for Editorial Discussion
CREATE TABLE IF NOT EXISTS public.dash_marketing_comments (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    comm_id uuid REFERENCES public.dash_marketing_communications(id) ON DELETE CASCADE,
    email_id uuid REFERENCES public.dash_marketing_emails(id) ON DELETE CASCADE,
    user_email text NOT NULL REFERENCES public.dash_authorized_users(email),
    content text NOT NULL,
    created_at timestamptz DEFAULT now(),
    -- Constraint: either comm_id or email_id must be set
    CONSTRAINT either_id_check CHECK (
        (comm_id IS NOT NULL AND email_id IS NULL) OR 
        (comm_id IS NULL AND email_id IS NOT NULL)
    )
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_marketing_comments_comm ON public.dash_marketing_comments(comm_id);
CREATE INDEX IF NOT EXISTS idx_marketing_comments_email ON public.dash_marketing_comments(email_id);

-- RLS for comments
ALTER TABLE public.dash_marketing_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can manage marketing comments" 
ON public.dash_marketing_comments FOR ALL TO authenticated USING (true);
