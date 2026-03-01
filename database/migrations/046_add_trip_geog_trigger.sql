-- Migration: Add Trigger for Automatic Route Geography Update
-- Description: Automatically decodes polylines into geography objects on every insert or update.

-- 1. Create the trigger function
CREATE OR REPLACE FUNCTION public.fn_sync_trip_route_geog()
RETURNS TRIGGER AS $$
BEGIN
    -- Only decode if polyline exists and has changed (or is new)
    IF (TG_OP = 'INSERT' AND NEW.polyline IS NOT NULL) OR 
       (TG_OP = 'UPDATE' AND NEW.polyline IS DISTINCT FROM OLD.polyline) THEN
        BEGIN
            NEW.route_geog := public.decode_polyline(NEW.polyline)::geography;
        EXCEPTION WHEN OTHERS THEN
            -- In case of invalid polyline, don't crash the insert, just set to NULL
            NEW.route_geog := NULL;
            RAISE WARNING 'Failed to decode polyline for trip %', NEW.trip_id;
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Attach the trigger to the trips table
DROP TRIGGER IF EXISTS tr_sync_trip_route_geog ON public.trips;
CREATE TRIGGER tr_sync_trip_route_geog
BEFORE INSERT OR UPDATE ON public.trips
FOR EACH ROW
EXECUTE FUNCTION public.fn_sync_trip_route_geog();

-- 3. Initial sync for any remaining trips without route_geog
UPDATE public.trips 
SET route_geog = decode_polyline(polyline)::geography 
WHERE polyline IS NOT NULL AND route_geog IS NULL;
