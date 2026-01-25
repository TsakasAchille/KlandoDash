-- Migration: Support Technique - Index et Fonctions RPC
-- Date: 2025-01-25
-- Description: Ajoute les contraintes, index et fonctions pour la page Support

-- ============================================
-- 1. CONTRAINTES CHECK
-- ============================================

-- Status des tickets (OPEN, CLOSED, PENDING)
ALTER TABLE support_tickets
ADD CONSTRAINT support_ticket_status_check
CHECK (status IN ('OPEN', 'CLOSED', 'PENDING'));

-- Preference de contact (mail, phone, aucun)
ALTER TABLE support_tickets
ADD CONSTRAINT support_ticket_contact_pref_check
CHECK (contact_preference IN ('mail', 'phone', 'aucun'));

-- ============================================
-- 2. INDEX
-- ============================================

-- Filtrer par status
CREATE INDEX IF NOT EXISTS idx_support_tickets_status
ON support_tickets(status);

-- Trier par date de creation DESC
CREATE INDEX IF NOT EXISTS idx_support_tickets_created_at
ON support_tickets(created_at DESC);

-- Rechercher par utilisateur
CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id
ON support_tickets(user_id);

-- Combine: status + date (listing principal)
CREATE INDEX IF NOT EXISTS idx_support_tickets_status_created
ON support_tickets(status, created_at DESC);

-- ============================================
-- 3. FONCTIONS RPC
-- ============================================

-- 3.1 Liste des tickets avec infos utilisateur
CREATE OR REPLACE FUNCTION get_tickets_with_user(
  p_status text DEFAULT NULL,
  p_limit int DEFAULT 50,
  p_offset int DEFAULT 0
)
RETURNS TABLE (
  ticket_id uuid,
  subject text,
  message text,
  status text,
  contact_preference text,
  created_at timestamp,
  updated_at timestamp,
  user_uid text,
  user_display_name text,
  user_phone text,
  user_email text,
  comment_count bigint
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.ticket_id,
    t.subject,
    t.message,
    t.status,
    t.contact_preference,
    t.created_at,
    t.updated_at,
    u.uid,
    u.display_name,
    COALESCE(t.phone, u.phone_number) as user_phone,
    COALESCE(t.mail, u.email) as user_email,
    COUNT(c.comment_id) as comment_count
  FROM support_tickets t
  LEFT JOIN users u ON t.user_id = u.uid
  LEFT JOIN support_comments c ON t.ticket_id = c.ticket_id
  WHERE (p_status IS NULL OR t.status = p_status)
  GROUP BY t.ticket_id, u.uid, u.display_name, u.phone_number, u.email
  ORDER BY t.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 3.2 Detail d'un ticket avec commentaires
CREATE OR REPLACE FUNCTION get_ticket_detail(p_ticket_id uuid)
RETURNS TABLE (
  ticket_id uuid,
  subject text,
  message text,
  status text,
  contact_preference text,
  phone text,
  mail text,
  created_at timestamp,
  updated_at timestamp,
  user_uid text,
  user_display_name text,
  user_avatar_url text,
  comments jsonb
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.ticket_id,
    t.subject,
    t.message,
    t.status,
    t.contact_preference,
    t.phone,
    t.mail,
    t.created_at,
    t.updated_at,
    u.uid,
    u.display_name,
    u.photo_url,
    COALESCE(
      jsonb_agg(
        jsonb_build_object(
          'comment_id', c.comment_id,
          'comment_text', c.comment_text,
          'created_at', c.created_at,
          'comment_source', c.comment_source,
          'user_id', c.user_id
        ) ORDER BY c.created_at ASC
      ) FILTER (WHERE c.comment_id IS NOT NULL),
      '[]'::jsonb
    ) as comments
  FROM support_tickets t
  LEFT JOIN users u ON t.user_id = u.uid
  LEFT JOIN support_comments c ON t.ticket_id = c.ticket_id
  WHERE t.ticket_id = p_ticket_id
  GROUP BY t.ticket_id, u.uid, u.display_name, u.photo_url;
END;
$$ LANGUAGE plpgsql;

-- 3.3 Mettre a jour le status d'un ticket
CREATE OR REPLACE FUNCTION update_ticket_status(
  p_ticket_id uuid,
  p_status text
)
RETURNS void AS $$
BEGIN
  -- Validation du status
  IF p_status NOT IN ('OPEN', 'CLOSED', 'PENDING') THEN
    RAISE EXCEPTION 'Status invalide: %. Valeurs autorisees: OPEN, CLOSED, PENDING', p_status;
  END IF;

  UPDATE support_tickets
  SET
    status = p_status,
    updated_at = now()
  WHERE ticket_id = p_ticket_id;

  -- Verifier que le ticket existe
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Ticket non trouve: %', p_ticket_id;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- 3.4 Ajouter un commentaire
CREATE OR REPLACE FUNCTION add_support_comment(
  p_ticket_id uuid,
  p_user_id text,
  p_comment_text text,
  p_comment_source text DEFAULT 'admin'
)
RETURNS uuid AS $$
DECLARE
  new_comment_id uuid;
BEGIN
  -- Validation du commentaire
  IF length(trim(p_comment_text)) < 10 THEN
    RAISE EXCEPTION 'Le commentaire doit faire au moins 10 caracteres';
  END IF;

  -- Verifier que le ticket existe
  IF NOT EXISTS (SELECT 1 FROM support_tickets WHERE ticket_id = p_ticket_id) THEN
    RAISE EXCEPTION 'Ticket non trouve: %', p_ticket_id;
  END IF;

  -- Inserer le commentaire
  INSERT INTO support_comments (
    comment_id,
    ticket_id,
    user_id,
    comment_text,
    comment_source,
    created_at
  ) VALUES (
    gen_random_uuid(),
    p_ticket_id,
    p_user_id,
    trim(p_comment_text),
    p_comment_source,
    now()
  )
  RETURNING comment_id INTO new_comment_id;

  -- Mettre a jour updated_at du ticket
  UPDATE support_tickets
  SET updated_at = now()
  WHERE ticket_id = p_ticket_id;

  RETURN new_comment_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4. GRANTS (pour service_role)
-- ============================================

GRANT EXECUTE ON FUNCTION get_tickets_with_user TO service_role;
GRANT EXECUTE ON FUNCTION get_ticket_detail TO service_role;
GRANT EXECUTE ON FUNCTION update_ticket_status TO service_role;
GRANT EXECUTE ON FUNCTION add_support_comment TO service_role;

-- ============================================
-- FIN DE LA MIGRATION
-- ============================================
