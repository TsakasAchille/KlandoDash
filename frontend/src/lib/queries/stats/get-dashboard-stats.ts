import { createServerClient } from "../../supabase";
import { getCashDirection } from "@/types/transaction";
import { DashboardStats } from "./types";

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
      .select("uid, is_driver_doc_validated, created_at, gender, birth"),
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
    gender: string | null;
    birth: string | null;
  };
  const usersData = (users || []) as UserRow[];
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const newThisMonth = usersData.filter((u: UserRow) => {
    if (!u.created_at) return false;
    return new Date(u.created_at) >= monthStart;
  }).length;

  // Gender distribution
  const genderCounts: Record<string, number> = { "Homme": 0, "Femme": 0, "Non spécifié": 0 };
  usersData.forEach((u: UserRow) => {
    const g = u.gender?.toLowerCase();
    if (g === "man") {
      genderCounts["Homme"]++;
    } else if (g === "woman") {
      genderCounts["Femme"]++;
    } else {
      genderCounts["Non spécifié"]++;
    }
  });

  // Age distribution
  const ageGroups: Record<string, number> = {
    "-18": 0,
    "18-25": 0,
    "26-35": 0,
    "36-50": 0,
    "50+": 0,
    "Inconnu": 0
  };

  usersData.forEach((u: UserRow) => {
    if (!u.birth) {
      ageGroups["Inconnu"]++;
      return;
    }
    const birthDate = new Date(u.birth);
    let age = now.getFullYear() - birthDate.getFullYear();
    const m = now.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && now.getDate() < birthDate.getDate())) {
      age--;
    }

    if (age < 18) ageGroups["-18"]++;
    else if (age <= 25) ageGroups["18-25"]++;
    else if (age <= 35) ageGroups["26-35"]++;
    else if (age <= 50) ageGroups["36-50"]++;
    else ageGroups["50+"]++;
  });

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
      demographics: {
        gender: Object.entries(genderCounts).map(([label, count]) => ({ label, count })),
        age: Object.entries(ageGroups).map(([label, count]) => ({ label, count })),
      },
      typicalProfile: {
        gender: Object.entries(genderCounts).reduce((a, b) => a[1] > b[1] ? a : b)[0],
        ageGroup: Object.entries(ageGroups).filter(([l]) => l !== "Inconnu").reduce((a, b) => a[1] > b[1] ? a : b)[0]
      }
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
