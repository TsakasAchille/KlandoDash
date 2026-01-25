

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."annotation_tag_entity" (
    "id" character varying(16) NOT NULL,
    "name" character varying(24) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."annotation_tag_entity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."auth_identity" (
    "userId" "uuid",
    "providerId" character varying(64) NOT NULL,
    "providerType" character varying(32) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."auth_identity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."auth_provider_sync_history" (
    "id" integer NOT NULL,
    "providerType" character varying(32) NOT NULL,
    "runMode" "text" NOT NULL,
    "status" "text" NOT NULL,
    "startedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "endedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "scanned" integer NOT NULL,
    "created" integer NOT NULL,
    "updated" integer NOT NULL,
    "disabled" integer NOT NULL,
    "error" "text"
);


ALTER TABLE "public"."auth_provider_sync_history" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."auth_provider_sync_history_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."auth_provider_sync_history_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."auth_provider_sync_history_id_seq" OWNED BY "public"."auth_provider_sync_history"."id";



CREATE TABLE IF NOT EXISTS "public"."bookings" (
    "id" "text" NOT NULL,
    "seats" integer NOT NULL,
    "user_id" "text" NOT NULL,
    "trip_id" "text" NOT NULL,
    "status" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."bookings" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."chats" (
    "id" character varying NOT NULL,
    "trip_id" character varying,
    "sender_id" character varying,
    "message" character varying,
    "timestamp" timestamp without time zone,
    "updated_at" timestamp without time zone
);


ALTER TABLE "public"."chats" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."conversation_memory" (
    "id" integer NOT NULL,
    "user_id" integer,
    "session_id" "uuid" NOT NULL,
    "question" "text" NOT NULL,
    "sql_query" "text",
    "response" "text",
    "context" "jsonb",
    "metadata" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "relevance_score" double precision,
    "is_favorite" boolean DEFAULT false
);


ALTER TABLE "public"."conversation_memory" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."conversation_memory_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."conversation_memory_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."conversation_memory_id_seq" OWNED BY "public"."conversation_memory"."id";



CREATE TABLE IF NOT EXISTS "public"."credentials_entity" (
    "name" character varying(128) NOT NULL,
    "data" "text" NOT NULL,
    "type" character varying(128) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "id" character varying(36) NOT NULL,
    "isManaged" boolean DEFAULT false NOT NULL
);


ALTER TABLE "public"."credentials_entity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."dash_authorized_users" (
    "email" character varying(255) NOT NULL,
    "active" boolean DEFAULT true NOT NULL,
    "role" character varying(50) DEFAULT 'user'::character varying NOT NULL,
    "added_at" timestamp without time zone DEFAULT "now"(),
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "added_by" character varying(255),
    "notes" "text"
);


ALTER TABLE "public"."dash_authorized_users" OWNER TO "postgres";


COMMENT ON TABLE "public"."dash_authorized_users" IS 'Table des utilisateurs autorisés à accéder à KlandoDash';



COMMENT ON COLUMN "public"."dash_authorized_users"."email" IS 'Adresse email de l''utilisateur (clé primaire)';



COMMENT ON COLUMN "public"."dash_authorized_users"."active" IS 'Indique si l''utilisateur est actuellement autorisé à se connecter';



COMMENT ON COLUMN "public"."dash_authorized_users"."role" IS 'Rôle de l''utilisateur (admin, user, etc.)';



COMMENT ON COLUMN "public"."dash_authorized_users"."added_at" IS 'Date d''ajout de l''utilisateur';



COMMENT ON COLUMN "public"."dash_authorized_users"."updated_at" IS 'Date de dernière mise à jour';



COMMENT ON COLUMN "public"."dash_authorized_users"."added_by" IS 'Email de l''administrateur qui a ajouté cet utilisateur';



COMMENT ON COLUMN "public"."dash_authorized_users"."notes" IS 'Notes ou commentaires sur cet utilisateur';



CREATE TABLE IF NOT EXISTS "public"."event_destinations" (
    "id" "uuid" NOT NULL,
    "destination" "jsonb" NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."event_destinations" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."execution_annotation_tags" (
    "annotationId" integer NOT NULL,
    "tagId" character varying(24) NOT NULL
);


ALTER TABLE "public"."execution_annotation_tags" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."execution_annotations" (
    "id" integer NOT NULL,
    "executionId" integer NOT NULL,
    "vote" character varying(6),
    "note" "text",
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."execution_annotations" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."execution_annotations_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."execution_annotations_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."execution_annotations_id_seq" OWNED BY "public"."execution_annotations"."id";



CREATE TABLE IF NOT EXISTS "public"."execution_data" (
    "executionId" integer NOT NULL,
    "workflowData" "json" NOT NULL,
    "data" "text" NOT NULL
);


ALTER TABLE "public"."execution_data" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."execution_entity" (
    "id" integer NOT NULL,
    "finished" boolean NOT NULL,
    "mode" character varying NOT NULL,
    "retryOf" character varying,
    "retrySuccessId" character varying,
    "startedAt" timestamp(3) with time zone,
    "stoppedAt" timestamp(3) with time zone,
    "waitTill" timestamp(3) with time zone,
    "status" character varying NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    "deletedAt" timestamp(3) with time zone,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."execution_entity" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."execution_entity_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."execution_entity_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."execution_entity_id_seq" OWNED BY "public"."execution_entity"."id";



CREATE TABLE IF NOT EXISTS "public"."execution_metadata" (
    "id" integer NOT NULL,
    "executionId" integer NOT NULL,
    "key" character varying(255) NOT NULL,
    "value" "text" NOT NULL
);


ALTER TABLE "public"."execution_metadata" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."execution_metadata_temp_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."execution_metadata_temp_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."execution_metadata_temp_id_seq" OWNED BY "public"."execution_metadata"."id";



CREATE TABLE IF NOT EXISTS "public"."folder" (
    "id" character varying(36) NOT NULL,
    "name" character varying(128) NOT NULL,
    "parentFolderId" character varying(36),
    "projectId" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."folder" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."folder_tag" (
    "folderId" character varying(36) NOT NULL,
    "tagId" character varying(36) NOT NULL
);


ALTER TABLE "public"."folder_tag" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."insights_by_period" (
    "id" integer NOT NULL,
    "metaId" integer NOT NULL,
    "type" integer NOT NULL,
    "value" integer NOT NULL,
    "periodUnit" integer NOT NULL,
    "periodStart" timestamp(0) with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE "public"."insights_by_period" OWNER TO "postgres";


COMMENT ON COLUMN "public"."insights_by_period"."type" IS '0: time_saved_minutes, 1: runtime_milliseconds, 2: success, 3: failure';



COMMENT ON COLUMN "public"."insights_by_period"."periodUnit" IS '0: hour, 1: day, 2: week';



ALTER TABLE "public"."insights_by_period" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."insights_by_period_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."insights_metadata" (
    "metaId" integer NOT NULL,
    "workflowId" character varying(16),
    "projectId" character varying(36),
    "workflowName" character varying(128) NOT NULL,
    "projectName" character varying(255) NOT NULL
);


ALTER TABLE "public"."insights_metadata" OWNER TO "postgres";


ALTER TABLE "public"."insights_metadata" ALTER COLUMN "metaId" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."insights_metadata_metaId_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."insights_raw" (
    "id" integer NOT NULL,
    "metaId" integer NOT NULL,
    "type" integer NOT NULL,
    "value" integer NOT NULL,
    "timestamp" timestamp(0) with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE "public"."insights_raw" OWNER TO "postgres";


COMMENT ON COLUMN "public"."insights_raw"."type" IS '0: time_saved_minutes, 1: runtime_milliseconds, 2: success, 3: failure';



ALTER TABLE "public"."insights_raw" ALTER COLUMN "id" ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME "public"."insights_raw_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);



CREATE TABLE IF NOT EXISTS "public"."installed_nodes" (
    "name" character varying(200) NOT NULL,
    "type" character varying(200) NOT NULL,
    "latestVersion" integer DEFAULT 1 NOT NULL,
    "package" character varying(241) NOT NULL
);


ALTER TABLE "public"."installed_nodes" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."installed_packages" (
    "packageName" character varying(214) NOT NULL,
    "installedVersion" character varying(50) NOT NULL,
    "authorName" character varying(70),
    "authorEmail" character varying(70),
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."installed_packages" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."invalid_auth_token" (
    "token" character varying(512) NOT NULL,
    "expiresAt" timestamp(3) with time zone NOT NULL
);


ALTER TABLE "public"."invalid_auth_token" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."migrations" (
    "id" integer NOT NULL,
    "timestamp" bigint NOT NULL,
    "name" character varying NOT NULL
);


ALTER TABLE "public"."migrations" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."migrations_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."migrations_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."migrations_id_seq" OWNED BY "public"."migrations"."id";



CREATE TABLE IF NOT EXISTS "public"."n8n_chat_histories" (
    "id" integer NOT NULL,
    "session_id" character varying(255) NOT NULL,
    "message" "jsonb" NOT NULL
);


ALTER TABLE "public"."n8n_chat_histories" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."n8n_chat_histories_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."n8n_chat_histories_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."n8n_chat_histories_id_seq" OWNED BY "public"."n8n_chat_histories"."id";



CREATE TABLE IF NOT EXISTS "public"."processed_data" (
    "workflowId" character varying(36) NOT NULL,
    "context" character varying(255) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "value" "text" NOT NULL
);


ALTER TABLE "public"."processed_data" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."project" (
    "id" character varying(36) NOT NULL,
    "name" character varying(255) NOT NULL,
    "type" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "icon" "json"
);


ALTER TABLE "public"."project" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."project_relation" (
    "projectId" character varying(36) NOT NULL,
    "userId" "uuid" NOT NULL,
    "role" character varying NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."project_relation" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."role" (
    "id" integer NOT NULL,
    "name" character varying(32) NOT NULL,
    "scope" character varying(255) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."role" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."role_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."role_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."role_id_seq" OWNED BY "public"."role"."id";



CREATE TABLE IF NOT EXISTS "public"."settings" (
    "key" character varying(255) NOT NULL,
    "value" "text" NOT NULL,
    "loadOnStartup" boolean DEFAULT false NOT NULL
);


ALTER TABLE "public"."settings" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."shared_credentials" (
    "credentialsId" character varying(36) NOT NULL,
    "projectId" character varying(36) NOT NULL,
    "role" "text" NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."shared_credentials" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."shared_workflow" (
    "workflowId" character varying(36) NOT NULL,
    "projectId" character varying(36) NOT NULL,
    "role" "text" NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."shared_workflow" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."support_comments" (
    "comment_id" "uuid" NOT NULL,
    "ticket_id" "uuid" NOT NULL,
    "user_id" "text" NOT NULL,
    "comment_text" "text" NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"(),
    "comment_sent" "text",
    "comment_received" "text",
    "comment_type" "text",
    "comment_source" "text"
);


ALTER TABLE "public"."support_comments" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."support_tickets" (
    "user_id" "text" NOT NULL,
    "subject" "text",
    "message" "text" NOT NULL,
    "status" "text" DEFAULT 'open'::"text",
    "created_at" timestamp without time zone DEFAULT "now"(),
    "updated_at" timestamp without time zone DEFAULT "now"(),
    "contact_preference" "text" DEFAULT 'aucun'::"text",
    "phone" "text",
    "mail" "text",
    "ticket_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    CONSTRAINT "support_tickets_contact_preference_check" CHECK (("contact_preference" = ANY (ARRAY['mail'::"text", 'phone'::"text", 'aucun'::"text"])))
);


ALTER TABLE "public"."support_tickets" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."tag_entity" (
    "name" character varying(24) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "id" character varying(36) NOT NULL
);


ALTER TABLE "public"."tag_entity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."test_case_execution" (
    "id" character varying(36) NOT NULL,
    "testRunId" character varying(36) NOT NULL,
    "pastExecutionId" integer,
    "executionId" integer,
    "evaluationExecutionId" integer,
    "status" character varying NOT NULL,
    "runAt" timestamp(3) with time zone,
    "completedAt" timestamp(3) with time zone,
    "errorCode" character varying,
    "errorDetails" "json",
    "metrics" "json",
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."test_case_execution" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."test_definition" (
    "name" character varying(255) NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    "evaluationWorkflowId" character varying(36),
    "annotationTagId" character varying(16),
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "description" "text",
    "id" character varying(36) NOT NULL,
    "mockedNodes" "json" DEFAULT '[]'::"json" NOT NULL
);


ALTER TABLE "public"."test_definition" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."test_metric" (
    "id" character varying(36) NOT NULL,
    "name" character varying(255) NOT NULL,
    "testDefinitionId" character varying(36) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."test_metric" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."test_run" (
    "id" character varying(36) NOT NULL,
    "testDefinitionId" character varying(36) NOT NULL,
    "status" character varying NOT NULL,
    "runAt" timestamp(3) with time zone,
    "completedAt" timestamp(3) with time zone,
    "metrics" "json",
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "totalCases" integer,
    "passedCases" integer,
    "failedCases" integer,
    "errorCode" character varying(255),
    "errorDetails" "text",
    CONSTRAINT "test_run_check" CHECK (
CASE
    WHEN (("status")::"text" = 'new'::"text") THEN ("totalCases" IS NULL)
    WHEN (("status")::"text" = ANY ((ARRAY['cancelled'::character varying, 'error'::character varying])::"text"[])) THEN (("totalCases" IS NULL) OR ("totalCases" >= 0))
    ELSE ("totalCases" >= 0)
END),
    CONSTRAINT "test_run_check1" CHECK (
CASE
    WHEN (("status")::"text" = 'new'::"text") THEN ("passedCases" IS NULL)
    WHEN (("status")::"text" = ANY ((ARRAY['cancelled'::character varying, 'error'::character varying])::"text"[])) THEN (("passedCases" IS NULL) OR ("passedCases" >= 0))
    ELSE ("passedCases" >= 0)
END),
    CONSTRAINT "test_run_check2" CHECK (
CASE
    WHEN (("status")::"text" = 'new'::"text") THEN ("failedCases" IS NULL)
    WHEN (("status")::"text" = ANY ((ARRAY['cancelled'::character varying, 'error'::character varying])::"text"[])) THEN (("failedCases" IS NULL) OR ("failedCases" >= 0))
    ELSE ("failedCases" >= 0)
END)
);


ALTER TABLE "public"."test_run" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ticket_references" (
    "reference_token" character varying(20) NOT NULL,
    "ticket_id" character varying(36) NOT NULL,
    "created_at" timestamp without time zone NOT NULL,
    "expires_at" timestamp without time zone
);


ALTER TABLE "public"."ticket_references" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."transactions" (
    "id" "text" NOT NULL,
    "user_id" "text" NOT NULL,
    "external_id" "text",
    "msg" "text",
    "amount" integer,
    "status" "text",
    "phone" "text",
    "service_code" "text",
    "sender" "text",
    "created_at" timestamp without time zone,
    "updated_at" timestamp without time zone,
    "error_message" "text",
    "has_transactions" boolean,
    "metadata" "jsonb"
);


ALTER TABLE "public"."transactions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."trip_embeddings" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "trip_id" "text",
    "content" "text",
    "embedding" "public"."vector"(1536),
    "created_at" timestamp without time zone DEFAULT "now"()
);


ALTER TABLE "public"."trip_embeddings" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."trips" (
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "departure_date" timestamp with time zone,
    "departure_name" "text",
    "departure_schedule" timestamp with time zone,
    "destination_name" "text",
    "seats_available" bigint,
    "passenger_price" bigint,
    "distance" double precision,
    "precision" "text",
    "polyline" "text",
    "trip_id" "text" NOT NULL,
    "driver_id" "text",
    "departure_latitude" double precision,
    "departure_longitude" double precision,
    "destination_latitude" double precision,
    "destination_longitude" double precision,
    "updated_at" timestamp with time zone,
    "seats_booked" bigint,
    "seats_published" bigint,
    "driver_price" bigint,
    "status" "text",
    "departure_description" "text",
    "destination_description" "text",
    "auto_confirmation" boolean
);


ALTER TABLE "public"."trips" OWNER TO "postgres";


COMMENT ON COLUMN "public"."trips"."destination_name" IS 'Nom formaté du lieu de départ, nom GPS complet fourni par la map';



COMMENT ON COLUMN "public"."trips"."seats_available" IS 'Nombre de places encore disponibles';



COMMENT ON COLUMN "public"."trips"."updated_at" IS 'Date de dernière mise à jour de l’entrée';



COMMENT ON COLUMN "public"."trips"."seats_booked" IS 'Nombre de places réservées';



COMMENT ON COLUMN "public"."trips"."seats_published" IS 'Nombre de places mises en ligne.';



COMMENT ON COLUMN "public"."trips"."driver_price" IS 'Prix fixé par le conducteur pour le trajet -> somme réel que le driver va recevoir';



COMMENT ON COLUMN "public"."trips"."status" IS 'Statut actuel du trajet (ex. “PENDING”).';



COMMENT ON COLUMN "public"."trips"."departure_description" IS 'Description textuelle fourni par le conducteur de la zone de depart.';



CREATE TABLE IF NOT EXISTS "public"."user" (
    "id" "uuid" DEFAULT "uuid_in"((OVERLAY(OVERLAY("md5"(((("random"())::"text" || ':'::"text") || ("clock_timestamp"())::"text")) PLACING '4'::"text" FROM 13) PLACING "to_hex"(("floor"((("random"() * (((11 - 8) + 1))::double precision) + (8)::double precision)))::integer) FROM 17))::"cstring") NOT NULL,
    "email" character varying(255),
    "firstName" character varying(32),
    "lastName" character varying(32),
    "password" character varying(255),
    "personalizationAnswers" "json",
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "settings" "json",
    "disabled" boolean DEFAULT false NOT NULL,
    "mfaEnabled" boolean DEFAULT false NOT NULL,
    "mfaSecret" "text",
    "mfaRecoveryCodes" "text",
    "role" "text" NOT NULL
);


ALTER TABLE "public"."user" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."user_api_keys" (
    "id" character varying(36) NOT NULL,
    "userId" "uuid" NOT NULL,
    "label" character varying(100) NOT NULL,
    "apiKey" character varying NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL
);


ALTER TABLE "public"."user_api_keys" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."users" (
    "uid" "text" NOT NULL,
    "display_name" "text",
    "email" "text",
    "first_name" "text",
    "name" "text",
    "phone_number" "text",
    "birth" "date",
    "photo_url" "text",
    "bio" "text",
    "driver_license_url" "text",
    "gender" "text",
    "id_card_url" "text",
    "rating" numeric(3,2),
    "rating_count" integer,
    "role" "text",
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "created_at" timestamp with time zone DEFAULT "now"(),
    "is_driver_doc_validated" boolean DEFAULT false
);


ALTER TABLE "public"."users" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."variables" (
    "key" character varying(50) NOT NULL,
    "type" character varying(50) DEFAULT 'string'::character varying NOT NULL,
    "value" character varying(255),
    "id" character varying(36) NOT NULL
);


ALTER TABLE "public"."variables" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."webhook_entity" (
    "webhookPath" character varying NOT NULL,
    "method" character varying NOT NULL,
    "node" character varying NOT NULL,
    "webhookId" character varying,
    "pathLength" integer,
    "workflowId" character varying(36) NOT NULL
);


ALTER TABLE "public"."webhook_entity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."workflow_entity" (
    "name" character varying(128) NOT NULL,
    "active" boolean NOT NULL,
    "nodes" "json" NOT NULL,
    "connections" "json" NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "settings" "json",
    "staticData" "json",
    "pinData" "json",
    "versionId" character(36),
    "triggerCount" integer DEFAULT 0 NOT NULL,
    "id" character varying(36) NOT NULL,
    "meta" "json",
    "parentFolderId" character varying(36) DEFAULT NULL::character varying
);


ALTER TABLE "public"."workflow_entity" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."workflow_history" (
    "versionId" character varying(36) NOT NULL,
    "workflowId" character varying(36) NOT NULL,
    "authors" character varying(255) NOT NULL,
    "createdAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "updatedAt" timestamp(3) with time zone DEFAULT CURRENT_TIMESTAMP(3) NOT NULL,
    "nodes" "json" NOT NULL,
    "connections" "json" NOT NULL
);


ALTER TABLE "public"."workflow_history" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."workflow_statistics" (
    "count" integer DEFAULT 0,
    "latestEvent" timestamp(3) with time zone,
    "name" character varying(128) NOT NULL,
    "workflowId" character varying(36) NOT NULL
);


ALTER TABLE "public"."workflow_statistics" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."workflows_tags" (
    "workflowId" character varying(36) NOT NULL,
    "tagId" character varying(36) NOT NULL
);


ALTER TABLE "public"."workflows_tags" OWNER TO "postgres";


ALTER TABLE ONLY "public"."auth_provider_sync_history" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."auth_provider_sync_history_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."conversation_memory" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."conversation_memory_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."execution_annotations" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."execution_annotations_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."execution_entity" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."execution_entity_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."execution_metadata" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."execution_metadata_temp_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."migrations" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."migrations_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."n8n_chat_histories" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."n8n_chat_histories_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."role" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."role_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."test_run"
    ADD CONSTRAINT "PK_011c050f566e9db509a0fadb9b9" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."installed_packages"
    ADD CONSTRAINT "PK_08cc9197c39b028c1e9beca225940576fd1a5804" PRIMARY KEY ("packageName");



ALTER TABLE ONLY "public"."execution_metadata"
    ADD CONSTRAINT "PK_17a0b6284f8d626aae88e1c16e4" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."project_relation"
    ADD CONSTRAINT "PK_1caaa312a5d7184a003be0f0cb6" PRIMARY KEY ("projectId", "userId");



ALTER TABLE ONLY "public"."folder_tag"
    ADD CONSTRAINT "PK_27e4e00852f6b06a925a4d83a3e" PRIMARY KEY ("folderId", "tagId");



ALTER TABLE ONLY "public"."test_metric"
    ADD CONSTRAINT "PK_3e98b8e20acc19c5030a8644142" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."project"
    ADD CONSTRAINT "PK_4d68b1358bb5b766d3e78f32f57" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."invalid_auth_token"
    ADD CONSTRAINT "PK_5779069b7235b256d91f7af1a15" PRIMARY KEY ("token");



ALTER TABLE ONLY "public"."shared_workflow"
    ADD CONSTRAINT "PK_5ba87620386b847201c9531c58f" PRIMARY KEY ("workflowId", "projectId");



ALTER TABLE ONLY "public"."folder"
    ADD CONSTRAINT "PK_6278a41a706740c94c02e288df8" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."annotation_tag_entity"
    ADD CONSTRAINT "PK_69dfa041592c30bbc0d4b84aa00" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."execution_annotations"
    ADD CONSTRAINT "PK_7afcf93ffa20c4252869a7c6a23" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."migrations"
    ADD CONSTRAINT "PK_8c82d7f526340ab734260ea46be" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."installed_nodes"
    ADD CONSTRAINT "PK_8ebd28194e4f792f96b5933423fc439df97d9689" PRIMARY KEY ("name");



ALTER TABLE ONLY "public"."shared_credentials"
    ADD CONSTRAINT "PK_8ef3a59796a228913f251779cff" PRIMARY KEY ("credentialsId", "projectId");



ALTER TABLE ONLY "public"."test_case_execution"
    ADD CONSTRAINT "PK_90c121f77a78a6580e94b794bce" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_api_keys"
    ADD CONSTRAINT "PK_978fa5caa3468f463dac9d92e69" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."execution_annotation_tags"
    ADD CONSTRAINT "PK_979ec03d31294cca484be65d11f" PRIMARY KEY ("annotationId", "tagId");



ALTER TABLE ONLY "public"."webhook_entity"
    ADD CONSTRAINT "PK_b21ace2e13596ccd87dc9bf4ea6" PRIMARY KEY ("webhookPath", "method");



ALTER TABLE ONLY "public"."insights_by_period"
    ADD CONSTRAINT "PK_b606942249b90cc39b0265f0575" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."workflow_history"
    ADD CONSTRAINT "PK_b6572dd6173e4cd06fe79937b58" PRIMARY KEY ("versionId");



ALTER TABLE ONLY "public"."processed_data"
    ADD CONSTRAINT "PK_ca04b9d8dc72de268fe07a65773" PRIMARY KEY ("workflowId", "context");



ALTER TABLE ONLY "public"."settings"
    ADD CONSTRAINT "PK_dc0fe14e6d9943f268e7b119f69ab8bd" PRIMARY KEY ("key");



ALTER TABLE ONLY "public"."role"
    ADD CONSTRAINT "PK_e853ce24e8200abe5721d2c6ac552b73" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user"
    ADD CONSTRAINT "PK_ea8f538c94b6e352418254ed6474a81f" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."insights_raw"
    ADD CONSTRAINT "PK_ec15125755151e3a7e00e00014f" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."insights_metadata"
    ADD CONSTRAINT "PK_f448a94c35218b6208ce20cf5a1" PRIMARY KEY ("metaId");



ALTER TABLE ONLY "public"."role"
    ADD CONSTRAINT "UQ_5b49d0f504f7ef31045a1fb2eb8" UNIQUE ("scope", "name");



ALTER TABLE ONLY "public"."user"
    ADD CONSTRAINT "UQ_e12875dfb3b1d92d7d7c5377e2" UNIQUE ("email");



ALTER TABLE ONLY "public"."auth_identity"
    ADD CONSTRAINT "auth_identity_pkey" PRIMARY KEY ("providerId", "providerType");



ALTER TABLE ONLY "public"."auth_provider_sync_history"
    ADD CONSTRAINT "auth_provider_sync_history_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."bookings"
    ADD CONSTRAINT "bookings_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."chats"
    ADD CONSTRAINT "chats_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."conversation_memory"
    ADD CONSTRAINT "conversation_memory_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."credentials_entity"
    ADD CONSTRAINT "credentials_entity_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."dash_authorized_users"
    ADD CONSTRAINT "dash_authorized_users_pkey" PRIMARY KEY ("email");



ALTER TABLE ONLY "public"."event_destinations"
    ADD CONSTRAINT "event_destinations_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."execution_data"
    ADD CONSTRAINT "execution_data_pkey" PRIMARY KEY ("executionId");



ALTER TABLE ONLY "public"."n8n_chat_histories"
    ADD CONSTRAINT "n8n_chat_histories_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."execution_entity"
    ADD CONSTRAINT "pk_e3e63bbf986767844bbe1166d4e" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."workflow_statistics"
    ADD CONSTRAINT "pk_workflow_statistics" PRIMARY KEY ("workflowId", "name");



ALTER TABLE ONLY "public"."workflows_tags"
    ADD CONSTRAINT "pk_workflows_tags" PRIMARY KEY ("workflowId", "tagId");



ALTER TABLE ONLY "public"."support_comments"
    ADD CONSTRAINT "support_comments_pkey" PRIMARY KEY ("comment_id");



ALTER TABLE ONLY "public"."support_tickets"
    ADD CONSTRAINT "support_tickets_pkey" PRIMARY KEY ("ticket_id");



ALTER TABLE ONLY "public"."tag_entity"
    ADD CONSTRAINT "tag_entity_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."test_definition"
    ADD CONSTRAINT "test_definition_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."ticket_references"
    ADD CONSTRAINT "ticket_references_pkey" PRIMARY KEY ("reference_token");



ALTER TABLE ONLY "public"."ticket_references"
    ADD CONSTRAINT "ticket_references_ticket_id_key" UNIQUE ("ticket_id");



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "transactions_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."trip_embeddings"
    ADD CONSTRAINT "trip_embeddings_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."trips"
    ADD CONSTRAINT "trips_pkey" PRIMARY KEY ("trip_id");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("uid");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_uid_unique" UNIQUE ("uid");



ALTER TABLE ONLY "public"."variables"
    ADD CONSTRAINT "variables_key_key" UNIQUE ("key");



ALTER TABLE ONLY "public"."variables"
    ADD CONSTRAINT "variables_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."workflow_entity"
    ADD CONSTRAINT "workflow_entity_pkey" PRIMARY KEY ("id");



CREATE UNIQUE INDEX "IDX_14f68deffaf858465715995508" ON "public"."folder" USING "btree" ("projectId", "id");



CREATE UNIQUE INDEX "IDX_1d8ab99d5861c9388d2dc1cf73" ON "public"."insights_metadata" USING "btree" ("workflowId");



CREATE INDEX "IDX_1e31657f5fe46816c34be7c1b4" ON "public"."workflow_history" USING "btree" ("workflowId");



CREATE UNIQUE INDEX "IDX_1ef35bac35d20bdae979d917a3" ON "public"."user_api_keys" USING "btree" ("apiKey");



CREATE INDEX "IDX_3a4e9cf37111ac3270e2469b47" ON "public"."test_metric" USING "btree" ("testDefinitionId");



CREATE INDEX "IDX_3a81713a76f2295b12b46cdfca" ON "public"."test_run" USING "btree" ("testDefinitionId");



CREATE INDEX "IDX_5f0643f6717905a05164090dde" ON "public"."project_relation" USING "btree" ("userId");



CREATE UNIQUE INDEX "IDX_60b6a84299eeb3f671dfec7693" ON "public"."insights_by_period" USING "btree" ("periodStart", "type", "periodUnit", "metaId");



CREATE INDEX "IDX_61448d56d61802b5dfde5cdb00" ON "public"."project_relation" USING "btree" ("projectId");



CREATE UNIQUE INDEX "IDX_63d7bbae72c767cf162d459fcc" ON "public"."user_api_keys" USING "btree" ("userId", "label");



CREATE INDEX "IDX_8e4b4774db42f1e6dda3452b2a" ON "public"."test_case_execution" USING "btree" ("testRunId");



CREATE UNIQUE INDEX "IDX_97f863fa83c4786f1956508496" ON "public"."execution_annotations" USING "btree" ("executionId");



CREATE INDEX "IDX_9ec1ce6fbf82305f489adb971d" ON "public"."test_definition" USING "btree" ("evaluationWorkflowId");



CREATE INDEX "IDX_a3697779b366e131b2bbdae297" ON "public"."execution_annotation_tags" USING "btree" ("tagId");



CREATE UNIQUE INDEX "IDX_ae51b54c4bb430cf92f48b623f" ON "public"."annotation_tag_entity" USING "btree" ("name");



CREATE INDEX "IDX_b0dd0087fe3da02b0ffa4b9c5b" ON "public"."test_definition" USING "btree" ("workflowId");



CREATE INDEX "IDX_c1519757391996eb06064f0e7c" ON "public"."execution_annotation_tags" USING "btree" ("annotationId");



CREATE UNIQUE INDEX "IDX_cec8eea3bf49551482ccb4933e" ON "public"."execution_metadata" USING "btree" ("executionId", "key");



CREATE INDEX "IDX_execution_entity_deletedAt" ON "public"."execution_entity" USING "btree" ("deletedAt");



CREATE INDEX "IDX_workflow_entity_name" ON "public"."workflow_entity" USING "btree" ("name");



CREATE INDEX "idx_07fde106c0b471d8cc80a64fc8" ON "public"."credentials_entity" USING "btree" ("type");



CREATE INDEX "idx_16f4436789e804e3e1c9eeb240" ON "public"."webhook_entity" USING "btree" ("webhookId", "method", "pathLength");



CREATE UNIQUE INDEX "idx_812eb05f7451ca757fb98444ce" ON "public"."tag_entity" USING "btree" ("name");



CREATE INDEX "idx_dash_authorized_users_email" ON "public"."dash_authorized_users" USING "btree" ("email");



CREATE INDEX "idx_execution_entity_stopped_at_status_deleted_at" ON "public"."execution_entity" USING "btree" ("stoppedAt", "status", "deletedAt") WHERE (("stoppedAt" IS NOT NULL) AND ("deletedAt" IS NULL));



CREATE INDEX "idx_execution_entity_wait_till_status_deleted_at" ON "public"."execution_entity" USING "btree" ("waitTill", "status", "deletedAt") WHERE (("waitTill" IS NOT NULL) AND ("deletedAt" IS NULL));



CREATE INDEX "idx_execution_entity_workflow_id_started_at" ON "public"."execution_entity" USING "btree" ("workflowId", "startedAt") WHERE (("startedAt" IS NOT NULL) AND ("deletedAt" IS NULL));



CREATE INDEX "idx_support_comments_received" ON "public"."support_comments" USING "btree" ("comment_received");



CREATE INDEX "idx_support_comments_sent" ON "public"."support_comments" USING "btree" ("comment_sent");



CREATE INDEX "idx_support_comments_ticket_id" ON "public"."support_comments" USING "btree" ("ticket_id");



CREATE INDEX "idx_ticket_references_ticket_id" ON "public"."ticket_references" USING "btree" ("ticket_id");



CREATE INDEX "idx_ticket_references_token" ON "public"."ticket_references" USING "btree" ("reference_token");



CREATE INDEX "idx_workflows_tags_workflow_id" ON "public"."workflows_tags" USING "btree" ("workflowId");



CREATE UNIQUE INDEX "pk_credentials_entity_id" ON "public"."credentials_entity" USING "btree" ("id");



CREATE UNIQUE INDEX "pk_tag_entity_id" ON "public"."tag_entity" USING "btree" ("id");



CREATE UNIQUE INDEX "pk_test_definition_id" ON "public"."test_definition" USING "btree" ("id");



CREATE UNIQUE INDEX "pk_variables_id" ON "public"."variables" USING "btree" ("id");



CREATE UNIQUE INDEX "pk_workflow_entity_id" ON "public"."workflow_entity" USING "btree" ("id");



CREATE INDEX "trip_embeddings_embedding_idx" ON "public"."trip_embeddings" USING "ivfflat" ("embedding" "public"."vector_cosine_ops") WITH ("lists"='100');



CREATE OR REPLACE TRIGGER "webhook-support-tickets" AFTER INSERT ON "public"."support_tickets" FOR EACH ROW EXECUTE FUNCTION "supabase_functions"."http_request"('https://klando.app.n8n.cloud/webhook/a427c889-e960-4304-ac2e-e149bffcdf2f', 'POST', '{"Content-type":"application/json"}', '{}', '5000');



ALTER TABLE ONLY "public"."processed_data"
    ADD CONSTRAINT "FK_06a69a7032c97a763c2c7599464" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."insights_metadata"
    ADD CONSTRAINT "FK_1d8ab99d5861c9388d2dc1cf733" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."workflow_history"
    ADD CONSTRAINT "FK_1e31657f5fe46816c34be7c1b4b" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."insights_metadata"
    ADD CONSTRAINT "FK_2375a1eda085adb16b24615b69c" FOREIGN KEY ("projectId") REFERENCES "public"."project"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."test_case_execution"
    ADD CONSTRAINT "FK_258d954733841d51edd826a562b" FOREIGN KEY ("pastExecutionId") REFERENCES "public"."execution_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."execution_metadata"
    ADD CONSTRAINT "FK_31d0b4c93fb85ced26f6005cda3" FOREIGN KEY ("executionId") REFERENCES "public"."execution_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_metric"
    ADD CONSTRAINT "FK_3a4e9cf37111ac3270e2469b475" FOREIGN KEY ("testDefinitionId") REFERENCES "public"."test_definition"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_run"
    ADD CONSTRAINT "FK_3a81713a76f2295b12b46cdfcab" FOREIGN KEY ("testDefinitionId") REFERENCES "public"."test_definition"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."shared_credentials"
    ADD CONSTRAINT "FK_416f66fc846c7c442970c094ccf" FOREIGN KEY ("credentialsId") REFERENCES "public"."credentials_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."project_relation"
    ADD CONSTRAINT "FK_5f0643f6717905a05164090dde7" FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."project_relation"
    ADD CONSTRAINT "FK_61448d56d61802b5dfde5cdb002" FOREIGN KEY ("projectId") REFERENCES "public"."project"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."insights_by_period"
    ADD CONSTRAINT "FK_6414cfed98daabbfdd61a1cfbc0" FOREIGN KEY ("metaId") REFERENCES "public"."insights_metadata"("metaId") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."insights_raw"
    ADD CONSTRAINT "FK_6e2e33741adef2a7c5d66befa4e" FOREIGN KEY ("metaId") REFERENCES "public"."insights_metadata"("metaId") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."installed_nodes"
    ADD CONSTRAINT "FK_73f857fc5dce682cef8a99c11dbddbc969618951" FOREIGN KEY ("package") REFERENCES "public"."installed_packages"("packageName") ON UPDATE CASCADE ON DELETE CASCADE;



ALTER TABLE ONLY "public"."folder"
    ADD CONSTRAINT "FK_804ea52f6729e3940498bd54d78" FOREIGN KEY ("parentFolderId") REFERENCES "public"."folder"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."shared_credentials"
    ADD CONSTRAINT "FK_812c2852270da1247756e77f5a4" FOREIGN KEY ("projectId") REFERENCES "public"."project"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_case_execution"
    ADD CONSTRAINT "FK_8e4b4774db42f1e6dda3452b2af" FOREIGN KEY ("testRunId") REFERENCES "public"."test_run"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."folder_tag"
    ADD CONSTRAINT "FK_94a60854e06f2897b2e0d39edba" FOREIGN KEY ("folderId") REFERENCES "public"."folder"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."execution_annotations"
    ADD CONSTRAINT "FK_97f863fa83c4786f19565084960" FOREIGN KEY ("executionId") REFERENCES "public"."execution_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_definition"
    ADD CONSTRAINT "FK_9ec1ce6fbf82305f489adb971d3" FOREIGN KEY ("evaluationWorkflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."execution_annotation_tags"
    ADD CONSTRAINT "FK_a3697779b366e131b2bbdae2976" FOREIGN KEY ("tagId") REFERENCES "public"."annotation_tag_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."shared_workflow"
    ADD CONSTRAINT "FK_a45ea5f27bcfdc21af9b4188560" FOREIGN KEY ("projectId") REFERENCES "public"."project"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."folder"
    ADD CONSTRAINT "FK_a8260b0b36939c6247f385b8221" FOREIGN KEY ("projectId") REFERENCES "public"."project"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_definition"
    ADD CONSTRAINT "FK_b0dd0087fe3da02b0ffa4b9c5bb" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."execution_annotation_tags"
    ADD CONSTRAINT "FK_c1519757391996eb06064f0e7c8" FOREIGN KEY ("annotationId") REFERENCES "public"."execution_annotations"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_definition"
    ADD CONSTRAINT "FK_d5d7ea64662dbc62f5e266fbeb0" FOREIGN KEY ("annotationTagId") REFERENCES "public"."annotation_tag_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."shared_workflow"
    ADD CONSTRAINT "FK_daa206a04983d47d0a9c34649ce" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."folder_tag"
    ADD CONSTRAINT "FK_dc88164176283de80af47621746" FOREIGN KEY ("tagId") REFERENCES "public"."tag_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_case_execution"
    ADD CONSTRAINT "FK_dfbe194e3ebdfe49a87bc4692ca" FOREIGN KEY ("evaluationExecutionId") REFERENCES "public"."execution_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."user_api_keys"
    ADD CONSTRAINT "FK_e131705cbbc8fb589889b02d457" FOREIGN KEY ("userId") REFERENCES "public"."user"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."test_case_execution"
    ADD CONSTRAINT "FK_e48965fac35d0f5b9e7f51d8c44" FOREIGN KEY ("executionId") REFERENCES "public"."execution_entity"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."auth_identity"
    ADD CONSTRAINT "auth_identity_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."user"("id");



ALTER TABLE ONLY "public"."bookings"
    ADD CONSTRAINT "bookings_trip_id_fkey" FOREIGN KEY ("trip_id") REFERENCES "public"."trips"("trip_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."bookings"
    ADD CONSTRAINT "bookings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("uid") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."execution_data"
    ADD CONSTRAINT "execution_data_fk" FOREIGN KEY ("executionId") REFERENCES "public"."execution_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."trips"
    ADD CONSTRAINT "fk_driver" FOREIGN KEY ("driver_id") REFERENCES "public"."users"("uid") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."execution_entity"
    ADD CONSTRAINT "fk_execution_entity_workflow_id" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."transactions"
    ADD CONSTRAINT "fk_transactions_user" FOREIGN KEY ("user_id") REFERENCES "public"."users"("uid") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."webhook_entity"
    ADD CONSTRAINT "fk_webhook_entity_workflow_id" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."workflow_entity"
    ADD CONSTRAINT "fk_workflow_parent_folder" FOREIGN KEY ("parentFolderId") REFERENCES "public"."folder"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."workflow_statistics"
    ADD CONSTRAINT "fk_workflow_statistics_workflow_id" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."workflows_tags"
    ADD CONSTRAINT "fk_workflows_tags_tag_id" FOREIGN KEY ("tagId") REFERENCES "public"."tag_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."workflows_tags"
    ADD CONSTRAINT "fk_workflows_tags_workflow_id" FOREIGN KEY ("workflowId") REFERENCES "public"."workflow_entity"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."support_comments"
    ADD CONSTRAINT "support_comments_ticket_id_fkey" FOREIGN KEY ("ticket_id") REFERENCES "public"."support_tickets"("ticket_id");



ALTER TABLE ONLY "public"."support_tickets"
    ADD CONSTRAINT "support_tickets_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("uid") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."trip_embeddings"
    ADD CONSTRAINT "trip_embeddings_trip_id_fkey" FOREIGN KEY ("trip_id") REFERENCES "public"."trips"("trip_id") ON DELETE CASCADE;



GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON TABLE "public"."annotation_tag_entity" TO "anon";
GRANT ALL ON TABLE "public"."annotation_tag_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."annotation_tag_entity" TO "service_role";



GRANT ALL ON TABLE "public"."auth_identity" TO "anon";
GRANT ALL ON TABLE "public"."auth_identity" TO "authenticated";
GRANT ALL ON TABLE "public"."auth_identity" TO "service_role";



GRANT ALL ON TABLE "public"."auth_provider_sync_history" TO "anon";
GRANT ALL ON TABLE "public"."auth_provider_sync_history" TO "authenticated";
GRANT ALL ON TABLE "public"."auth_provider_sync_history" TO "service_role";



GRANT ALL ON SEQUENCE "public"."auth_provider_sync_history_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."auth_provider_sync_history_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."auth_provider_sync_history_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."bookings" TO "anon";
GRANT ALL ON TABLE "public"."bookings" TO "authenticated";
GRANT ALL ON TABLE "public"."bookings" TO "service_role";



GRANT ALL ON TABLE "public"."chats" TO "anon";
GRANT ALL ON TABLE "public"."chats" TO "authenticated";
GRANT ALL ON TABLE "public"."chats" TO "service_role";



GRANT ALL ON TABLE "public"."conversation_memory" TO "anon";
GRANT ALL ON TABLE "public"."conversation_memory" TO "authenticated";
GRANT ALL ON TABLE "public"."conversation_memory" TO "service_role";



GRANT ALL ON SEQUENCE "public"."conversation_memory_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."conversation_memory_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."conversation_memory_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."credentials_entity" TO "anon";
GRANT ALL ON TABLE "public"."credentials_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."credentials_entity" TO "service_role";



GRANT ALL ON TABLE "public"."dash_authorized_users" TO "anon";
GRANT ALL ON TABLE "public"."dash_authorized_users" TO "authenticated";
GRANT ALL ON TABLE "public"."dash_authorized_users" TO "service_role";



GRANT ALL ON TABLE "public"."event_destinations" TO "anon";
GRANT ALL ON TABLE "public"."event_destinations" TO "authenticated";
GRANT ALL ON TABLE "public"."event_destinations" TO "service_role";



GRANT ALL ON TABLE "public"."execution_annotation_tags" TO "anon";
GRANT ALL ON TABLE "public"."execution_annotation_tags" TO "authenticated";
GRANT ALL ON TABLE "public"."execution_annotation_tags" TO "service_role";



GRANT ALL ON TABLE "public"."execution_annotations" TO "anon";
GRANT ALL ON TABLE "public"."execution_annotations" TO "authenticated";
GRANT ALL ON TABLE "public"."execution_annotations" TO "service_role";



GRANT ALL ON SEQUENCE "public"."execution_annotations_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."execution_annotations_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."execution_annotations_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."execution_data" TO "anon";
GRANT ALL ON TABLE "public"."execution_data" TO "authenticated";
GRANT ALL ON TABLE "public"."execution_data" TO "service_role";



GRANT ALL ON TABLE "public"."execution_entity" TO "anon";
GRANT ALL ON TABLE "public"."execution_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."execution_entity" TO "service_role";



GRANT ALL ON SEQUENCE "public"."execution_entity_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."execution_entity_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."execution_entity_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."execution_metadata" TO "anon";
GRANT ALL ON TABLE "public"."execution_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."execution_metadata" TO "service_role";



GRANT ALL ON SEQUENCE "public"."execution_metadata_temp_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."execution_metadata_temp_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."execution_metadata_temp_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."folder" TO "anon";
GRANT ALL ON TABLE "public"."folder" TO "authenticated";
GRANT ALL ON TABLE "public"."folder" TO "service_role";



GRANT ALL ON TABLE "public"."folder_tag" TO "anon";
GRANT ALL ON TABLE "public"."folder_tag" TO "authenticated";
GRANT ALL ON TABLE "public"."folder_tag" TO "service_role";



GRANT ALL ON TABLE "public"."insights_by_period" TO "anon";
GRANT ALL ON TABLE "public"."insights_by_period" TO "authenticated";
GRANT ALL ON TABLE "public"."insights_by_period" TO "service_role";



GRANT ALL ON SEQUENCE "public"."insights_by_period_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."insights_by_period_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."insights_by_period_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."insights_metadata" TO "anon";
GRANT ALL ON TABLE "public"."insights_metadata" TO "authenticated";
GRANT ALL ON TABLE "public"."insights_metadata" TO "service_role";



GRANT ALL ON SEQUENCE "public"."insights_metadata_metaId_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."insights_metadata_metaId_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."insights_metadata_metaId_seq" TO "service_role";



GRANT ALL ON TABLE "public"."insights_raw" TO "anon";
GRANT ALL ON TABLE "public"."insights_raw" TO "authenticated";
GRANT ALL ON TABLE "public"."insights_raw" TO "service_role";



GRANT ALL ON SEQUENCE "public"."insights_raw_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."insights_raw_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."insights_raw_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."installed_nodes" TO "anon";
GRANT ALL ON TABLE "public"."installed_nodes" TO "authenticated";
GRANT ALL ON TABLE "public"."installed_nodes" TO "service_role";



GRANT ALL ON TABLE "public"."installed_packages" TO "anon";
GRANT ALL ON TABLE "public"."installed_packages" TO "authenticated";
GRANT ALL ON TABLE "public"."installed_packages" TO "service_role";



GRANT ALL ON TABLE "public"."invalid_auth_token" TO "anon";
GRANT ALL ON TABLE "public"."invalid_auth_token" TO "authenticated";
GRANT ALL ON TABLE "public"."invalid_auth_token" TO "service_role";



GRANT ALL ON TABLE "public"."migrations" TO "anon";
GRANT ALL ON TABLE "public"."migrations" TO "authenticated";
GRANT ALL ON TABLE "public"."migrations" TO "service_role";



GRANT ALL ON SEQUENCE "public"."migrations_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."migrations_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."migrations_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."n8n_chat_histories" TO "anon";
GRANT ALL ON TABLE "public"."n8n_chat_histories" TO "authenticated";
GRANT ALL ON TABLE "public"."n8n_chat_histories" TO "service_role";



GRANT ALL ON SEQUENCE "public"."n8n_chat_histories_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."n8n_chat_histories_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."n8n_chat_histories_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."processed_data" TO "anon";
GRANT ALL ON TABLE "public"."processed_data" TO "authenticated";
GRANT ALL ON TABLE "public"."processed_data" TO "service_role";



GRANT ALL ON TABLE "public"."project" TO "anon";
GRANT ALL ON TABLE "public"."project" TO "authenticated";
GRANT ALL ON TABLE "public"."project" TO "service_role";



GRANT ALL ON TABLE "public"."project_relation" TO "anon";
GRANT ALL ON TABLE "public"."project_relation" TO "authenticated";
GRANT ALL ON TABLE "public"."project_relation" TO "service_role";



GRANT ALL ON TABLE "public"."role" TO "anon";
GRANT ALL ON TABLE "public"."role" TO "authenticated";
GRANT ALL ON TABLE "public"."role" TO "service_role";



GRANT ALL ON SEQUENCE "public"."role_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."role_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."role_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."settings" TO "anon";
GRANT ALL ON TABLE "public"."settings" TO "authenticated";
GRANT ALL ON TABLE "public"."settings" TO "service_role";



GRANT ALL ON TABLE "public"."shared_credentials" TO "anon";
GRANT ALL ON TABLE "public"."shared_credentials" TO "authenticated";
GRANT ALL ON TABLE "public"."shared_credentials" TO "service_role";



GRANT ALL ON TABLE "public"."shared_workflow" TO "anon";
GRANT ALL ON TABLE "public"."shared_workflow" TO "authenticated";
GRANT ALL ON TABLE "public"."shared_workflow" TO "service_role";



GRANT ALL ON TABLE "public"."support_comments" TO "anon";
GRANT ALL ON TABLE "public"."support_comments" TO "authenticated";
GRANT ALL ON TABLE "public"."support_comments" TO "service_role";



GRANT ALL ON TABLE "public"."support_tickets" TO "anon";
GRANT ALL ON TABLE "public"."support_tickets" TO "authenticated";
GRANT ALL ON TABLE "public"."support_tickets" TO "service_role";



GRANT ALL ON TABLE "public"."tag_entity" TO "anon";
GRANT ALL ON TABLE "public"."tag_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."tag_entity" TO "service_role";



GRANT ALL ON TABLE "public"."test_case_execution" TO "anon";
GRANT ALL ON TABLE "public"."test_case_execution" TO "authenticated";
GRANT ALL ON TABLE "public"."test_case_execution" TO "service_role";



GRANT ALL ON TABLE "public"."test_definition" TO "anon";
GRANT ALL ON TABLE "public"."test_definition" TO "authenticated";
GRANT ALL ON TABLE "public"."test_definition" TO "service_role";



GRANT ALL ON TABLE "public"."test_metric" TO "anon";
GRANT ALL ON TABLE "public"."test_metric" TO "authenticated";
GRANT ALL ON TABLE "public"."test_metric" TO "service_role";



GRANT ALL ON TABLE "public"."test_run" TO "anon";
GRANT ALL ON TABLE "public"."test_run" TO "authenticated";
GRANT ALL ON TABLE "public"."test_run" TO "service_role";



GRANT ALL ON TABLE "public"."ticket_references" TO "anon";
GRANT ALL ON TABLE "public"."ticket_references" TO "authenticated";
GRANT ALL ON TABLE "public"."ticket_references" TO "service_role";



GRANT ALL ON TABLE "public"."transactions" TO "anon";
GRANT ALL ON TABLE "public"."transactions" TO "authenticated";
GRANT ALL ON TABLE "public"."transactions" TO "service_role";



GRANT ALL ON TABLE "public"."trip_embeddings" TO "anon";
GRANT ALL ON TABLE "public"."trip_embeddings" TO "authenticated";
GRANT ALL ON TABLE "public"."trip_embeddings" TO "service_role";



GRANT ALL ON TABLE "public"."trips" TO "anon";
GRANT ALL ON TABLE "public"."trips" TO "authenticated";
GRANT ALL ON TABLE "public"."trips" TO "service_role";



GRANT ALL ON TABLE "public"."user" TO "anon";
GRANT ALL ON TABLE "public"."user" TO "authenticated";
GRANT ALL ON TABLE "public"."user" TO "service_role";



GRANT ALL ON TABLE "public"."user_api_keys" TO "anon";
GRANT ALL ON TABLE "public"."user_api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."user_api_keys" TO "service_role";



GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";



GRANT ALL ON TABLE "public"."variables" TO "anon";
GRANT ALL ON TABLE "public"."variables" TO "authenticated";
GRANT ALL ON TABLE "public"."variables" TO "service_role";



GRANT ALL ON TABLE "public"."webhook_entity" TO "anon";
GRANT ALL ON TABLE "public"."webhook_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."webhook_entity" TO "service_role";



GRANT ALL ON TABLE "public"."workflow_entity" TO "anon";
GRANT ALL ON TABLE "public"."workflow_entity" TO "authenticated";
GRANT ALL ON TABLE "public"."workflow_entity" TO "service_role";



GRANT ALL ON TABLE "public"."workflow_history" TO "anon";
GRANT ALL ON TABLE "public"."workflow_history" TO "authenticated";
GRANT ALL ON TABLE "public"."workflow_history" TO "service_role";



GRANT ALL ON TABLE "public"."workflow_statistics" TO "anon";
GRANT ALL ON TABLE "public"."workflow_statistics" TO "authenticated";
GRANT ALL ON TABLE "public"."workflow_statistics" TO "service_role";



GRANT ALL ON TABLE "public"."workflows_tags" TO "anon";
GRANT ALL ON TABLE "public"."workflows_tags" TO "authenticated";
GRANT ALL ON TABLE "public"."workflows_tags" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";






