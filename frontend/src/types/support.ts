// Types pour le module Support Technique

export type TicketStatus = "OPEN" | "CLOSED" | "PENDING";
export type ContactPreference = "mail" | "phone" | "aucun";
export type CommentSource = "admin" | "user" | "system";

// Ticket de base (table support_tickets)
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

// Ticket avec infos utilisateur (retour de get_tickets_with_user)
export interface SupportTicketWithUser {
  ticket_id: string;
  subject: string | null;
  message: string;
  status: TicketStatus;
  contact_preference: ContactPreference;
  created_at: string;
  updated_at: string;
  user_uid: string | null;
  user_display_name: string | null;
  user_phone: string | null;
  user_email: string | null;
  comment_count: number;
}

// Commentaire (table support_comments)
export interface SupportComment {
  comment_id: string;
  ticket_id: string;
  user_id: string;
  comment_text: string;
  created_at: string;
  comment_source: CommentSource;
  user_display_name: string | null;
  user_avatar_url: string | null;
}

// Detail du ticket avec commentaires (retour de get_ticket_detail)
export interface TicketDetail {
  ticket_id: string;
  subject: string | null;
  message: string;
  status: TicketStatus;
  contact_preference: ContactPreference;
  phone: string | null;
  mail: string | null;
  created_at: string;
  updated_at: string;
  user_uid: string | null;
  user_display_name: string | null;
  user_avatar_url: string | null;
  comments: SupportComment[];
}

// Stats du support
export interface SupportStats {
  total: number;
  open: number;
  closed: number;
  pending: number;
}

// Labels pour l'affichage
export const TICKET_STATUS_LABELS: Record<TicketStatus, string> = {
  OPEN: "Ouvert",
  CLOSED: "Fermé",
  PENDING: "En attente",
};

export const CONTACT_PREFERENCE_LABELS: Record<ContactPreference, string> = {
  mail: "Email",
  phone: "Téléphone",
  aucun: "Aucun",
};

export const COMMENT_SOURCE_LABELS: Record<CommentSource, string> = {
  admin: "Admin",
  user: "Utilisateur",
  system: "Système",
};
