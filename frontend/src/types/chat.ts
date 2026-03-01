export interface ChatMessage {
  id: string;
  trip_id: string | null;
  sender_id: string | null;
  message: string;
  timestamp: string;
  updated_at: string;
  // Joined info
  sender?: {
    display_name: string | null;
    photo_url: string | null;
  };
}

export interface Conversation {
  trip_id: string;
  last_message: string;
  last_timestamp: string;
  participant_ids: string[];
  participants: Array<{
    uid: string;
    display_name: string | null;
    photo_url: string | null;
  }>;
  departure_name?: string | null;
  destination_name?: string | null;
}
