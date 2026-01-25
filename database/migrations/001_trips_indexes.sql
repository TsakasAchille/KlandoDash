-- =====================================================
-- Indexes pour la table trips
-- =====================================================

-- Index sur le statut (filtrage fréquent)
CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(status);

-- Index sur la date de départ (tri et filtrage par date)
CREATE INDEX IF NOT EXISTS idx_trips_departure_schedule ON trips(departure_schedule DESC);

-- Index sur le conducteur (jointure avec users)
CREATE INDEX IF NOT EXISTS idx_trips_driver_id ON trips(driver_id);

-- Index composé pour les recherches fréquentes (status + date)
CREATE INDEX IF NOT EXISTS idx_trips_status_departure ON trips(status, departure_schedule DESC);

-- Index pour la recherche géographique (départ)
CREATE INDEX IF NOT EXISTS idx_trips_departure_geo ON trips(departure_latitude, departure_longitude);

-- Index pour la recherche géographique (destination)
CREATE INDEX IF NOT EXISTS idx_trips_destination_geo ON trips(destination_latitude, destination_longitude);

-- Index sur created_at pour le tri par date de création
CREATE INDEX IF NOT EXISTS idx_trips_created_at ON trips(created_at DESC);

-- =====================================================
-- Vérifier les indexes existants
-- =====================================================
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'trips';
