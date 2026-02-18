-- Migration: Create Marketing Mailing Table
-- Description: Stores email drafts and sending history for marketing campaigns.

CREATE TYPE email_status AS ENUM ('DRAFT', 'SENT', 'FAILED');
CREATE TYPE email_category AS ENUM ('WELCOME', 'MATCH_FOUND', 'RETENTION', 'PROMO', 'GENERAL');

CREATE TABLE IF NOT EXISTS public.dash_marketing_emails (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    category email_category DEFAULT 'GENERAL',
    subject text NOT NULL,
    content text NOT NULL, -- Markdown/HTML content
    recipient_email text NOT NULL,
    recipient_name text,
    status email_status DEFAULT 'DRAFT',
    resend_id text, -- ID returned by Resend API
    error_message text,
    created_at timestamptz DEFAULT now(),
    sent_at timestamptz,
    created_by uuid REFERENCES auth.users(id)
);

-- Index for history
CREATE INDEX idx_marketing_emails_status ON public.dash_marketing_emails(status);
CREATE INDEX idx_marketing_emails_created_at ON public.dash_marketing_emails(created_at DESC);

-- RLS
ALTER TABLE public.dash_marketing_emails ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can manage marketing emails" 
ON public.dash_marketing_emails FOR ALL TO authenticated USING (true);
