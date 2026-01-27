import { createServerClient } from "../supabase";
import {
  TransactionListItem,
  TransactionWithUser,
  TransactionWithBooking,
  TransactionStats,
  CashFlowStats,
  RevenueStats,
  getCashDirection,
} from "@/types/transaction";

/**
 * Liste des transactions (colonnes minimales)
 */
export async function getTransactions(options: {
  limit?: number;
  offset?: number;
  status?: string;
  type?: string;
  userId?: string;
} = {}): Promise<TransactionListItem[]> {
  const { limit = 50, offset = 0, status, type, userId } = options;
  const supabase = createServerClient();

  let query = supabase
    .from("transactions")
    .select(`
      id,
      user_id,
      amount,
      status,
      type,
      code_service,
      phone,
      created_at
    `)
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (status) query = query.eq("status", status);
  if (type) query = query.eq("type", type);
  if (userId) query = query.eq("user_id", userId);

  const { data, error } = await query;

  if (error) {
    console.error("Erreur getTransactions:", error.message);
    return [];
  }

  return (data ?? []) as TransactionListItem[];
}

/**
 * Liste des transactions avec infos utilisateur
 */
export async function getTransactionsWithUser(limit = 50): Promise<TransactionWithUser[]> {
  const supabase = createServerClient();

  // Fetch transactions first
  const { data: transactions, error: txnError } = await supabase
    .from("transactions")
    .select(`
      id,
      user_id,
      amount,
      status,
      type,
      code_service,
      phone,
      created_at
    `)
    .order("created_at", { ascending: false })
    .limit(limit);

  if (txnError) {
    console.error("Erreur getTransactionsWithUser:", txnError.message);
    return [];
  }

  if (!transactions || transactions.length === 0) {
    return [];
  }

  // Get unique user IDs and fetch users separately (no FK between transactions and users)
  const userIds = Array.from(new Set(transactions.map(t => t.user_id).filter(Boolean)));


  const { data: users } = await supabase
    .from("users")
    .select("uid, display_name, phone_number")
    .in("uid", userIds);



  const userMap = new Map(users?.map(u => [u.uid, u]) || []);

  // Merge transactions with user data
  return transactions.map(t => ({
    ...t,
    user: userMap.get(t.user_id) ? {
      display_name: userMap.get(t.user_id)!.display_name,
      phone: userMap.get(t.user_id)!.phone_number,
    } : null,
  })) as unknown as TransactionWithUser[];
}

/**
 * Détail d'une transaction par ID (avec booking + trip si lié)
 */
export async function getTransactionById(id: string): Promise<TransactionWithBooking | null> {
  const supabase = createServerClient();

  // Récupérer la transaction
  const { data: txn, error: txnError } = await supabase
    .from("transactions")
    .select("*")
    .eq("id", id)
    .single();

  if (txnError || !txn) {
    console.error("Erreur getTransactionById:", txnError?.message);
    return null;
  }

  // Récupérer l'utilisateur séparément (pas de FK entre transactions et users)
  let user = null;
  if (txn.user_id) {
    const { data: userData } = await supabase
      .from("users")
      .select("display_name, phone_number, email")
      .eq("uid", txn.user_id)
      .maybeSingle();
    user = userData ? {
      display_name: userData.display_name,
      phone: userData.phone_number,
      email: userData.email,
    } : null;
  }

  // Chercher le booking lié (bookings.transaction_id → transactions.id)
  const { data: booking } = await supabase
    .from("bookings")
    .select(`
      id,
      trip_id,
      user_id,
      trip:trips!trip_id (
        trip_id,
        departure_name,
        destination_name,
        driver_price,
        passenger_price
      )
    `)
    .eq("transaction_id", id)
    .maybeSingle();

  return {
    ...txn,
    user,
    booking: booking ?? null,
  } as unknown as TransactionWithBooking;
}

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
 * CASH_IN (Intech) = argent qui SORT pour Klando
 * CASH_OUT (Intech) = argent qui RENTRE pour Klando
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

  let totalIn = 0;   // Entrées Klando (CASH_OUT Intech)
  let totalOut = 0;   // Sorties Klando (CASH_IN Intech)
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
 * Marge = transactions.amount - trips.driver_price (par booking)
 * Uniquement transactions SUCCESS
 */
export async function getRevenueStats(options: {
  from?: string;
  to?: string;
} = {}): Promise<RevenueStats> {
  const { from, to } = options;
  const supabase = createServerClient();

  // Bookings avec transaction_id non null + join transaction et trip
  let query = supabase
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
    const txn = row.transaction as unknown as { id: string; amount: number | null; status: string | null; created_at: string | null } | null;
    const trip = row.trip as unknown as { driver_price: number | null } | null;

    if (!txn || txn.status !== "SUCCESS") continue;

    // Filtre par date si spécifié
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

/**
 * Transactions d'un utilisateur spécifique
 */
export async function getTransactionsForUser(userId: string) {
  return getTransactions({ userId, limit: 100 });
}
