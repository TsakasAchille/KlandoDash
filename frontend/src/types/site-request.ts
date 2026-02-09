export type SiteTripRequestStatus = 'NEW' | 'REVIEWED' | 'CONTACTED' | 'IGNORED';

export interface SiteTripRequest {
  id: string;
  origin_city: string;
  destination_city: string;
  desired_date: string | null;
  contact_info: string;
  status: SiteTripRequestStatus;
  created_at: string;
  notes: string | null;
}

export interface SiteTripRequestsStats {
  total: number;
  new: number;
  reviewed: number;
  contacted: number;
}
