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
  image_url?: string | null;
  created_at: string;
  sent_at: string | null;
}

export type CommType = 'IDEA' | 'POST';
export type CommPlatform = 'TIKTOK' | 'INSTAGRAM' | 'X' | 'WHATSAPP' | 'GENERAL';

export interface MarketingComm {
  id: string;
  type: CommType;
  platform: CommPlatform;
  title: string;
  content: string;
  hashtags?: string[];
  visual_suggestion?: string;
  created_at: string;
}

export type RecommendationType = 'TRACTION' | 'STRATEGIC' | 'ENGAGEMENT' | 'QUALITY';
export type RecommendationStatus = 'PENDING' | 'APPLIED' | 'DISMISSED';

export interface AIRecommendation {
  id: string;
  type: RecommendationType;
  priority: number;
  title: string;
  content: any;
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
