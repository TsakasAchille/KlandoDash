-- Migration 068: Add start_date to roadmap_items for Gantt chart
ALTER TABLE public.roadmap_items 
ADD COLUMN IF NOT EXISTS start_date DATE;

COMMENT ON COLUMN public.roadmap_items.start_date IS 'Start date for the Gantt chart visualization.';
