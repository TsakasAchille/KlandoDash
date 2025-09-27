-- Ajouter un nouveau passager au trip TRIP-1758214129289639-SoMfalwk5yRq7GqCXJZjSkogDJr1
-- User ID: bk17O0BBAndQR7xxSZxDvAGkSWU2

INSERT INTO "public"."bookings" (
    "id", 
    "seats", 
    "user_id", 
    "trip_id", 
    "status", 
    "created_at", 
    "updated_at"
) VALUES (
    gen_random_uuid(),  -- Génère automatiquement un UUID unique
    1,                  -- 1 place réservée
    'bk17O0BBAndQR7xxSZxDvAGkSWU2',  -- User ID du nouveau passager
    'TRIP-1758214129289639-SoMfalwk5yRq7GqCXJZjSkogDJr1',  -- Trip ID
    'CONFIRMED',        -- Statut confirmé (au lieu d'ARCHIVED)
    NOW(),              -- Date de création actuelle
    NOW()               -- Date de mise à jour actuelle
);

-- Vérifier que l'insertion a fonctionné
SELECT 
    b.id,
    b.seats,
    b.user_id,
    b.trip_id,
    b.status,
    b.created_at,
    u.display_name,
    u.email
FROM bookings b
LEFT JOIN users u ON b.user_id = u.uid
WHERE b.trip_id = 'TRIP-1758214129289639-SoMfalwk5yRq7GqCXJZjSkogDJr1'
ORDER BY b.created_at DESC;
