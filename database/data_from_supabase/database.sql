-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.annotation_tag_entity (
  id character varying NOT NULL,
  name character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT annotation_tag_entity_pkey PRIMARY KEY (id)
);
CREATE TABLE public.auth_identity (
  userId uuid,
  providerId character varying NOT NULL,
  providerType character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT auth_identity_pkey PRIMARY KEY (providerId, providerType),
  CONSTRAINT auth_identity_userId_fkey FOREIGN KEY (userId) REFERENCES public.user(id)
);
CREATE TABLE public.auth_provider_sync_history (
  id integer NOT NULL DEFAULT nextval('auth_provider_sync_history_id_seq'::regclass),
  providerType character varying NOT NULL,
  runMode text NOT NULL,
  status text NOT NULL,
  startedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  endedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  scanned integer NOT NULL,
  created integer NOT NULL,
  updated integer NOT NULL,
  disabled integer NOT NULL,
  error text,
  CONSTRAINT auth_provider_sync_history_pkey PRIMARY KEY (id)
);
CREATE TABLE public.bookings (
  id text NOT NULL,
  seats integer NOT NULL,
  user_id text NOT NULL,
  trip_id text NOT NULL,
  status text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT bookings_pkey PRIMARY KEY (id),
  CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uid),
  CONSTRAINT bookings_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trips(trip_id)
);
CREATE TABLE public.chats (
  id character varying NOT NULL,
  trip_id character varying,
  sender_id character varying,
  message character varying,
  timestamp timestamp without time zone,
  updated_at timestamp without time zone,
  CONSTRAINT chats_pkey PRIMARY KEY (id)
);
CREATE TABLE public.conversation_memory (
  id integer NOT NULL DEFAULT nextval('conversation_memory_id_seq'::regclass),
  user_id integer,
  session_id uuid NOT NULL,
  question text NOT NULL,
  sql_query text,
  response text,
  context jsonb,
  metadata jsonb,
  created_at timestamp with time zone DEFAULT now(),
  relevance_score double precision,
  is_favorite boolean DEFAULT false,
  CONSTRAINT conversation_memory_pkey PRIMARY KEY (id)
);
CREATE TABLE public.credentials_entity (
  name character varying NOT NULL,
  data text NOT NULL,
  type character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  id character varying NOT NULL,
  isManaged boolean NOT NULL DEFAULT false,
  CONSTRAINT credentials_entity_pkey PRIMARY KEY (id)
);
CREATE TABLE public.dash_authorized_users (
  email character varying NOT NULL,
  active boolean NOT NULL DEFAULT true,
  role character varying NOT NULL DEFAULT 'user'::character varying,
  added_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  added_by character varying,
  notes text,
  CONSTRAINT dash_authorized_users_pkey PRIMARY KEY (email)
);
CREATE TABLE public.event_destinations (
  id uuid NOT NULL,
  destination jsonb NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT event_destinations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.execution_annotation_tags (
  annotationId integer NOT NULL,
  tagId character varying NOT NULL,
  CONSTRAINT execution_annotation_tags_pkey PRIMARY KEY (annotationId, tagId),
  CONSTRAINT FK_c1519757391996eb06064f0e7c8 FOREIGN KEY (annotationId) REFERENCES public.execution_annotations(id),
  CONSTRAINT FK_a3697779b366e131b2bbdae2976 FOREIGN KEY (tagId) REFERENCES public.annotation_tag_entity(id)
);
CREATE TABLE public.execution_annotations (
  id integer NOT NULL DEFAULT nextval('execution_annotations_id_seq'::regclass),
  executionId integer NOT NULL,
  vote character varying,
  note text,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT execution_annotations_pkey PRIMARY KEY (id),
  CONSTRAINT FK_97f863fa83c4786f19565084960 FOREIGN KEY (executionId) REFERENCES public.execution_entity(id)
);
CREATE TABLE public.execution_data (
  executionId integer NOT NULL,
  workflowData json NOT NULL,
  data text NOT NULL,
  CONSTRAINT execution_data_pkey PRIMARY KEY (executionId),
  CONSTRAINT execution_data_fk FOREIGN KEY (executionId) REFERENCES public.execution_entity(id)
);
CREATE TABLE public.execution_entity (
  id integer NOT NULL DEFAULT nextval('execution_entity_id_seq'::regclass),
  finished boolean NOT NULL,
  mode character varying NOT NULL,
  retryOf character varying,
  retrySuccessId character varying,
  startedAt timestamp with time zone,
  stoppedAt timestamp with time zone,
  waitTill timestamp with time zone,
  status character varying NOT NULL,
  workflowId character varying NOT NULL,
  deletedAt timestamp with time zone,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT execution_entity_pkey PRIMARY KEY (id),
  CONSTRAINT fk_execution_entity_workflow_id FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id)
);
CREATE TABLE public.execution_metadata (
  id integer NOT NULL DEFAULT nextval('execution_metadata_temp_id_seq'::regclass),
  executionId integer NOT NULL,
  key character varying NOT NULL,
  value text NOT NULL,
  CONSTRAINT execution_metadata_pkey PRIMARY KEY (id),
  CONSTRAINT FK_31d0b4c93fb85ced26f6005cda3 FOREIGN KEY (executionId) REFERENCES public.execution_entity(id)
);
CREATE TABLE public.folder (
  id character varying NOT NULL,
  name character varying NOT NULL,
  parentFolderId character varying,
  projectId character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT folder_pkey PRIMARY KEY (id),
  CONSTRAINT FK_a8260b0b36939c6247f385b8221 FOREIGN KEY (projectId) REFERENCES public.project(id),
  CONSTRAINT FK_804ea52f6729e3940498bd54d78 FOREIGN KEY (parentFolderId) REFERENCES public.folder(id)
);
CREATE TABLE public.folder_tag (
  folderId character varying NOT NULL,
  tagId character varying NOT NULL,
  CONSTRAINT folder_tag_pkey PRIMARY KEY (folderId, tagId),
  CONSTRAINT FK_94a60854e06f2897b2e0d39edba FOREIGN KEY (folderId) REFERENCES public.folder(id),
  CONSTRAINT FK_dc88164176283de80af47621746 FOREIGN KEY (tagId) REFERENCES public.tag_entity(id)
);
CREATE TABLE public.insights_by_period (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  metaId integer NOT NULL,
  type integer NOT NULL,
  value integer NOT NULL,
  periodUnit integer NOT NULL,
  periodStart timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT insights_by_period_pkey PRIMARY KEY (id),
  CONSTRAINT FK_6414cfed98daabbfdd61a1cfbc0 FOREIGN KEY (metaId) REFERENCES public.insights_metadata(metaId)
);
CREATE TABLE public.insights_metadata (
  metaId integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  workflowId character varying,
  projectId character varying,
  workflowName character varying NOT NULL,
  projectName character varying NOT NULL,
  CONSTRAINT insights_metadata_pkey PRIMARY KEY (metaId),
  CONSTRAINT FK_1d8ab99d5861c9388d2dc1cf733 FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id),
  CONSTRAINT FK_2375a1eda085adb16b24615b69c FOREIGN KEY (projectId) REFERENCES public.project(id)
);
CREATE TABLE public.insights_raw (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  metaId integer NOT NULL,
  type integer NOT NULL,
  value integer NOT NULL,
  timestamp timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT insights_raw_pkey PRIMARY KEY (id),
  CONSTRAINT FK_6e2e33741adef2a7c5d66befa4e FOREIGN KEY (metaId) REFERENCES public.insights_metadata(metaId)
);
CREATE TABLE public.installed_nodes (
  name character varying NOT NULL,
  type character varying NOT NULL,
  latestVersion integer NOT NULL DEFAULT 1,
  package character varying NOT NULL,
  CONSTRAINT installed_nodes_pkey PRIMARY KEY (name),
  CONSTRAINT FK_73f857fc5dce682cef8a99c11dbddbc969618951 FOREIGN KEY (package) REFERENCES public.installed_packages(packageName)
);
CREATE TABLE public.installed_packages (
  packageName character varying NOT NULL,
  installedVersion character varying NOT NULL,
  authorName character varying,
  authorEmail character varying,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT installed_packages_pkey PRIMARY KEY (packageName)
);
CREATE TABLE public.invalid_auth_token (
  token character varying NOT NULL,
  expiresAt timestamp with time zone NOT NULL,
  CONSTRAINT invalid_auth_token_pkey PRIMARY KEY (token)
);
CREATE TABLE public.migrations (
  id integer NOT NULL DEFAULT nextval('migrations_id_seq'::regclass),
  timestamp bigint NOT NULL,
  name character varying NOT NULL,
  CONSTRAINT migrations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.n8n_chat_histories (
  id integer NOT NULL DEFAULT nextval('n8n_chat_histories_id_seq'::regclass),
  session_id character varying NOT NULL,
  message jsonb NOT NULL,
  CONSTRAINT n8n_chat_histories_pkey PRIMARY KEY (id)
);
CREATE TABLE public.processed_data (
  workflowId character varying NOT NULL,
  context character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  value text NOT NULL,
  CONSTRAINT processed_data_pkey PRIMARY KEY (workflowId, context),
  CONSTRAINT FK_06a69a7032c97a763c2c7599464 FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id)
);
CREATE TABLE public.project (
  id character varying NOT NULL,
  name character varying NOT NULL,
  type character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  icon json,
  CONSTRAINT project_pkey PRIMARY KEY (id)
);
CREATE TABLE public.project_relation (
  projectId character varying NOT NULL,
  userId uuid NOT NULL,
  role character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT project_relation_pkey PRIMARY KEY (projectId, userId),
  CONSTRAINT FK_61448d56d61802b5dfde5cdb002 FOREIGN KEY (projectId) REFERENCES public.project(id),
  CONSTRAINT FK_5f0643f6717905a05164090dde7 FOREIGN KEY (userId) REFERENCES public.user(id)
);
CREATE TABLE public.role (
  id integer NOT NULL DEFAULT nextval('role_id_seq'::regclass),
  name character varying NOT NULL,
  scope character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT role_pkey PRIMARY KEY (id)
);
CREATE TABLE public.settings (
  key character varying NOT NULL,
  value text NOT NULL,
  loadOnStartup boolean NOT NULL DEFAULT false,
  CONSTRAINT settings_pkey PRIMARY KEY (key)
);
CREATE TABLE public.shared_credentials (
  credentialsId character varying NOT NULL,
  projectId character varying NOT NULL,
  role text NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT shared_credentials_pkey PRIMARY KEY (credentialsId, projectId),
  CONSTRAINT FK_416f66fc846c7c442970c094ccf FOREIGN KEY (credentialsId) REFERENCES public.credentials_entity(id),
  CONSTRAINT FK_812c2852270da1247756e77f5a4 FOREIGN KEY (projectId) REFERENCES public.project(id)
);
CREATE TABLE public.shared_workflow (
  workflowId character varying NOT NULL,
  projectId character varying NOT NULL,
  role text NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT shared_workflow_pkey PRIMARY KEY (workflowId, projectId),
  CONSTRAINT FK_daa206a04983d47d0a9c34649ce FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id),
  CONSTRAINT FK_a45ea5f27bcfdc21af9b4188560 FOREIGN KEY (projectId) REFERENCES public.project(id)
);
CREATE TABLE public.support_comments (
  comment_id uuid NOT NULL,
  ticket_id uuid NOT NULL,
  user_id text NOT NULL,
  comment_text text NOT NULL,
  created_at timestamp without time zone DEFAULT now(),
  comment_sent text,
  comment_received text,
  comment_type text,
  comment_source text,
  CONSTRAINT support_comments_pkey PRIMARY KEY (comment_id),
  CONSTRAINT support_comments_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.support_tickets(ticket_id)
);
CREATE TABLE public.support_tickets (
  user_id text NOT NULL,
  subject text,
  message text NOT NULL,
  status text DEFAULT 'open'::text CHECK (status = ANY (ARRAY['OPEN'::text, 'CLOSED'::text, 'PENDING'::text])),
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  contact_preference text DEFAULT 'aucun'::text CHECK (contact_preference = ANY (ARRAY['mail'::text, 'phone'::text, 'aucun'::text])),
  phone text,
  mail text,
  ticket_id uuid NOT NULL DEFAULT gen_random_uuid(),
  CONSTRAINT support_tickets_pkey PRIMARY KEY (ticket_id),
  CONSTRAINT support_tickets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(uid)
);
CREATE TABLE public.tag_entity (
  name character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  id character varying NOT NULL,
  CONSTRAINT tag_entity_pkey PRIMARY KEY (id)
);
CREATE TABLE public.test_case_execution (
  id character varying NOT NULL,
  testRunId character varying NOT NULL,
  pastExecutionId integer,
  executionId integer,
  evaluationExecutionId integer,
  status character varying NOT NULL,
  runAt timestamp with time zone,
  completedAt timestamp with time zone,
  errorCode character varying,
  errorDetails json,
  metrics json,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT test_case_execution_pkey PRIMARY KEY (id),
  CONSTRAINT FK_8e4b4774db42f1e6dda3452b2af FOREIGN KEY (testRunId) REFERENCES public.test_run(id),
  CONSTRAINT FK_258d954733841d51edd826a562b FOREIGN KEY (pastExecutionId) REFERENCES public.execution_entity(id),
  CONSTRAINT FK_e48965fac35d0f5b9e7f51d8c44 FOREIGN KEY (executionId) REFERENCES public.execution_entity(id),
  CONSTRAINT FK_dfbe194e3ebdfe49a87bc4692ca FOREIGN KEY (evaluationExecutionId) REFERENCES public.execution_entity(id)
);
CREATE TABLE public.test_definition (
  name character varying NOT NULL,
  workflowId character varying NOT NULL,
  evaluationWorkflowId character varying,
  annotationTagId character varying,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  description text,
  id character varying NOT NULL,
  mockedNodes json NOT NULL DEFAULT '[]'::json,
  CONSTRAINT test_definition_pkey PRIMARY KEY (id),
  CONSTRAINT FK_b0dd0087fe3da02b0ffa4b9c5bb FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id),
  CONSTRAINT FK_9ec1ce6fbf82305f489adb971d3 FOREIGN KEY (evaluationWorkflowId) REFERENCES public.workflow_entity(id),
  CONSTRAINT FK_d5d7ea64662dbc62f5e266fbeb0 FOREIGN KEY (annotationTagId) REFERENCES public.annotation_tag_entity(id)
);
CREATE TABLE public.test_metric (
  id character varying NOT NULL,
  name character varying NOT NULL,
  testDefinitionId character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT test_metric_pkey PRIMARY KEY (id),
  CONSTRAINT FK_3a4e9cf37111ac3270e2469b475 FOREIGN KEY (testDefinitionId) REFERENCES public.test_definition(id)
);
CREATE TABLE public.test_run (
  id character varying NOT NULL,
  testDefinitionId character varying NOT NULL,
  status character varying NOT NULL,
  runAt timestamp with time zone,
  completedAt timestamp with time zone,
  metrics json,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  totalCases integer,
  passedCases integer,
  failedCases integer,
  errorCode character varying,
  errorDetails text,
  CONSTRAINT test_run_pkey PRIMARY KEY (id),
  CONSTRAINT FK_3a81713a76f2295b12b46cdfcab FOREIGN KEY (testDefinitionId) REFERENCES public.test_definition(id)
);
CREATE TABLE public.ticket_references (
  reference_token character varying NOT NULL,
  ticket_id character varying NOT NULL UNIQUE,
  created_at timestamp without time zone NOT NULL,
  expires_at timestamp without time zone,
  CONSTRAINT ticket_references_pkey PRIMARY KEY (reference_token)
);
CREATE TABLE public.transactions (
  id text NOT NULL,
  user_id text NOT NULL,
  external_id text,
  msg text,
  amount integer,
  status text,
  phone text,
  service_code text,
  sender text,
  created_at timestamp without time zone,
  updated_at timestamp without time zone,
  error_message text,
  has_transactions boolean,
  metadata jsonb,
  CONSTRAINT transactions_pkey PRIMARY KEY (id),
  CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES public.users(uid)
);
CREATE TABLE public.trip_embeddings (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  trip_id text,
  content text,
  embedding USER-DEFINED,
  created_at timestamp without time zone DEFAULT now(),
  CONSTRAINT trip_embeddings_pkey PRIMARY KEY (id),
  CONSTRAINT trip_embeddings_trip_id_fkey FOREIGN KEY (trip_id) REFERENCES public.trips(trip_id)
);
CREATE TABLE public.trips (
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  departure_date timestamp with time zone,
  departure_name text,
  departure_schedule timestamp with time zone,
  destination_name text,
  seats_available bigint,
  passenger_price bigint,
  distance double precision,
  precision text,
  polyline text,
  trip_id text NOT NULL,
  driver_id text,
  departure_latitude double precision,
  departure_longitude double precision,
  destination_latitude double precision,
  destination_longitude double precision,
  updated_at timestamp with time zone,
  seats_booked bigint,
  seats_published bigint,
  driver_price bigint,
  status text,
  departure_description text,
  destination_description text,
  auto_confirmation boolean,
  CONSTRAINT trips_pkey PRIMARY KEY (trip_id),
  CONSTRAINT fk_driver FOREIGN KEY (driver_id) REFERENCES public.users(uid)
);
CREATE TABLE public.user (
  id uuid NOT NULL DEFAULT uuid_in((OVERLAY(OVERLAY(md5((((random())::text || ':'::text) || (clock_timestamp())::text)) PLACING '4'::text FROM 13) PLACING to_hex((floor(((random() * (((11 - 8) + 1))::double precision) + (8)::double precision)))::integer) FROM 17))::cstring),
  email character varying UNIQUE,
  firstName character varying,
  lastName character varying,
  password character varying,
  personalizationAnswers json,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  settings json,
  disabled boolean NOT NULL DEFAULT false,
  mfaEnabled boolean NOT NULL DEFAULT false,
  mfaSecret text,
  mfaRecoveryCodes text,
  role text NOT NULL,
  CONSTRAINT user_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_api_keys (
  id character varying NOT NULL,
  userId uuid NOT NULL,
  label character varying NOT NULL,
  apiKey character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT user_api_keys_pkey PRIMARY KEY (id),
  CONSTRAINT FK_e131705cbbc8fb589889b02d457 FOREIGN KEY (userId) REFERENCES public.user(id)
);
CREATE TABLE public.users (
  uid text NOT NULL UNIQUE,
  display_name text,
  email text,
  first_name text,
  name text,
  phone_number text,
  birth date,
  photo_url text,
  bio text,
  driver_license_url text,
  gender text,
  id_card_url text,
  rating numeric,
  rating_count integer,
  role text,
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  is_driver_doc_validated boolean DEFAULT false,
  CONSTRAINT users_pkey PRIMARY KEY (uid)
);
CREATE TABLE public.variables (
  key character varying NOT NULL UNIQUE,
  type character varying NOT NULL DEFAULT 'string'::character varying,
  value character varying,
  id character varying NOT NULL,
  CONSTRAINT variables_pkey PRIMARY KEY (id)
);
CREATE TABLE public.webhook_entity (
  webhookPath character varying NOT NULL,
  method character varying NOT NULL,
  node character varying NOT NULL,
  webhookId character varying,
  pathLength integer,
  workflowId character varying NOT NULL,
  CONSTRAINT webhook_entity_pkey PRIMARY KEY (webhookPath, method),
  CONSTRAINT fk_webhook_entity_workflow_id FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id)
);
CREATE TABLE public.workflow_entity (
  name character varying NOT NULL,
  active boolean NOT NULL,
  nodes json NOT NULL,
  connections json NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  settings json,
  staticData json,
  pinData json,
  versionId character,
  triggerCount integer NOT NULL DEFAULT 0,
  id character varying NOT NULL,
  meta json,
  parentFolderId character varying DEFAULT NULL::character varying,
  CONSTRAINT workflow_entity_pkey PRIMARY KEY (id),
  CONSTRAINT fk_workflow_parent_folder FOREIGN KEY (parentFolderId) REFERENCES public.folder(id)
);
CREATE TABLE public.workflow_history (
  versionId character varying NOT NULL,
  workflowId character varying NOT NULL,
  authors character varying NOT NULL,
  createdAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updatedAt timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  nodes json NOT NULL,
  connections json NOT NULL,
  CONSTRAINT workflow_history_pkey PRIMARY KEY (versionId),
  CONSTRAINT FK_1e31657f5fe46816c34be7c1b4b FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id)
);
CREATE TABLE public.workflow_statistics (
  count integer DEFAULT 0,
  latestEvent timestamp with time zone,
  name character varying NOT NULL,
  workflowId character varying NOT NULL,
  CONSTRAINT workflow_statistics_pkey PRIMARY KEY (workflowId, name),
  CONSTRAINT fk_workflow_statistics_workflow_id FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id)
);
CREATE TABLE public.workflows_tags (
  workflowId character varying NOT NULL,
  tagId character varying NOT NULL,
  CONSTRAINT workflows_tags_pkey PRIMARY KEY (workflowId, tagId),
  CONSTRAINT fk_workflows_tags_workflow_id FOREIGN KEY (workflowId) REFERENCES public.workflow_entity(id),
  CONSTRAINT fk_workflows_tags_tag_id FOREIGN KEY (tagId) REFERENCES public.tag_entity(id)
);