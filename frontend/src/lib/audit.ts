import { auth } from "@/lib/auth";
import { createAdminClient } from "@/lib/supabase";

export type AuditAction =
  | 'USER_CREATE' | 'USER_UPDATE' | 'USER_DELETE'
  | 'USER_VALIDATED' | 'USER_INVALIDATED' | 'USER_AI_ANALYZED'
  | 'EMAIL_SENT' | 'MESSAGE_SENT' | 'MESSAGE_DRAFT_CREATED' | 'MESSAGE_TRASHED' | 'EMAIL_DRAFT_CREATED' | 'EMAIL_TRASHED'
  | 'POST_CREATED' | 'POST_UPDATED' | 'POST_TRASHED' | 'POST_DELETED'
  | 'TRIP_VALIDATED' | 'TRIP_CANCELLED'
  | 'IA_DATA_INGESTION' | 'LOGIN_SUCCESS';
export type AuditEntity = 'USER' | 'MARKETING_EMAIL' | 'MARKETING_MESSAGE' | 'COMMUNICATION' | 'TRIP' | 'SYSTEM';

interface LogOptions {
  action: AuditAction;
  entityType: AuditEntity;
  entityId?: string;
  details?: Record<string, any>;
}

/**
 * Records an administrative action in the audit logs.
 */
export async function recordAuditLog({ 
  action, 
  entityType, 
  entityId, 
  details = {} 
}: LogOptions) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      console.warn(`[AUDIT] Attempted to log "${action}" without a valid session.`);
      return;
    }

    const supabase = createAdminClient();
    
    const { error } = await supabase
      .from('dash_audit_logs')
      .insert([{
        admin_email: session.user.email,
        action_type: action,
        entity_type: entityType,
        entity_id: entityId,
        details: details,
        // We can't easily get the client IP in a standard server action without extra headers, 
        // but for now, the email and timestamp are the most critical.
      }]);

    if (error) {
      console.error("[AUDIT] Failed to insert log:", error.message);
    }
  } catch (err) {
    console.error("[AUDIT] Unexpected error during logging:", err);
  }
}
