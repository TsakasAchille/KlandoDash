
-- Script de migration pour corriger les données users
-- Généré automatiquement par analyze_users_data.py

-- Correction des valeurs GENDER
UPDATE users SET gender = 'MALE' WHERE gender = 'MAN';
UPDATE users SET gender = 'FEMALE' WHERE gender = 'WOMAN';
UPDATE users SET gender = 'NOT_SPECIFIED' WHERE gender IS NULL OR gender = '';

-- Correction des valeurs ROLE (normalisation en majuscules)
UPDATE users SET role = 'USER' WHERE LOWER(role) = 'user';
UPDATE users SET role = 'DRIVER' WHERE LOWER(role) = 'driver';
UPDATE users SET role = 'ADMIN' WHERE LOWER(role) = 'admin';
UPDATE users SET role = 'MODERATOR' WHERE LOWER(role) = 'moderator';
UPDATE users SET role = 'USER' WHERE role IS NULL OR role = '';

-- Vérification post-migration
SELECT 
    gender, COUNT(*) as count 
FROM users 
GROUP BY gender 
ORDER BY count DESC;

SELECT 
    role, COUNT(*) as count 
FROM users 
GROUP BY role 
ORDER BY count DESC;
