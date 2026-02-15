-- ==============================================================================
-- Query: Clear all AI Recommendations
-- Description: Resets AI matching data for all site trip requests.
-- ==============================================================================

UPDATE public.site_trip_requests
SET 
    ai_recommendation = NULL,
    ai_updated_at = NULL;
