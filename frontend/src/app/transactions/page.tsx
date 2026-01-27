import { getTransactionsWithUser, getTransactionById, getTransactionsStats, getCashFlowStats } from "@/lib/queries/transactions";
import { TransactionsPageClient } from "./transactions-client";
import { Banknote } from "lucide-react";
import { formatPrice } from "@/lib/utils";

export const dynamic = "force-dynamic";

interface Props {
  searchParams: Promise<{ selected?: string }>;
}

export default async function TransactionsPage({ searchParams }: Props) {
  const { selected } = await searchParams;

  const [transactions, stats, cashFlow, selectedTransaction] = await Promise.all([
    getTransactionsWithUser(100),
    getTransactionsStats(),
    getCashFlowStats(),
    selected ? getTransactionById(selected) : null,
  ]);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Banknote className="w-6 h-6 sm:w-8 sm:h-8 text-klando-gold" />
          <h1 className="text-2xl sm:text-3xl font-bold">Transactions</h1>
        </div>
      </div>

      {/* Stats badges */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <div className="flex flex-wrap gap-2">
          <div className="px-3 py-1 rounded-full bg-secondary">
            <span className="text-muted-foreground text-xs sm:text-sm">Total:</span>{" "}
            <span className="font-semibold text-xs sm:text-sm">{stats.total}</span>
          </div>
          <div className="px-3 py-1 rounded-full bg-klando-gold/20 text-klando-gold text-xs sm:text-sm">
            Montant: {formatPrice(stats.totalAmount)}
          </div>
          <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs sm:text-sm flex items-center gap-1">
            <span>Entrées:</span> {formatPrice(cashFlow.totalIn)}
          </div>
          <div className="px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs sm:text-sm flex items-center gap-1">
            <span>Sorties:</span> {formatPrice(cashFlow.totalOut)}
          </div>
        </div>
      </div>

      <TransactionsPageClient
        transactions={transactions}
        initialSelectedId={selected || null}
        initialSelectedTransaction={selectedTransaction}
      />
    </div>
  );
}
