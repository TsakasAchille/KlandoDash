-- Migration: Add support for multiple images with descriptions
-- Description: Adds a JSONB 'images' column to dash_marketing_emails and migrates legacy data.

-- 1. Create the new JSONB column
ALTER TABLE public.dash_marketing_emails ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]'::jsonb;

-- 2. Migrate existing single images to the new array format
UPDATE public.dash_marketing_emails 
SET images = jsonb_build_array(jsonb_build_object('url', image_url, 'description', 'Capture originale'))
WHERE image_url IS NOT NULL AND (images IS NULL OR jsonb_array_length(images) = 0);

-- 3. Documentation of JSONB structure:
-- Array of objects: [{ "url": "https://...", "description": "Context description" }]

-- NOTE: If you still see 'column not found' after running this, 
-- please go to Supabase Dashboard > Settings > API > 'Reload PostgREST Schema'.
