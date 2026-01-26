-- Migration: Add profile fields to dash_authorized_users
-- Date: 2026-01-26
-- Description: Adds display_name and avatar_url to the dash_authorized_users table.

ALTER TABLE public.dash_authorized_users
ADD COLUMN display_name TEXT,
ADD COLUMN avatar_url TEXT;

-- Optional: If you want to update existing rows with some default or initial values
-- For example, setting display_name from the email if it's not null
-- UPDATE public.dash_authorized_users
-- SET display_name = split_part(email, '@', 1)
-- WHERE display_name IS NULL;
