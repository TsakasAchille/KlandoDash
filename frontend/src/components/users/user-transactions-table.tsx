"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { TransactionListItem, getCashDirection } from "@/types/transaction";
import { formatDate, formatPrice, cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { ChevronLeft, ChevronRight, ExternalLink, ArrowUpRight, ArrowDownLeft, Loader2 } from "lucide-react";

interface UserTransactionsTableProps {
  userId: string;
}

const statusColors: Record<string, string> = {
  SUCCESS: "text-green-500",
  PENDING: "text-yellow-500",
  FAILED: "text-red-500",
};

export function UserTransactionsTable({ userId }: UserTransactionsTableProps) {
  const [transactions, setTransactions] = useState<TransactionListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const limit = 5;

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}/transactions?page=${page}&limit=${limit}`)
      .then((res) => res.json())
      .then((data) => {
        setTransactions(data.transactions || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => {
        setTransactions([]);
        setTotal(0);
        setLoading(false);
      });
  }, [userId, page]);

  useEffect(() => {
    setPage(1);
  }, [userId]);

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-klando-gold" />
      </div>
    );
  }

  return (
    <div className="bg-card">
      {transactions.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-muted-foreground text-xs font-medium">Aucune transaction enregistrée</p>
        </div>
      ) : (
        <div className="divide-y divide-border/10">
          <Table>
            <TableBody>
              {transactions.map((txn) => {
                const direction = getCashDirection(txn.code_service);
                return (
                  <TableRow key={txn.id} className="hover:bg-muted/5 border-none">
                    <TableCell className="py-2 px-4 w-6">
                      {direction === "CASH_OUT" ? (
                        <ArrowDownLeft className="w-3.5 h-3.5 text-green-500" />
                      ) : direction === "CASH_IN" ? (
                        <ArrowUpRight className="w-3.5 h-3.5 text-red-500" />
                      ) : (
                        <span className="w-3.5 h-3.5 inline-block" />
                      )}
                    </TableCell>
                    <TableCell className="py-2 px-0">
                      <div className="flex items-center gap-2">
                        <span className={cn(
                          "text-[11px] font-black font-mono",
                          direction === "CASH_OUT" ? "text-green-500" :
                          direction === "CASH_IN" ? "text-red-500" : ""
                        )}>
                          {direction === "CASH_OUT" ? "+" : direction === "CASH_IN" ? "-" : ""}
                          {formatPrice(txn.amount ?? 0)}
                        </span>
                        <span className={cn("text-[9px] font-black px-1 rounded bg-secondary", statusColors[txn.status || ""] || "text-muted-foreground")}>
                          {txn.status}
                        </span>
                      </div>
                      <div className="text-[10px] text-muted-foreground font-medium">
                        {txn.type || "-"} · {txn.created_at ? formatDate(txn.created_at) : "-"}
                      </div>
                    </TableCell>
                    <TableCell className="text-right py-2 px-4">
                      <Link href={`/transactions?selected=${txn.id}`}>
                        <Button
                          variant="ghost"
                          className="h-7 w-7 p-0 hover:bg-klando-gold/10 hover:text-klando-gold transition-colors"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-2 bg-muted/5">
              <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">
                {page} / {totalPages}
              </span>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                >
                  <ChevronRight className="w-3 h-3" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
