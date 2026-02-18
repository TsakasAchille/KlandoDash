-- Migration: Add is_ai_generated flag to marketing emails
-- Description: Allows explicit separation between manual drafts and AI suggestions.

ALTER TABLE public.dash_marketing_emails 
ADD COLUMN IF NOT EXISTS is_ai_generated boolean DEFAULT false;

-- Index for filtering
CREATE INDEX IF NOT EXISTS idx_marketing_emails_is_ai ON public.dash_marketing_emails(is_ai_generated);
