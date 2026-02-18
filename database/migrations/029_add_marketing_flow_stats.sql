-- Migration: Add Marketing Flow Statistics Function
-- Description: Aggregates validated requests to identify top routes and heatmaps.

CREATE OR REPLACE FUNCTION public.get_marketing_flow_stats()
RETURNS TABLE (
    origin_city text,
    destination_city text,
    request_count bigint,
    avg_origin_lat double precision,
    avg_origin_lng double precision,
    avg_dest_lat double precision,
    avg_dest_lng double precision
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.origin_city,
        r.destination_city,
        COUNT(*) as request_count,
        AVG(r.origin_lat) as avg_origin_lat,
        AVG(r.origin_lng) as avg_origin_lng,
        AVG(r.destination_lat) as avg_dest_lat,
        AVG(r.destination_lng) as avg_dest_lng
    FROM 
        public.site_trip_requests r
    WHERE 
        r.origin_lat IS NOT NULL 
        AND r.destination_lat IS NOT NULL
    GROUP BY 
        r.origin_city, r.destination_city
    ORDER BY 
        request_count DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.get_marketing_flow_stats() TO authenticated;
