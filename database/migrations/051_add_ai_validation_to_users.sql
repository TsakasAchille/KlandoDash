-- Migration: Add AI Validation fields to users
-- Description: Adds fields to store extracted document numbers and AI validation reports.

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS id_card_number text,
ADD COLUMN IF NOT EXISTS driver_license_number text,
ADD COLUMN IF NOT EXISTS ai_validation_status text DEFAULT 'PENDING', -- PENDING, SUCCESS, FAILED, WARNING
ADD COLUMN IF NOT EXISTS ai_validation_report jsonb;

-- Index for searching duplicates
CREATE INDEX IF NOT EXISTS idx_users_id_card_number ON public.users(id_card_number);
CREATE INDEX IF NOT EXISTS idx_users_driver_license_number ON public.users(driver_license_number);
