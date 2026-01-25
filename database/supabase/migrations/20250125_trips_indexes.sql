-- Index pour la table trips
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);
CREATE INDEX IF NOT EXISTS idx_trips_departure_schedule ON trips(departure_schedule DESC);
CREATE INDEX IF NOT EXISTS idx_trips_driver_id ON trips(driver_id);
CREATE INDEX IF NOT EXISTS idx_trips_status_departure ON trips(status, departure_schedule DESC);
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);
