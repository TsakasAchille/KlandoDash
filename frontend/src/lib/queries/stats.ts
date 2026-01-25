import { createServerClient } from "../supabase";

export interface DashboardStats {
  trips: {
    total: number;
    byStatus: { status: string; count: number }[];
    totalDistance: number;
    totalSeatsBooked: number;
  };
  users: {
    total: number;
    verifiedDrivers: number;
    newThisMonth: number;
  };
  bookings: {
    total: number;
  };
  revenue: {
    totalPassengerPrice: number;
    totalDriverPrice: number;
    avgTripPrice: number;
  };
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const supabase = createServerClient();

  // Fetch trips data
  const { data: trips } = await supabase
    .from("trips")
    .select("status, distance, seats_booked, passenger_price, driver_price");

  // Fetch users data
  const { data: users } = await supabase
    .from("users")
    .select("uid, is_driver_doc_validated, created_at");

  // Fetch bookings count
  const { count: bookingsCount } = await supabase
    .from("bookings")
    .select("*", { count: "exact", head: true });

  // Process trips
  type TripRow = {
    status: string | null;
    distance: number | null;
    seats_booked: number | null;
    passenger_price: number | null;
    driver_price: number | null;
  };
  const tripsData = (trips || []) as TripRow[];

  // Count by status
  const statusCounts: Record<string, number> = {};
  tripsData.forEach((t: TripRow) => {
    const status = t.status || "UNKNOWN";
    statusCounts[status] = (statusCounts[status] || 0) + 1;
  });
  const byStatus = Object.entries(statusCounts).map(([status, count]) => ({
    status,
    count,
  }));

  // Process users
  type UserRow = {
    uid: string;
    is_driver_doc_validated: boolean | null;
    created_at: string | null;
  };
  const usersData = (users || []) as UserRow[];
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const newThisMonth = usersData.filter((u: UserRow) => {
    if (!u.created_at) return false;
    return new Date(u.created_at) >= monthStart;
  }).length;

  return {
    trips: {
      total: tripsData.length,
      byStatus,
      totalDistance: tripsData.reduce((sum: number, t: TripRow) => sum + (t.distance || 0), 0),
      totalSeatsBooked: tripsData.reduce((sum: number, t: TripRow) => sum + (t.seats_booked || 0), 0),
    },
    users: {
      total: usersData.length,
      verifiedDrivers: usersData.filter((u: UserRow) => u.is_driver_doc_validated === true).length,
      newThisMonth,
    },
    bookings: {
      total: bookingsCount || 0,
    },
    revenue: {
      totalPassengerPrice: tripsData.reduce((sum: number, t: TripRow) => sum + (t.passenger_price || 0), 0),
      totalDriverPrice: tripsData.reduce((sum: number, t: TripRow) => sum + (t.driver_price || 0), 0),
      avgTripPrice: tripsData.length > 0
        ? Math.round(tripsData.reduce((sum: number, t: TripRow) => sum + (t.passenger_price || 0), 0) / tripsData.length)
        : 0,
    },
  };
}
