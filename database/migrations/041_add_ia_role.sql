-- Migration: Add 'ia' role to dash_authorized_users
-- Description: Updates the check constraint to allow the new 'ia' role for automated data ingestion.

ALTER TABLE public.dash_authorized_users DROP CONSTRAINT IF EXISTS dash_authorized_users_role_check;

ALTER TABLE public.dash_authorized_users 
ADD CONSTRAINT dash_authorized_users_role_check 
CHECK (role IN ('admin', 'support', 'marketing', 'ia', 'user'));

-- Description of roles:
-- 'admin' : Accès total.
-- 'support' : Gestion tickets et utilisateurs.
-- 'marketing' : Stratégie et Editorial.
-- 'ia' : Accès restreint au Hub de Données (IA Data Hub).
-- 'user' : Accès de base lecture seule.
