-- This migration officially documents the addition of the 'support' role 
-- to the set of possible roles in the dash_authorized_users table.
COMMENT ON COLUMN public.dash_authorized_users.role IS 'Rôle de l''utilisateur (admin, user, support)';
