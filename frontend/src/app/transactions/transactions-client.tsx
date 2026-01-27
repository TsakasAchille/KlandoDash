"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { TransactionWithUser, TransactionWithBooking } from "@/types/transaction";
import { TransactionTable } from "@/components/transactions/transaction-table";
import { TransactionDetails } from "@/components/transactions/transaction-details";

interface TransactionsPageClientProps {
  transactions: TransactionWithUser[];
  initialSelectedId: string | null;
  initialSelectedTransaction: TransactionWithBooking | null;
}

function scrollToRow(id: string) {
  const element = document.querySelector(`[data-transaction-id="${id}"]`);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "center" });
    element.classList.add("ring-2", "ring-klando-gold");
    setTimeout(() => {
      element.classList.remove("ring-2", "ring-klando-gold");
    }, 2000);
  }
}

export function TransactionsPageClient({
  transactions,
  initialSelectedId,
  initialSelectedTransaction,
}: TransactionsPageClientProps) {
  const router = useRouter();
  const [selectedTransaction, setSelectedTransaction] = useState<TransactionWithBooking | null>(
    initialSelectedTransaction
  );

  const handleSelectTransaction = useCallback(
    (transaction: TransactionWithUser) => {
      router.replace(`/transactions?selected=${transaction.id}`, { scroll: false });
    },
    [router]
  );

  useEffect(() => {
    if (initialSelectedId) {
      setTimeout(() => scrollToRow(initialSelectedId), 100);
    }
  }, [initialSelectedId]);

  useEffect(() => {
    setSelectedTransaction(initialSelectedTransaction);
  }, [initialSelectedTransaction]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Table - 1/3 width on large screens */}
      <div className="lg:col-span-1 min-w-0">
        <TransactionTable
          transactions={transactions}
          selectedTransactionId={selectedTransaction?.id || null}
          initialSelectedId={initialSelectedId}
          onSelectTransaction={handleSelectTransaction}
        />
      </div>

      {/* Details - 2/3 width on large screens */}
      <div className="lg:col-span-2">
        {selectedTransaction ? (
          <TransactionDetails transaction={selectedTransaction} />
        ) : (
          <div className="flex items-center justify-center h-64 rounded-lg border border-dashed border-border">
            <p className="text-muted-foreground">
              Sélectionnez une transaction pour voir les détails
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
