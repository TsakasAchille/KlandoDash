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
    <div className="max-w-[1600px] mx-auto space-y-8 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black tracking-tight uppercase flex items-center gap-3">
            <Banknote className="w-8 h-8 text-klando-gold" />
            Transactions
          </h1>
          <p className="text-sm text-muted-foreground font-medium">
            Flux financiers et comptabilité
          </p>
        </div>
        <RefreshButton />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MiniStatCard 
          title="Total" 
          value={stats.total} 
          icon={Wallet} 
          color="gold" 
        />
        <MiniStatCard 
          title="Montant Total" 
          value={formatPrice(stats.totalAmount)} 
          icon={Banknote} 
          color="blue" 
        />
        <MiniStatCard 
          title="Entrées" 
          value={formatPrice(cashFlow.totalIn)} 
          icon={ArrowDownLeft} 
          color="green" 
        />
        <MiniStatCard 
          title="Sorties" 
          value={formatPrice(cashFlow.totalOut)} 
          icon={ArrowUpRight} 
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