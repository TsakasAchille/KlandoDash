-- Migration 072: Create default "DASH" board and assign existing planning items to it
DO $$
DECLARE
  board_id UUID;
BEGIN
  INSERT INTO public.planning_boards (name, description)
  VALUES ('DASH', 'Planning principal du dashboard')
  RETURNING id INTO board_id;

  UPDATE public.roadmap_items
  SET planning_board_id = board_id
  WHERE is_planning = true AND planning_board_id IS NULL;
END $$;
