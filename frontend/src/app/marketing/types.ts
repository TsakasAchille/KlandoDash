export type InsightCategory = 'REVENUE' | 'CONVERSION' | 'USER_QUALITY' | 'GROWTH' | 'GENERAL';

export interface MarketingInsight {
  id: string;
  category: InsightCategory;
  title: string;
  content: string;
  summary: string;
  created_at: string;
}

export type EmailStatus = 'DRAFT' | 'SENT' | 'FAILED' | 'TRASH';
export type EmailCategory = 'WELCOME' | 'MATCH_FOUND' | 'RETENTION' | 'PROMO' | 'GENERAL';

export interface MarketingEmail {
  id: string;
  category: EmailCategory;
  subject: string;
  content: string;
  recipient_email: string;
  recipient_name: string | null;
  status: EmailStatus;
  is_ai_generated: boolean;
  ai_reasoning?: string | null;
  is_liked?: boolean;
  admin_feedback?: string | null;
  image_url?: string | null;
  asset_id?: string | null;
  created_at: string;
  sent_at: string | null;
}

export type CommType = 'IDEA' | 'POST';
export type CommPlatform = 'TIKTOK' | 'INSTAGRAM' | 'X' | 'WHATSAPP' | 'GENERAL';
export type CommStatus = 'NEW' | 'DRAFT' | 'PUBLISHED' | 'TRASH';

export interface MarketingComm {
  id: string;
  type: CommType;
  platform: CommPlatform;
  title: string;
  content: string;
  hashtags?: string[];
  visual_suggestion?: string;
  status: CommStatus;
  created_at: string;
  updated_at: string;
  scheduled_at?: string | null;
  asset_id?: string | null;
  image_url?: string | null;
}

export interface MarketingAsset {
  id: string;
  file_url: string;
  file_name?: string;
  file_type?: 'IMAGE' | 'VIDEO';
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface MarketingComment {
  id: string;
  comm_id?: string | null;
  email_id?: string | null;
  user_email: string;
  content: string;
  created_at: string;
  author?: {
    display_name: string | null;
    avatar_url: string | null;
  };
}

export type RecommendationType = 'TRACTION' | 'STRATEGIC' | 'ENGAGEMENT' | 'QUALITY';
export type RecommendationStatus = 'PENDING' | 'APPLIED' | 'DISMISSED';

export interface AIRecommendation {
  id: string;
  type: RecommendationType;
  priority: number;
  title: string;
  content: Record<string, unknown>; // Complex nested object from AI matching
  target_id: string;
  status: RecommendationStatus;
  created_at: string;
}

export interface MarketingFlowStat {
  origin_city: string;
  destination_city: string;
  request_count: number;
  avg_origin_lat: number;
  avg_origin_lng: number;
  avg_dest_lat: number;
  avg_dest_lng: number;
}
