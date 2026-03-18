-- Migration 067: Add planning_stage to roadmap_items
-- Adds temporal buckets for better project management organization.

ALTER TABLE public.roadmap_items 
ADD COLUMN IF NOT EXISTS planning_stage TEXT DEFAULT 'backlog' 
CHECK (planning_stage IN ('now', 'next', 'later', 'backlog'));

-- Add a target date for milestones
ALTER TABLE public.roadmap_items 
ADD COLUMN IF NOT EXISTS target_date DATE;

-- Comments for documentation
COMMENT ON COLUMN public.roadmap_items.planning_stage IS 'Temporal bucket: now (immediate), next (1-2 months), later (3-6 months), backlog (future).';
COMMENT ON COLUMN public.roadmap_items.target_date IS 'Optional specific date for a milestone or delivery.';
