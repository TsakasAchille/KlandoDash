-- Migration 007: Sécurisation globale (Correction des erreurs du Linter Supabase)
-- Cette migration active la Row Level Security (RLS) sur toutes les tables exposées.
-- Par défaut, cela bloque tout accès via l'API publique (anon), 
-- mais laisse l'accès total au Dashboard Admin (service_role).

-- 1. Tables principales de KlandoDash
ALTER TABLE IF EXISTS "public"."trips" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."bookings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."support_tickets" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."support_comments" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."dash_authorized_users" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."ticket_references" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."trip_embeddings" ENABLE ROW LEVEL SECURITY;

-- 2. Tables Techniques et n8n (on les verrouille pour éviter les fuites de données)
ALTER TABLE IF EXISTS "public"."test_metric" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."workflow_history" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."test_definition" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."test_case_execution" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."test_run" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."folder" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."folder_tag" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."insights_metadata" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."insights_raw" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."insights_by_period" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."workflow_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."n8n_chat_histories" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."conversation_memory" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."auth_provider_sync_history" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."migrations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."project" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."webhook_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."execution_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."project_relation" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."shared_credentials" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."workflows_tags" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."credentials_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."tag_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."shared_workflow" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."execution_metadata" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."invalid_auth_token" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."execution_annotations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."execution_annotation_tags" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."annotation_tag_entity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."chats" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."installed_packages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."role" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."user_api_keys" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."settings" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."installed_nodes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."processed_data" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."auth_identity" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."event_destinations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."variables" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."execution_data" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS "public"."workflow_statistics" ENABLE ROW LEVEL SECURITY;

-- Note: Aucune politique (POLICY) n'est créée ici pour les tables n8n.
-- Cela signifie qu'elles sont désormais totalement privées et inaccessibles via l'API anon.
