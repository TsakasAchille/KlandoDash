-- Migration: Add split name AI columns
-- Description: Adds separate columns for first name and last name extracted by AI.

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS id_card_first_name_ai text,
ADD COLUMN IF NOT EXISTS id_card_last_name_ai text,
ADD COLUMN IF NOT EXISTS driver_license_first_name_ai text,
ADD COLUMN IF NOT EXISTS driver_license_last_name_ai text;
