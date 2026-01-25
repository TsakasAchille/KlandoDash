# Plan d'Intégration - Page Support Technique

> **Date:** 2025-01-25
> **Branche:** `feature/support-technique`
> **Complexité:** Élevée (opérations CRUD avec écritures Supabase)

---

## 1. État Actuel

### Base de données (Prête ✅)

| Table | Description | Lignes | Index |
|-------|-------------|--------|-------|
| `support_tickets` | Tickets de support | - | ❌ Aucun (à créer) |
| `support_comments` | Commentaires/réponses | - | ✅ 3 index |
| `ticket_references` | Tokens d'accès externe | - | ✅ 2 index |

### Schéma des tables

```sql
-- support_tickets
ticket_id uuid PK DEFAULT gen_random_uuid()
user_id text FK → users.uid
subject text
message text NOT NULL
status text DEFAULT 'open'
contact_preference text CHECK (mail|phone|aucun)
phone text
mail text
created_at timestamp DEFAULT now()
updated_at timestamp DEFAULT now()

-- support_comments
comment_id uuid PK
ticket_id uuid FK → support_tickets.ticket_id
user_id text NOT NULL
comment_text text NOT NULL
created_at timestamp DEFAULT now()
comment_sent text       -- tracking envoi
comment_received text   -- tracking réception
comment_type text
comment_source text     -- (admin|user|system)
```

### Relations

```
users ──< support_tickets (user_id → uid)
support_tickets ──< support_comments (ticket_id)
support_tickets ──< ticket_references (ticket_id)
```

### Webhook existant

```sql
-- Trigger sur INSERT support_tickets → n8n
webhook-support-tickets → https://klando.app.n8n.cloud/webhook/...
```

### Frontend (À créer ❌)

- Page `/support` inexistante
- Pas d'entrée dans la sidebar
- Pas de types TypeScript
- Pas de queries Supabase
- Pas de composants UI

---

## 2. Analyse des Index Manquants

### Index à créer pour `support_tickets`

```sql
-- Filtrer par status (open/closed/pending)
CREATE INDEX idx_support_tickets_status
ON support_tickets(status);

-- Trier par date de création DESC
CREATE INDEX idx_support_tickets_created_at
ON support_tickets(created_at DESC);

-- Rechercher par utilisateur
CREATE INDEX idx_support_tickets_user_id
ON support_tickets(user_id);

-- Combiné: status + date (listing principal)
CREATE INDEX idx_support_tickets_status_created
ON support_tickets(status, created_at DESC);
```

### Contraintes CHECK (à ajouter)

```sql
-- Verrouiller les valeurs autorisées pour status
ALTER TABLE support_tickets
ADD CONSTRAINT support_ticket_status_check
CHECK (status IN ('open', 'closed', 'pending'));

-- (Optionnel) Symétrie pour contact_preference
ALTER TABLE support_tickets
ADD CONSTRAINT support_ticket_contact_pref_check
CHECK (contact_preference IN ('mail', 'phone', 'aucun'));
```

> **Note:** Ces contraintes garantissent l'intégrité des données et alignent DB ↔ TypeScript.

### Index optionnel (si besoin futur)

```sql
-- Tickets récemment actifs (utile pour dashboard "activité récente")
CREATE INDEX idx_support_tickets_updated_at
ON support_tickets(updated_at DESC);
```

> **Note:** Non nécessaire en v1. À ajouter si besoin de trier par dernière activité.

### Index existants pour `support_comments` (OK ✅)

```sql
idx_support_comments_ticket_id   -- Fetch comments par ticket
idx_support_comments_sent        -- Tracking envoi
idx_support_comments_received    -- Tracking réception
```

---

## 3. Fonctions RPC à créer

### 3.1 `get_tickets_with_user`

Récupérer les tickets avec infos utilisateur (évite N+1).

```sql
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
  GROUP BY t.ticket_id, u.uid
  ORDER BY t.created_at DESC
  LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 `get_ticket_detail`

Récupérer un ticket avec ses commentaires.

```sql
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
  GROUP BY t.ticket_id, u.uid;
END;
$$ LANGUAGE plpgsql;
```

### 3.3 `update_ticket_status`

Mettre à jour le status avec timestamp.

```sql
CREATE OR REPLACE FUNCTION update_ticket_status(
  p_ticket_id uuid,
  p_status text
)
RETURNS void AS $$
BEGIN
  UPDATE support_tickets
  SET
    status = p_status,
    updated_at = now()
  WHERE ticket_id = p_ticket_id;
END;
$$ LANGUAGE plpgsql;
```

### 3.4 `add_support_comment`

Ajouter un commentaire admin.

```sql
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
    p_comment_text,
    p_comment_source,
    now()
  )
  RETURNING comment_id INTO new_comment_id;

  -- Update ticket updated_at
  UPDATE support_tickets
  SET updated_at = now()
  WHERE ticket_id = p_ticket_id;

  RETURN new_comment_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. Structure Frontend

### 4.1 Arborescence des fichiers

```
frontend/src/
├── app/
│   └── support/
│       ├── page.tsx                 # Server Component (fetch initial)
│       └── support-client.tsx       # Client Component (état, interactions)
│
├── components/
│   └── support/
│       ├── ticket-table.tsx         # Liste des tickets
│       ├── ticket-details.tsx       # Détail + commentaires
│       ├── ticket-status-badge.tsx  # Badge status (open/closed)
│       ├── comment-thread.tsx       # Thread de commentaires
│       ├── comment-form.tsx         # Formulaire ajout commentaire
│       └── ticket-filters.tsx       # Filtres (status, recherche)
│
├── lib/
│   └── queries/
│       └── support.ts               # Fonctions Supabase
│
└── types/
    └── support.ts                   # Interfaces TypeScript
```

### 4.2 Types TypeScript

```typescript
// types/support.ts

export type TicketStatus = 'open' | 'closed' | 'pending';
export type ContactPreference = 'mail' | 'phone' | 'aucun';
export type CommentSource = 'admin' | 'user' | 'system';

export interface SupportTicket {
  ticket_id: string;
  user_id: string;
  subject: string | null;
  message: string;
  status: TicketStatus;
  contact_preference: ContactPreference;
  phone: string | null;
  mail: string | null;
  created_at: string;
  updated_at: string;
}

export interface SupportTicketWithUser extends SupportTicket {
  user_display_name: string | null;
  user_phone: string | null;
  user_email: string | null;
  comment_count: number;
}

export interface SupportComment {
  comment_id: string;
  ticket_id: string;
  user_id: string;
  comment_text: string;
  created_at: string;
  comment_source: CommentSource;
}

export interface TicketDetail extends SupportTicket {
  user_display_name: string | null;
  user_avatar_url: string | null;
  comments: SupportComment[];
}
```

### 4.3 Queries Supabase

```typescript
// lib/queries/support.ts

import { createClient } from "@/lib/supabase";
import type { SupportTicketWithUser, TicketDetail, SupportComment } from "@/types/support";

// Liste des tickets avec utilisateur
export async function getTicketsWithUser(options?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<SupportTicketWithUser[]> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc("get_tickets_with_user", {
    p_status: options?.status || null,
    p_limit: options?.limit || 50,
    p_offset: options?.offset || 0,
  });

  if (error) throw error;
  return data || [];
}

// Détail d'un ticket avec commentaires
export async function getTicketDetail(ticketId: string): Promise<TicketDetail | null> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc("get_ticket_detail", {
    p_ticket_id: ticketId,
  });

  if (error) throw error;
  return data?.[0] || null;
}

// Mettre à jour le status
export async function updateTicketStatus(
  ticketId: string,
  status: string
): Promise<void> {
  const supabase = createClient();
  const { error } = await supabase.rpc("update_ticket_status", {
    p_ticket_id: ticketId,
    p_status: status,
  });

  if (error) throw error;
}

// Ajouter un commentaire
export async function addComment(
  ticketId: string,
  userId: string,
  text: string
): Promise<string> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc("add_support_comment", {
    p_ticket_id: ticketId,
    p_user_id: userId,
    p_comment_text: text,
    p_comment_source: "admin",
  });

  if (error) throw error;
  return data;
}

// Stats support
// NOTE: Approche simple pour v1 (comptage JS côté client)
// À terme: RPC dédiée avec COUNT(*) GROUP BY côté DB
export async function getSupportStats(): Promise<{
  total: number;
  open: number;
  closed: number;
  pending: number;
}> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("support_tickets")
    .select("status");

  if (error) throw error;

  const total = data?.length || 0;
  const open = data?.filter((t) => t.status === "open").length || 0;
  const pending = data?.filter((t) => t.status === "pending").length || 0;
  const closed = data?.filter((t) => t.status === "closed").length || 0;

  return { total, open, closed, pending };
}

// V2 (optionnel): RPC optimisée pour gros volumes
/*
CREATE OR REPLACE FUNCTION get_support_stats()
RETURNS TABLE (status text, count bigint) AS $$
BEGIN
  RETURN QUERY
  SELECT t.status, COUNT(*) as count
  FROM support_tickets t
  GROUP BY t.status;
END;
$$ LANGUAGE plpgsql;
*/
```

---

## 5. Composants UI

### 5.1 Page principale (`support-client.tsx`)

| Élément | Description |
|---------|-------------|
| Header | Titre "Support Technique" + stats (total, open, closed) |
| Filtres | Dropdown status (Tous/Ouverts/Fermés) + recherche |
| Liste | Table des tickets avec pagination |
| Détail | Panel latéral avec détail + commentaires |

### 5.2 Table des tickets (`ticket-table.tsx`)

| Colonne | Source | Notes |
|---------|--------|-------|
| Sujet | `subject` | Tronqué si > 50 chars |
| Utilisateur | `user_display_name` | Avec avatar |
| Status | `status` | Badge coloré |
| Date | `created_at` | Format FR relatif |
| Commentaires | `comment_count` | Badge numérique |
| Actions | - | Bouton "Voir" |

### 5.3 Détail ticket (`ticket-details.tsx`)

```
┌────────────────────────────────────────┐
│ [Badge Status]  Sujet du ticket        │
│ Par: Nom Utilisateur • 15/01/2025      │
├────────────────────────────────────────┤
│ Message original:                      │
│ Lorem ipsum dolor sit amet...          │
├────────────────────────────────────────┤
│ Contact: ☎ +221 77 123 45 67           │
│          ✉ email@example.com           │
├────────────────────────────────────────┤
│ Actions:                               │
│ [Marquer Fermé] [Marquer En attente]   │
├────────────────────────────────────────┤
│ Commentaires (3):                      │
│ ┌──────────────────────────────────┐   │
│ │ Admin • 16/01 14:30              │   │
│ │ Nous avons bien reçu...          │   │
│ └──────────────────────────────────┘   │
│ ┌──────────────────────────────────┐   │
│ │ User • 16/01 15:45               │   │
│ │ Merci pour la réponse...         │   │
│ └──────────────────────────────────┘   │
├────────────────────────────────────────┤
│ [Textarea: Ajouter un commentaire]     │
│                          [Envoyer]     │
└────────────────────────────────────────┘
```

### 5.4 Formulaire commentaire (`comment-form.tsx`)

- Textarea avec validation (min 10 chars)
- Bouton "Envoyer" avec loading state
- Optimistic update du thread
- Toast de confirmation

---

## 6. Opérations CRUD

### Lecture (Read)

| Action | Méthode | Endpoint/RPC |
|--------|---------|--------------|
| Liste tickets | GET | `rpc/get_tickets_with_user` |
| Détail ticket | GET | `rpc/get_ticket_detail` |
| Stats | GET | `from('support_tickets').select('status')` |

### Écriture (Write)

| Action | Méthode | Endpoint/RPC | Validation |
|--------|---------|--------------|------------|
| Changer status | POST | `rpc/update_ticket_status` | Status valide |
| Ajouter commentaire | POST | `rpc/add_support_comment` | Min 10 chars |

### Pas d'opération DELETE

- Les tickets ne sont jamais supprimés (archivage via status)
- Les commentaires ne sont jamais supprimés

---

## 7. Sécurité & Validation

### Côté serveur (RPC)

- Validation du status dans les valeurs autorisées
- Validation de l'existence du ticket avant modification
- Logging des modifications (à implémenter si nécessaire)

### Côté client

```typescript
// Validation commentaire
const commentSchema = z.object({
  text: z.string().min(10, "Le commentaire doit faire au moins 10 caractères"),
});

// Validation status
const statusSchema = z.enum(["open", "closed", "pending"]);
```

---

## 8. Étapes d'implémentation

### Phase 1: Base de données (1 migration)

```
database/migrations/
└── 004_support_indexes_and_functions.sql
```

Contenu:
1. Créer les 4 index manquants sur `support_tickets`
2. Créer les 4 fonctions RPC
3. Tester les fonctions

### Phase 2: Types & Queries

1. Créer `types/support.ts`
2. Créer `lib/queries/support.ts`
3. Tester les queries en isolation

### Phase 3: Composants UI

1. `ticket-status-badge.tsx` (simple)
2. `ticket-table.tsx` (basé sur `trip-table.tsx`)
3. `ticket-filters.tsx`
4. `comment-thread.tsx`
5. `comment-form.tsx`
6. `ticket-details.tsx` (composition)

### Phase 4: Page Support

1. `support/page.tsx` (Server Component)
2. `support/support-client.tsx` (Client Component)
3. Ajouter dans sidebar

### Phase 5: Tests & Polish

1. Test création commentaire
2. Test changement status
3. Gestion erreurs (toasts)
4. États de chargement
5. Responsive design

---

## 9. Estimation de complexité

| Composant | Complexité | Raison |
|-----------|------------|--------|
| Migration SQL | Faible | SQL standard |
| Types TS | Faible | Interfaces simples |
| Queries | Moyenne | RPC avec paramètres |
| Table tickets | Moyenne | Similaire à trips |
| Détail ticket | Élevée | Composition + state |
| Formulaire commentaire | Élevée | Validation + optimistic |
| Intégration globale | Élevée | State partagé read/write |

**Total estimé:** Élevé (plus complexe que Users/Trips car CRUD complet)

---

## 10. Dépendances

### Packages existants (OK)

- `@supabase/supabase-js` ✅
- `lucide-react` (icônes) ✅
- `date-fns` (dates) ✅
- Shadcn/ui components ✅

### À vérifier/ajouter

```bash
# Validation formulaires (si pas déjà installé)
npm install zod react-hook-form @hookform/resolvers

# Toast notifications (si pas Shadcn toast)
npx shadcn-ui@latest add toast
```

---

## 11. Points d'attention

### ⚠️ Webhook n8n

Le trigger `webhook-support-tickets` envoie les nouveaux tickets à n8n. S'assurer que:
- Le webhook est actif et fonctionnel
- Ne pas modifier le trigger sans coordination

### ⚠️ Contact Preference

La contrainte CHECK limite à `mail|phone|aucun`. Afficher correctement dans l'UI.

### ⚠️ Pas de RLS

Les tables support n'ont pas de RLS. Le dashboard utilise `service_role_key` - OK pour admin.

### ⚠️ Timezone

Les timestamps sont `timestamp` (sans timezone) vs `timestamptz` dans trips.

**Solution côté UI:**
```typescript
import { format } from "date-fns";
import { fr } from "date-fns/locale";

// Afficher en local admin (pas de conversion TZ)
const formatTicketDate = (date: string) =>
  format(new Date(date), "dd/MM/yyyy HH:mm", { locale: fr });

// Ou format relatif
import { formatDistanceToNow } from "date-fns";
const formatRelative = (date: string) =>
  formatDistanceToNow(new Date(date), { addSuffix: true, locale: fr });
```

> **Note:** Pas de changement DB nécessaire. La cohérence est maintenue côté affichage.

---

## 12. Améliorations Futures (Optionnel)

### 🚀 Audit Log (si besoin de traçabilité)

```sql
CREATE TABLE support_ticket_events (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id uuid FK → support_tickets.ticket_id,
  event_type text NOT NULL, -- 'status_changed', 'comment_added', 'assigned'
  actor_id text,            -- Admin qui a fait l'action
  old_value text,
  new_value text,
  created_at timestamp DEFAULT now()
);
```

> Non implémenté en v1. Le schéma actuel permet cette extension sans refactor.

### 🚀 Auto-close / SLA

Le schéma permet d'implémenter:
- Auto-close après X jours sans réponse (via n8n ou cron)
- Alertes SLA (ticket ouvert > 48h)
- Escalation automatique

> Workflow n8n existant = base idéale pour ces extensions.

### 🚀 Exposition côté utilisateur (si besoin)

Si un jour `/support` devient accessible aux users:
- Créer des vues SQL filtrées
- Ou RPC user-scoped avec `auth.uid()`
- Activer RLS sur les tables

---

## 13. Checklist finale

### Phase 1: Base de données
- [ ] Créer migration `004_support_indexes_and_functions.sql`
- [ ] Ajouter contrainte CHECK status (`open|closed|pending`)
- [ ] Créer les 4 index sur `support_tickets`
- [ ] Créer les 4 fonctions RPC
- [ ] Tester les fonctions via Supabase SQL Editor

### Phase 2: Types & Queries
- [ ] Créer `types/support.ts`
- [ ] Créer `lib/queries/support.ts`
- [ ] Tester les queries en isolation

### Phase 3: Composants UI
- [ ] `ticket-status-badge.tsx`
- [ ] `ticket-table.tsx`
- [ ] `ticket-filters.tsx`
- [ ] `comment-thread.tsx`
- [ ] `comment-form.tsx`
- [ ] `ticket-details.tsx`

### Phase 4: Page Support
- [ ] `support/page.tsx` (Server Component)
- [ ] `support/support-client.tsx` (Client Component)
- [ ] Ajouter entrée "Support" dans sidebar

### Phase 5: Tests & Polish
- [ ] Test création commentaire
- [ ] Test changement status
- [ ] Gestion erreurs (toasts)
- [ ] États de chargement
- [ ] Responsive design

---

*Document mis à jour avec retours d'analyse. Prêt pour implémentation.*
