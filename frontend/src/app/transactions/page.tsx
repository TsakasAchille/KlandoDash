import { getTransactionsWithUser, getTransactionById, getTransactionsStats, getCashFlowStats } from "@/lib/queries/transactions";
import { TransactionsPageClient } from "./transactions-client";
import { Banknote, ArrowUpRight, ArrowDownLeft, Wallet } from "lucide-react";
import { formatPrice } from "@/lib/utils";
import { RefreshButton } from "@/components/refresh-button";
import { MiniStatCard } from "@/components/mini-stat-card";

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
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8 pt-4 relative">
      {/* Action Bar Floating */}
      <div className="absolute top-4 right-8 z-10">
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total} 
          icon="Wallet" 
          color="gold" 
        />
        <MiniStatCard 
          title="Montant Total" 
          value={formatPrice(stats.totalAmount)} 
          icon="Banknote" 
          color="blue" 
        />
        <MiniStatCard 
          title="Entrées" 
          value={formatPrice(cashFlow.totalIn)} 
          icon="ArrowDownLeft" 
          color="green" 
        />
        <MiniStatCard 
          title="Sorties" 
          value={formatPrice(cashFlow.totalOut)} 
          icon="ArrowUpRight" 
          color="red" 
        />
      </div>

      <TransactionsPageClient
        transactions={transactions}
        initialSelectedId={selected || null}
        initialSelectedTransaction={selectedTransaction}
      />
    </div>
  );
}