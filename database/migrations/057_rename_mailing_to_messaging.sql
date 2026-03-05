-- =============================================================================
-- Migration: Rename Mailing to Messaging
-- Description: Expand mailing to support both Email and WhatsApp (Direct Messaging).
-- =============================================================================

-- Rename the table
ALTER TABLE IF EXISTS public.dash_marketing_emails RENAME TO dash_marketing_messages;

-- Create channel type and column
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_channel') THEN
        CREATE TYPE public.message_channel AS ENUM ('EMAIL', 'WHATSAPP');
    END IF;
END $$;

ALTER TABLE public.dash_marketing_messages ADD COLUMN IF NOT EXISTS channel public.message_channel DEFAULT 'EMAIL';

-- Rename specific email columns to be more generic
ALTER TABLE public.dash_marketing_messages RENAME COLUMN recipient_email TO recipient_contact;

-- Update status to allow TRASH
ALTER TYPE public.email_status ADD VALUE IF NOT EXISTS 'TRASH';

-- Indices for channel
CREATE INDEX IF NOT EXISTS idx_marketing_messages_channel ON public.dash_marketing_messages(channel);

-- Update RLS (Policies often use table name, but ALTER TABLE RENAME handles this in Postgres)
-- Just ensuring comments are updated
COMMENT ON TABLE public.dash_marketing_messages IS 'Stores direct messages (Email/WhatsApp) drafts and history.';
COMMENT ON COLUMN public.dash_marketing_messages.recipient_contact IS 'Email address or WhatsApp phone number of the recipient.';
