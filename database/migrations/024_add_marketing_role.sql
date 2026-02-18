-- Migration: Add 'marketing' role to dash_authorized_users
-- Description: Updates the check constraint to allow the new 'marketing' role.

ALTER TABLE public.dash_authorized_users DROP CONSTRAINT IF EXISTS dash_authorized_users_role_check;

ALTER TABLE public.dash_authorized_users 
ADD CONSTRAINT dash_authorized_users_role_check 
CHECK (role IN ('admin', 'support', 'marketing'));

-- Note: 'admin' sees everything.
-- 'support' sees tickets, chats, and users.
-- 'marketing' will see the new Marketing module (Prospects + AI Strategy).
