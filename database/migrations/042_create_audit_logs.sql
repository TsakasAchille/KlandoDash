-- Migration: Create Audit Logs Table
-- Description: Tracks all administrative actions for security and monitoring.

CREATE TABLE IF NOT EXISTS public.dash_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    admin_email TEXT NOT NULL,
    action_type TEXT NOT NULL, -- e.g., 'USER_UPDATE', 'EMAIL_SENT', 'POST_CREATED', 'TRIP_VALIDATED'
    entity_type TEXT NOT NULL, -- e.g., 'USER', 'MARKETING_EMAIL', 'COMMUNICATION', 'TRIP'
    entity_id TEXT,            -- ID of the affected record
    details JSONB DEFAULT '{}'::jsonb,
    ip_address TEXT
);

-- Index for performance
CREATE INDEX idx_audit_logs_created_at ON public.dash_audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_admin_email ON public.dash_audit_logs(admin_email);

-- RLS
ALTER TABLE public.dash_audit_logs ENABLE ROW LEVEL SECURITY;

-- Only admins can view logs
CREATE POLICY "Admins can view audit logs" 
ON public.dash_audit_logs FOR SELECT TO authenticated 
USING (
  EXISTS (
    SELECT 1 FROM public.dash_authorized_users 
    WHERE email = auth.jwt()->>'email' AND role = 'admin'
  )
);

-- System can insert logs (via service role or authenticated actions)
CREATE POLICY "Authenticated users can insert audit logs" 
ON public.dash_audit_logs FOR INSERT TO authenticated 
WITH CHECK (true);
