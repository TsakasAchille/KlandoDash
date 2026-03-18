-- Migration 065: Add is_planning column to roadmap_items
-- Adds the ability to separate "official roadmap" items from "planning/backlog" items.

ALTER TABLE public.roadmap_items 
ADD COLUMN IF NOT EXISTS is_planning BOOLEAN DEFAULT false;

-- Update RLS policies to include DELETE
DROP POLICY IF EXISTS "Roadmap items are editable by admins only" ON public.roadmap_items;

CREATE POLICY "Roadmap items are manageable by admins" ON public.roadmap_items
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.dash_authorized_users
            WHERE email = auth.jwt()->>'email' AND role = 'admin'
        )
    );

-- Comments for documentation
COMMENT ON COLUMN public.roadmap_items.is_planning IS 'True if the item is in the planning/backlog stage, false if it is part of the official roadmap.';
