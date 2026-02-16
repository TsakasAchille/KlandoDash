-- ==============================================================================
-- Migration: Clear Site Request Matches and AI Analyses
-- Description: Completely resets scanner results and Gemini recommendations
--              to allow for clean re-testing of the matching system.
-- ==============================================================================

BEGIN;

-- 1. Remove all persistent scanner results
DELETE FROM public.site_trip_request_matches;

-- 2. Clear AI recommendations and timestamps from site requests
UPDATE public.site_trip_requests 
SET 
    ai_recommendation = NULL, 
    ai_updated_at = NULL;

-- 3. Notify schema reload
NOTIFY pgrst, 'reload schema';

COMMIT;

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE 'Table site_trip_request_matches vidée et analyses IA réinitialisées avec succès.';
END $$;
