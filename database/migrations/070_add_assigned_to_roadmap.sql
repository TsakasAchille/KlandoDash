-- Migration 070: Add assigned_to for task assignment to dash users
ALTER TABLE public.roadmap_items
ADD COLUMN IF NOT EXISTS assigned_to TEXT[] DEFAULT '{}';

COMMENT ON COLUMN public.roadmap_items.assigned_to IS 'Array of dash_authorized_users emails assigned to this task.';
