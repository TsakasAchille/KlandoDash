-- Migration 069: Add custom_color to roadmap_items for per-task color customization
ALTER TABLE public.roadmap_items
ADD COLUMN IF NOT EXISTS custom_color TEXT;

COMMENT ON COLUMN public.roadmap_items.custom_color IS 'Optional hex color override for the Gantt bar (e.g. #EBC33F). Falls back to planning_stage color if null.';
