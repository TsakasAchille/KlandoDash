import { createServerClient } from "../supabase";
import { getCashDirection } from "@/types/transaction";
import type { CashFlowStats, RevenueStats } from "@/types/transaction";

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
  transactions: {
    total: number;
    totalAmount: number;
    byStatus: { status: string; count: number }[];
    byType: { type: string; count: number }[];
  };
  revenue: RevenueStats;
  cashFlow: CashFlowStats;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const supabase = createServerClient();

  // Fetch all data in parallel
  const [
    { data: trips },
    { data: users },
    { count: bookingsCount },
    { data: transactions },
    { data: bookingsWithTxn },
  ] = await Promise.all([
    supabase
      .from("trips")
      .select("status, distance, seats_booked, passenger_price, driver_price"),
    supabase
      .from("users")
      .select("uid, is_driver_doc_validated, created_at"),
    supabase
      .from("bookings")
      .select("*", { count: "exact", head: true }),
    supabase
      .from("transactions")
      .select("id, amount, status, type, code_service"),
    supabase
      .from("bookings")
      .select(`
        id,
        transaction:transactions!transaction_id (id, amount, status),
        trip:trips!trip_id (driver_price)
      `)
      .not("transaction_id", "is", null),
  ]);

  // --- Process trips ---
  type TripRow = {
    status: string | null;
    distance: number | null;
    seats_booked: number | null;
    passenger_price: number | null;
    driver_price: number | null;
  };
  const tripsData = (trips || []) as TripRow[];

  const statusCounts: Record<string, number> = {};
  tripsData.forEach((t: TripRow) => {
    const status = t.status || "UNKNOWN";
    statusCounts[status] = (statusCounts[status] || 0) + 1;
  });
  const byStatus = Object.entries(statusCounts).map(([status, count]) => ({
    status,
    count,
  }));

  // --- Process users ---
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

  // --- Process transactions ---
  type TxnRow = {
    id: string;
    amount: number | null;
    status: string | null;
    type: string | null;
    code_service: string | null;
  };
  const txnData = (transactions || []) as TxnRow[];

  const txnStatusCounts: Record<string, number> = {};
  const txnTypeCounts: Record<string, number> = {};
  let txnTotalAmount = 0;

  for (const t of txnData) {
    if (t.status) txnStatusCounts[t.status] = (txnStatusCounts[t.status] || 0) + 1;
    if (t.type) txnTypeCounts[t.type] = (txnTypeCounts[t.type] || 0) + 1;
    txnTotalAmount += t.amount ?? 0;
  }

  // --- Cash flow (uniquement SUCCESS) ---
  let totalIn = 0;
  let totalOut = 0;
  let countIn = 0;
  let countOut = 0;

  for (const t of txnData) {
    if (t.status !== "SUCCESS") continue;
    const dir = getCashDirection(t.code_service);
    const amount = t.amount ?? 0;
    if (dir === "CASH_OUT") {
      totalIn += amount;
      countIn++;
    } else if (dir === "CASH_IN") {
      totalOut += amount;
      countOut++;
    }
  }

  // --- Revenue (marge Klando via bookings) ---
  let totalPassengerPaid = 0;
  let totalDriverPrice = 0;
  let revenueCount = 0;

  for (const row of bookingsWithTxn ?? []) {
    const txn = row.transaction as unknown as { id: string; amount: number | null; status: string | null } | null;
    const trip = row.trip as unknown as { driver_price: number | null } | null;

    if (!txn || txn.status !== "SUCCESS") continue;
    totalPassengerPaid += txn.amount ?? 0;
    totalDriverPrice += trip?.driver_price ?? 0;
    revenueCount++;
  }

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
    transactions: {
      total: txnData.length,
      totalAmount: txnTotalAmount,
      byStatus: Object.entries(txnStatusCounts).map(([status, count]) => ({ status, count })),
      byType: Object.entries(txnTypeCounts).map(([type, count]) => ({ type, count })),
    },
    revenue: {
      totalPassengerPaid,
      totalDriverPrice,
      klandoMargin: totalPassengerPaid - totalDriverPrice,
      transactionCount: revenueCount,
    },
    cashFlow: {
      totalIn,
      totalOut,
      solde: totalIn - totalOut,
      countIn,
      countOut,
    },
  };
}
