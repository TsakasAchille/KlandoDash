-- Migration 008: Correction des alertes de sécurité du Linter Supabase
-- Résout: function_search_path_mutable et extension_in_public

-- 1. Sécurisation des extensions (Move from public to extensions schema)
CREATE SCHEMA IF NOT EXISTS extensions;

-- Déplacer l'extension vector si elle est dans public
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
    ALTER EXTENSION vector SET SCHEMA extensions;
  END IF;
END $$;

-- Déplacer l'extension http si elle est dans public
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'http') THEN
    ALTER EXTENSION http SET SCHEMA extensions;
  END IF;
END $$;

-- 2. Sécurisation des fonctions RPC (Fix search_path)
-- On rajoute 'SET search_path = public' à chaque fonction

ALTER FUNCTION public.get_tickets_with_user(text, int, int) 
SET search_path = public;

ALTER FUNCTION public.get_ticket_detail(uuid) 
SET search_path = public;

ALTER FUNCTION public.update_ticket_status(uuid, text) 
SET search_path = public;

ALTER FUNCTION public.add_support_comment(uuid, text, text, text) 
SET search_path = public;

-- Note: Les autres alertes (MFA, Leaked Passwords, Postgres version)
-- doivent être corrigées manuellement via l'interface utilisateur de Supabase
-- car elles concernent la configuration de la plateforme et non le SQL.
