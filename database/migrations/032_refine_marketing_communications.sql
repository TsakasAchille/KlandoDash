-- Migration: Enhance Marketing Communications Status
-- Description: Adds a robust status enum and updated_at column for better management.

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'comm_status') THEN
        CREATE TYPE comm_status AS ENUM ('NEW', 'DRAFT', 'PUBLISHED', 'TRASH');
    END IF;
END $$;

ALTER TABLE public.dash_marketing_communications 
ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

-- Temporarily drop default to change type if needed, or just alter
ALTER TABLE public.dash_marketing_communications 
ALTER COLUMN status TYPE text; -- Ensure it's text first to avoid casting issues

-- Update existing PENDING to NEW
UPDATE public.dash_marketing_communications SET status = 'NEW' WHERE status = 'PENDING';

-- Now change to enum if possible, or just keep as text with check constraint for simplicity in migrations
ALTER TABLE public.dash_marketing_communications 
ADD CONSTRAINT check_comm_status CHECK (status IN ('NEW', 'DRAFT', 'PUBLISHED', 'TRASH'));

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_marketing_comm_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_marketing_comm_modtime ON public.dash_marketing_communications;
CREATE TRIGGER update_marketing_comm_modtime
    BEFORE UPDATE ON public.dash_marketing_communications
    FOR EACH ROW
    EXECUTE FUNCTION update_marketing_comm_timestamp();
