import { createServerClient } from "../../supabase";
import { TransactionListItem, TransactionWithUser } from "@/types/transaction";

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

  const userIds = Array.from(new Set(transactions.map(t => t.user_id).filter(Boolean)));

  const { data: users } = await supabase
    .from("users")
    .select("uid, display_name, phone_number")
    .in("uid", userIds);

  const userMap = new Map(users?.map(u => [u.uid, u]) || []);

  return transactions.map(t => ({
    ...t,
    user: userMap.get(t.user_id) ? {
      display_name: userMap.get(t.user_id)!.display_name,
      phone: userMap.get(t.user_id)!.phone_number,
    } : null,
  })) as unknown as TransactionWithUser[];
}

/**
 * Transactions d'un utilisateur spécifique
 */
export async function getTransactionsForUser(userId: string) {
  return getTransactions({ userId, limit: 100 });
}
