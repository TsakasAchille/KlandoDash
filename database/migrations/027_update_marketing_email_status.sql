-- Migration: Add 'TRASH' status to marketing emails
-- Description: Updates the enum type to allow deleting emails to a trash folder.

-- Note: We use ALTER TYPE to add the value to the existing enum
ALTER TYPE public.email_status ADD VALUE IF NOT EXISTS 'TRASH';
