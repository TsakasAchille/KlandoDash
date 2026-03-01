export interface InternalMessage {
  id: string;
  sender_email: string;
  content: string;
  channel_id: string;
  created_at: string;
  // Infos jointes du staff
  sender?: {
    role: string;
    display_name?: string;
  };
}

export interface InternalChannel {
  id: string;
  name: string;
  last_message?: string;
  last_timestamp?: string;
}
