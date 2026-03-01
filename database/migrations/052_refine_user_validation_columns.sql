-- Migration: Refine AI Extraction columns for users
-- Description: Adds specific columns to store data extracted by AI from documents.

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS id_card_name_ai text,
ADD COLUMN IF NOT EXISTS id_card_expiry_ai date,
ADD COLUMN IF NOT EXISTS driver_license_name_ai text,
ADD COLUMN IF NOT EXISTS driver_license_expiry_ai date;

-- Note: id_card_number et driver_license_number ont déjà été ajoutés dans la migration 051.
