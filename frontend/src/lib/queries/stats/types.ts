import type { CashFlowStats, RevenueStats, TransactionWithUser } from "@/types/transaction";
import type { Trip } from "@/types/trip";
import type { SupportTicketWithUser } from "@/types/support";
import type { UserListItem } from "@/types/user";

export interface DashboardStats {
  trips: {
    total: number;
    byStatus: { status: string; count: number }[];
    totalDistance: number;
    totalSeatsBooked: number;
    cancellationRate?: number;
    avgSeatsPerTrip?: number;
  };
  users: {
    total: number;
    verifiedDrivers: number;
    newThisMonth: number;
    demographics: {
      gender: { label: string; count: number }[];
      age: { label: string; count: number }[];
    };
    typicalProfile: {
      gender: string;
      ageGroup: string;
    };
    acquisition?: {
      verificationStatus: { status: string; count: number }[];
      topDrivers: { uid: string; display_name: string; photo_url: string; trips_count: number; rating: number; revenue: number }[];
    };
    typology?: {
      drivers: number;
      passengers: number;
      mixed: number;
    };
  };
  bookings: {
    total: number;
  };
  transactions: {
    total: number;
    totalAmount: number;
    byStatus: { status: string; count: number }[];
    byType: { type: string; count: number }[];
  };
  revenue: RevenueStats;
  cashFlow: CashFlowStats;
  marketing?: {
    siteRequestsTotal: number;
  };
}

export interface PublicTrip {
  id: string;
  departure_city: string;
  arrival_city: string;
  departure_time: string;
  seats_available?: number;
}

export interface HomeSummary extends DashboardStats {
  recentTrips: Trip[];
  recentTransactions: TransactionWithUser[];
  recentTickets: SupportTicketWithUser[];
  recentUsers: UserListItem[];
  publicPending: PublicTrip[];
  publicCompleted: PublicTrip[];
}
