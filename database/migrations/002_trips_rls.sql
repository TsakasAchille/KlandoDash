-- =====================================================
-- Row Level Security (RLS) pour trips
-- =====================================================

-- Activer RLS sur trips
ALTER TABLE trips ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------
-- Politique: Lecture publique des trajets actifs
-- Tout le monde peut voir les trajets ACTIVE/PENDING
-- -----------------------------------------------------
CREATE POLICY "trips_select_public" ON trips
    FOR SELECT
    USING (status IN ('ACTIVE', 'PENDING', 'COMPLETED'));

-- -----------------------------------------------------
-- Politique: Le conducteur peut voir tous ses trajets
-- -----------------------------------------------------
CREATE POLICY "trips_select_own" ON trips
    FOR SELECT
    USING (driver_id = auth.uid()::text);

-- -----------------------------------------------------
-- Politique: Seul le conducteur peut modifier son trajet
-- -----------------------------------------------------
CREATE POLICY "trips_update_own" ON trips
    FOR UPDATE
    USING (driver_id = auth.uid()::text)
    WITH CHECK (driver_id = auth.uid()::text);

-- -----------------------------------------------------
-- Politique: Seul le conducteur peut supprimer son trajet
-- -----------------------------------------------------
CREATE POLICY "trips_delete_own" ON trips
    FOR DELETE
    USING (driver_id = auth.uid()::text);

-- -----------------------------------------------------
-- Politique: Utilisateur authentifié peut créer un trajet
-- -----------------------------------------------------
CREATE POLICY "trips_insert_auth" ON trips
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

-- =====================================================
-- RLS pour bookings
-- =====================================================

ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Le passager peut voir ses réservations
CREATE POLICY "bookings_select_passenger" ON bookings
    FOR SELECT
    USING (user_id = auth.uid()::text);

-- Le conducteur peut voir les réservations de ses trajets
CREATE POLICY "bookings_select_driver" ON bookings
    FOR SELECT
    USING (
        trip_id IN (
            SELECT trip_id FROM trips WHERE driver_id = auth.uid()::text
        )
    );

-- Le passager peut créer une réservation
CREATE POLICY "bookings_insert_auth" ON bookings
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL AND user_id = auth.uid()::text);

-- Le passager peut annuler sa réservation
CREATE POLICY "bookings_update_own" ON bookings
    FOR UPDATE
    USING (user_id = auth.uid()::text);

-- =====================================================
-- Note: Pour le dashboard admin, utiliser service_role
-- qui bypass RLS
-- =====================================================
