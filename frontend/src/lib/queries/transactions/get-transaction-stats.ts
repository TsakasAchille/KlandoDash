import { createServerClient } from "../../supabase";
import {
  TransactionStats,
  CashFlowStats,
  RevenueStats,
} from "@/types/transaction";

/**
 * Stats agrégées des transactions
 */
export async function getTransactionsStats(): Promise<TransactionStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

  if (error || !data) {
    if (error) console.error("Erreur getTransactionsStats:", error.message);
    return { total: 0, totalAmount: 0, byStatus: {}, byType: {} };
  }

  const byStatus: Record<string, number> = {};
  const byType: Record<string, number> = {};

  (data.transactions?.byStatus || []).forEach((item: { status: string; count: number }) => {
    byStatus[item.status] = item.count;
  });

  (data.transactions?.byType || []).forEach((item: { type: string; count: number }) => {
    byType[item.type] = item.count;
  });

  return {
    total: data.transactions?.total || 0,
    totalAmount: data.transactions?.totalAmount || 0,
    byStatus,
    byType
  };
}

/**
 * Cash flow : entrées vs sorties (uniquement transactions SUCCESS)
 */
export async function getCashFlowStats(): Promise<CashFlowStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

  if (error || !data || !data.cashFlow) {
    if (error) console.error("Erreur getCashFlowStats:", error.message);
    return { totalIn: 0, totalOut: 0, solde: 0, countIn: 0, countOut: 0 };
  }

  return data.cashFlow;
}

/**
 * Revenus Klando : marge sur les bookings avec transaction
 */
export async function getRevenueStats(): Promise<RevenueStats> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc("get_klando_stats_final");

  if (error || !data || !data.revenue) {
    if (error) console.error("Erreur getRevenueStats:", error.message);
    return { totalPassengerPaid: 0, totalDriverPrice: 0, klandoMargin: 0, transactionCount: 0 };
  }

  return data.revenue;
}

