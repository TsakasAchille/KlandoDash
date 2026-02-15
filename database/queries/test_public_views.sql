-- ==============================================================================
-- Test Data for Website Integration
-- Description: Inserts mock trips to verify 'public_pending_trips' 
--              and 'public_completed_trips' views.
-- ==============================================================================

-- 1. Cleanup old test data
DELETE FROM public.trips WHERE trip_id LIKE 'test-%';

-- 2. Insert new test trips
-- Using a valid driver_id (Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2) found in the database
INSERT INTO public.trips (
    trip_id, 
    driver_id, 
    departure_name, 
    destination_name, 
    departure_schedule, 
    seats_available, 
    seats_published, 
    status,
    passenger_price
) VALUES 
-- PENDING TRIPS (Will show in 'public_pending_trips')
('test-pending-1', 'Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2', 'Dakar', 'Saint-Louis', NOW() + INTERVAL '1 day', 3, 4, 'PENDING', 5000),
('test-pending-2', 'Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2', 'Thiès', 'Dakar', NOW() + INTERVAL '2 days', 2, 4, 'PENDING', 3000),
('test-pending-3', 'Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2', 'Mbour', 'Dakar', NOW() + INTERVAL '5 hours', 1, 4, 'PENDING', 2500),

-- COMPLETED TRIPS (Will show in 'public_completed_trips' for social proof)
('test-completed-1', 'Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2', 'Dakar', 'Mbour', NOW() - INTERVAL '1 day', 0, 4, 'COMPLETED', 4500),
('test-completed-2', 'Up0hK5DlhwQ7Y9UlcOEqtpJgo3O2', 'Saint-Louis', 'Dakar', NOW() - INTERVAL '2 days', 0, 4, 'COMPLETED', 5000);

-- 3. Verification Queries
-- Check live trips for landing page
SELECT * FROM public.public_pending_trips ORDER BY departure_time ASC;

-- Check social proof (completed trips)
SELECT * FROM public.public_completed_trips;
