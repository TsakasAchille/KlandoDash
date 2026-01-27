"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { TransactionListItem, getCashDirection } from "@/types/transaction";
import { formatDate, formatPrice, cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { ChevronLeft, ChevronRight, ExternalLink, Banknote, ArrowUpRight, ArrowDownLeft } from "lucide-react";

interface UserTransactionsTableProps {
  userId: string;
}

const statusColors: Record<string, string> = {
  SUCCESS: "text-green-400",
  PENDING: "text-yellow-400",
  FAILED: "text-red-400",
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

  // Reset page when user changes
  useEffect(() => {
    setPage(1);
  }, [userId]);

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Banknote className="w-5 h-5 text-klando-gold" />
            Transactions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 bg-secondary rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Banknote className="w-5 h-5 text-klando-gold" />
          Transactions ({total})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <p className="text-muted-foreground text-sm">Aucune transaction</p>
        ) : (
          <>
            <Table>
              <TableBody>
                {transactions.map((txn) => {
                  const direction = getCashDirection(txn.code_service);
                  return (
                    <TableRow key={txn.id}>
                      <TableCell className="py-2 w-8">
                        {direction === "CASH_OUT" ? (
                          <ArrowDownLeft className="w-4 h-4 text-green-400" />
                        ) : direction === "CASH_IN" ? (
                          <ArrowUpRight className="w-4 h-4 text-red-400" />
                        ) : (
                          <span className="w-4 h-4 inline-block" />
                        )}
                      </TableCell>
                      <TableCell className="py-2">
                        <div className="text-sm">
                          <span className={cn(
                            "font-semibold",
                            direction === "CASH_OUT" ? "text-green-400" :
                            direction === "CASH_IN" ? "text-red-400" : ""
                          )}>
                            {direction === "CASH_OUT" ? "+" : direction === "CASH_IN" ? "-" : ""}
                            {formatPrice(txn.amount ?? 0)}
                          </span>
                          <span className={cn("ml-2 text-xs", statusColors[txn.status || ""] || "text-muted-foreground")}>
                            {txn.status}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {txn.type || "-"} · {txn.created_at ? formatDate(txn.created_at) : "-"}
                        </div>
                      </TableCell>
                      <TableCell className="text-right py-2">
                        <Link href={`/transactions?selected=${txn.id}`}>
                          <Button
                            variant="ghost"
                            className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px] px-3 sm:px-2"
                            size="sm"
                          >
                            <ExternalLink className="w-4 h-4 sm:w-4 sm:h-4" />
                            <span className="hidden sm:inline ml-2">Voir</span>
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>

            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mt-4">
                <Button
                  variant="outline"
                  className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px]"
                  size="sm"
                  onClick={() => setPage((p) => p - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span className="hidden sm:inline ml-2">Précédent</span>
                </Button>
                <span className="text-sm text-muted-foreground text-center">
                  {page} / {totalPages}
                </span>
                <Button
                  variant="outline"
                  className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px]"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= totalPages}
                >
                  <span className="hidden sm:inline mr-2">Suivant</span>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
