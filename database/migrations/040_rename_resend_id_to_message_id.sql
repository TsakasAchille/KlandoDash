-- Migration: Rename resend_id to message_id
-- Description: Standardizes the column name for the email message identifier across different providers.

ALTER TABLE public.dash_marketing_emails 
RENAME COLUMN resend_id TO message_id;

COMMENT ON COLUMN public.dash_marketing_emails.message_id IS 'Identifier returned by the email provider (Nodemailer/Google/etc)';
