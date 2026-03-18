-- Migration 071: Create planning_boards table for multiple Gantt views
CREATE TABLE IF NOT EXISTS public.planning_boards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    color TEXT,
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc', now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc', now()) NOT NULL
);

ALTER TABLE public.planning_boards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Planning boards are viewable by everyone"
    ON public.planning_boards FOR SELECT USING (true);

CREATE POLICY "Planning boards are manageable by admins"
    ON public.planning_boards FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.dash_authorized_users
            WHERE email = auth.jwt()->>'email' AND role = 'admin'
        )
    );

-- Add FK on roadmap_items
ALTER TABLE public.roadmap_items
ADD COLUMN IF NOT EXISTS planning_board_id UUID REFERENCES public.planning_boards(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_roadmap_items_board ON public.roadmap_items(planning_board_id);
