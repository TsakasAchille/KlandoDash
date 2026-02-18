-- Migration: Add image_url to dash_marketing_emails
-- Description: Stores the URL of the map screenshot for email embedding.

ALTER TABLE public.dash_marketing_emails 
ADD COLUMN IF NOT EXISTS image_url text;
