-- =============================================================================
-- Migration: WhatsApp Business API Integration
-- Description: Tables to store WhatsApp conversations and messages.
-- =============================================================================

-- 1. Conversation Table (Groups messages by user)
CREATE TABLE IF NOT EXISTS public.whatsapp_conversations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    wa_id text UNIQUE NOT NULL, -- WhatsApp ID (Phone number)
    display_name text,
    last_message_at timestamptz DEFAULT now(),
    unread_count integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. Messages Table
CREATE TABLE IF NOT EXISTS public.whatsapp_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id uuid REFERENCES public.whatsapp_conversations(id) ON DELETE CASCADE,
    wa_message_id text UNIQUE, -- Meta's message ID
    direction text CHECK (direction IN ('INBOUND', 'OUTBOUND')),
    type text DEFAULT 'text', -- text, image, audio, etc.
    content text,
    media_url text,
    status text DEFAULT 'sent', -- sent, delivered, read, failed
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- 3. Indices
CREATE INDEX idx_wa_messages_conv ON public.whatsapp_messages(conversation_id);
CREATE INDEX idx_wa_messages_created ON public.whatsapp_messages(created_at DESC);

-- 4. RLS
ALTER TABLE public.whatsapp_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.whatsapp_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated full access to WhatsApp" ON public.whatsapp_conversations
FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow authenticated full access to WA messages" ON public.whatsapp_messages
FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- 5. Trigger for updated_at
CREATE OR REPLACE FUNCTION update_wa_conv_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.whatsapp_conversations 
    SET last_message_at = NOW(), updated_at = NOW() 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_update_wa_conv_time
AFTER INSERT ON public.whatsapp_messages
FOR EACH ROW EXECUTE FUNCTION update_wa_conv_timestamp();

-- 6. Helper functions for UI
CREATE OR REPLACE FUNCTION public.increment_wa_unread(conv_id uuid)
RETURNS void AS $$
BEGIN
    UPDATE public.whatsapp_conversations 
    SET unread_count = unread_count + 1 
    WHERE id = conv_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.reset_wa_unread(conv_id uuid)
RETURNS void AS $$
BEGIN
    UPDATE public.whatsapp_conversations 
    SET unread_count = 0 
    WHERE id = conv_id;
END;
$$ LANGUAGE plpgsql;
