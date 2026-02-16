-- ==============================================================================
-- Migration: Fix Site Requests Geometry Columns
-- Description: Ensures all coordinate and polyline columns exist for map visualization.
-- ==============================================================================

-- 1. Ajout des colonnes de coordonnées (si manquantes)
ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS origin_lat double precision,
ADD COLUMN IF NOT EXISTS origin_lng double precision,
ADD COLUMN IF NOT EXISTS destination_lat double precision,
ADD COLUMN IF NOT EXISTS destination_lng double precision;

-- 2. Ajout de la colonne polyline (si manquante)
ALTER TABLE public.site_trip_requests 
ADD COLUMN IF NOT EXISTS polyline text;

-- 3. Notification pour rafraîchir le cache du schéma Supabase (PostgREST)
-- Cela permet à l'API de voir les nouvelles colonnes immédiatement.
NOTIFY pgrst, 'reload schema';

-- Commentaire de succès
DO $$ 
BEGIN 
    RAISE NOTICE 'Schéma mis à jour avec succès pour site_trip_requests';
END $$;
