-- Migration: Add Context to Marketing Messages
-- Description: Stores the origin source and request type (Passenger/Driver) for marketing messages.

ALTER TABLE public.dash_marketing_messages 
ADD COLUMN IF NOT EXISTS source text,
ADD COLUMN IF NOT EXISTS request_type text;

-- Index for better filtering
CREATE INDEX IF NOT EXISTS idx_marketing_messages_source ON public.dash_marketing_messages(source);
CREATE INDEX IF NOT EXISTS idx_marketing_messages_type ON public.dash_marketing_messages(request_type);
