-- Migration: Indexes et RLS pour la table transactions
-- Date: 2026-01-27

-- ============================================
-- INDEXES
-- ============================================

-- Recherche par utilisateur
CREATE INDEX IF NOT EXISTS idx_transactions_user_id
  ON transactions (user_id);

-- Filtre par statut
CREATE INDEX IF NOT EXISTS idx_transactions_status
  ON transactions (status);

-- Tri par date de création DESC
CREATE INDEX IF NOT EXISTS idx_transactions_created_at
  ON transactions (created_at DESC);

-- Filtre par type
CREATE INDEX IF NOT EXISTS idx_transactions_type
  ON transactions (type);

-- Combiné : utilisateur + date (historique d'un utilisateur)
CREATE INDEX IF NOT EXISTS idx_transactions_user_created
  ON transactions (user_id, created_at DESC);

-- Combiné : statut + date (transactions récentes par statut)
CREATE INDEX IF NOT EXISTS idx_transactions_status_created
  ON transactions (status, created_at DESC);

-- ============================================
-- RLS (Row Level Security)
-- ============================================

-- Activer RLS
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Le dashboard utilise service_role (bypass RLS),
-- mais on ajoute des policies pour les accès via anon/authenticated key

-- Les utilisateurs authentifiés peuvent voir leurs propres transactions
CREATE POLICY "Users can view own transactions"
  ON transactions
  FOR SELECT
  USING (auth.uid()::text = user_id);

-- Seul le service_role peut insérer/modifier (pas de policy INSERT/UPDATE pour authenticated)
-- Le dashboard admin utilise service_role qui bypass RLS automatiquement
