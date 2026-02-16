import { createServerClient } from "../../supabase";
import {
  TransactionStats,
  CashFlowStats,
  RevenueStats,
  getCashDirection,
} from "@/types/transaction";

/**
 * Stats agrégées des transactions
 */
export async function getTransactionsStats(): Promise<TransactionStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from("transactions")
    .select("id, amount, status, type");

  if (error) {
    console.error("Erreur getTransactionsStats:", error.message);
    return { total: 0, totalAmount: 0, byStatus: {}, byType: {} };
  }

  const rows = data ?? [];
  const total = rows.length;
  const totalAmount = rows.reduce((sum, r) => sum + (r.amount ?? 0), 0);

  const byStatus: Record<string, number> = {};
  const byType: Record<string, number> = {};

  for (const r of rows) {
    if (r.status) byStatus[r.status] = (byStatus[r.status] ?? 0) + 1;
    if (r.type) byType[r.type] = (byType[r.type] ?? 0) + 1;
  }

  return { total, totalAmount, byStatus, byType };
}

/**
 * Cash flow : entrées vs sorties (uniquement transactions SUCCESS)
 */
export async function getCashFlowStats(options: {
  from?: string;
  to?: string;
} = {}): Promise<CashFlowStats> {
  const { from, to } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("transactions")
    .select("amount, code_service")
    .eq("status", "SUCCESS");

  if (from) query = query.gte("created_at", from);
  if (to) query = query.lte("created_at", to);

  const { data, error } = await query;

  if (error) {
    console.error("Erreur getCashFlowStats:", error.message);
    return { totalIn: 0, totalOut: 0, solde: 0, countIn: 0, countOut: 0 };
  }

  let totalIn = 0;   
  let totalOut = 0;   
  let countIn = 0;
  let countOut = 0;

  for (const r of data ?? []) {
    const dir = getCashDirection(r.code_service);
    const amount = r.amount ?? 0;
    if (dir === "CASH_OUT") {
      totalIn += amount;
      countIn++;
    } else if (dir === "CASH_IN") {
      totalOut += amount;
      countOut++;
    }
  }

  return { totalIn, totalOut, solde: totalIn - totalOut, countIn, countOut };
}

/**
 * Revenus Klando : marge sur les bookings avec transaction
 */
export async function getRevenueStats(options: {
  from?: string;
  to?: string;
} = {}): Promise<RevenueStats> {
  const { from, to } = options;
  const supabase = createServerClient();

  const query = supabase
    .from("bookings")
    .select(`
      id,
      transaction:transactions!transaction_id (
        id,
        amount,
        status,
        created_at
      ),
      trip:trips!trip_id (
        driver_price
      )
    `)
    .not("transaction_id", "is", null);

  const { data, error } = await query;

  if (error) {
    console.error("Erreur getRevenueStats:", error.message);
    return { totalPassengerPaid: 0, totalDriverPrice: 0, klandoMargin: 0, transactionCount: 0 };
  }

  let totalPassengerPaid = 0;
  let totalDriverPrice = 0;
  let transactionCount = 0;

  for (const row of data ?? []) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const txn = row.transaction as any;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const trip = row.trip as any;

    if (!txn || txn.status !== "SUCCESS") continue;

    if (from && txn.created_at && txn.created_at < from) continue;
    if (to && txn.created_at && txn.created_at > to) continue;

    totalPassengerPaid += txn.amount ?? 0;
    totalDriverPrice += trip?.driver_price ?? 0;
    transactionCount++;
  }

  return {
    totalPassengerPaid,
    totalDriverPrice,
    klandoMargin: totalPassengerPaid - totalDriverPrice,
    transactionCount,
  };
}
