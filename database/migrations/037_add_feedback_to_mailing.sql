-- Migration: Add Feedback and Reasoning to Marketing Mailing
-- Description: Adds columns to store AI reasoning and admin feedback for learning loops.

ALTER TABLE public.dash_marketing_emails 
ADD COLUMN IF NOT EXISTS ai_reasoning text,
ADD COLUMN IF NOT EXISTS is_liked boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS admin_feedback text;

-- Index for liked content to help IA find good examples
CREATE INDEX IF NOT EXISTS idx_marketing_emails_liked ON public.dash_marketing_emails(is_liked) WHERE is_liked = true;
