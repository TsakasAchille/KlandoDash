-- Migration: Create Internal Admin Chat Table
-- Description: Stores messages between dashboard staff members.

CREATE TABLE IF NOT EXISTS public.dash_internal_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_email TEXT NOT NULL REFERENCES public.dash_authorized_users(email) ON DELETE CASCADE,
    content TEXT NOT NULL,
    channel_id TEXT DEFAULT 'general', -- Pourrait servir plus tard à avoir des salons (ex: #support, #marketing)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index pour la rapidité
CREATE INDEX idx_internal_messages_created_at ON public.dash_internal_messages(created_at DESC);

-- RLS
ALTER TABLE public.dash_internal_messages ENABLE ROW LEVEL SECURITY;

-- Tout utilisateur du dash peut lire et écrire
CREATE POLICY "Dashboard users can manage internal messages" 
ON public.dash_internal_messages FOR ALL TO authenticated 
USING (
  EXISTS (
    SELECT 1 FROM public.dash_authorized_users 
    WHERE email = auth.jwt()->>'email' AND active = true
  )
);
