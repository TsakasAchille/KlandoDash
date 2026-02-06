"use client";

import { useState, useMemo } from "react";
import { TransactionWithUser, getCashDirection } from "@/types/transaction";
import { formatDate, formatPrice, cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronLeft, ChevronRight, ArrowUpRight, ArrowDownLeft } from "lucide-react";

interface TransactionTableProps {
  transactions: TransactionWithUser[];
  selectedTransactionId: string | null;
  initialSelectedId?: string | null;
  onSelectTransaction: (transaction: TransactionWithUser) => void;
}

const statusColors: Record<string, string> = {
  SUCCESS: "bg-green-500/20 text-green-400",
  PENDING: "bg-yellow-500/20 text-yellow-400",
  FAILED: "bg-red-500/20 text-red-400",
  CANCELLED: "bg-gray-500/20 text-gray-400",
};

const ITEMS_PER_PAGE = 10;

export function TransactionTable({
  transactions,
  selectedTransactionId,
  initialSelectedId,
  onSelectTransaction,
}: TransactionTableProps) {
  const getInitialPage = () => {
    if (!initialSelectedId) return 1;
    const index = transactions.findIndex((t) => t.id === initialSelectedId);
    if (index === -1) return 1;
    return Math.floor(index / ITEMS_PER_PAGE) + 1;
  };

  const [currentPage, setCurrentPage] = useState(getInitialPage);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [directionFilter, setDirectionFilter] = useState<string>("all");

  // Filter transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter((txn) => {
      if (statusFilter !== "all" && txn.status !== statusFilter) return false;
      if (directionFilter !== "all") {
        const dir = getCashDirection(txn.code_service);
        if (directionFilter === "in" && dir !== "CASH_OUT") return false;
        if (directionFilter === "out" && dir !== "CASH_IN") return false;
      }
      return true;
    });
  }, [transactions, statusFilter, directionFilter]);

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedTransactions = filteredTransactions.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // Get unique statuses
  const statuses = useMemo(() => {
    const unique = Array.from(new Set(transactions.map((t) => t.status).filter(Boolean)));
    return unique.sort();
  }, [transactions]);

  const handleFilterChange = (type: "status" | "direction", value: string) => {
    if (type === "status") setStatusFilter(value);
    else setDirectionFilter(value);
    setCurrentPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <Select value={statusFilter} onValueChange={(v) => handleFilterChange("status", v)}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Statut" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous</SelectItem>
            {statuses.map((status) => (
              <SelectItem key={status} value={status!}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={directionFilter} onValueChange={(v) => handleFilterChange("direction", v)}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Direction" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tout</SelectItem>
            <SelectItem value="in">Entrées</SelectItem>
            <SelectItem value="out">Sorties</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {filteredTransactions.length} transaction{filteredTransactions.length > 1 ? "s" : ""}
        </span>
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-card overflow-x-auto lg:overflow-visible">
        <div className="min-w-[500px] lg:min-w-0">
          <Table>
                        <TableHeader>
                          <TableRow className="bg-klando-dark hover:bg-klando-dark">
                            <TableHead className="text-klando-gold w-8"></TableHead>
                            <TableHead className="text-klando-gold">Utilisateur</TableHead>
                            <TableHead className="text-klando-gold">Montant</TableHead>
                            <TableHead className="text-klando-gold hidden sm:table-cell">Type</TableHead>
                            <TableHead className="text-klando-gold">Statut</TableHead>
                            <TableHead className="text-klando-gold hidden md:table-cell">Date</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {paginatedTransactions.length === 0 ? (
                            <TableRow>
                              <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                                Aucune transaction trouvée
                              </TableCell>
                            </TableRow>
                          ) : (
                            paginatedTransactions.map((txn) => {
                              const direction = getCashDirection(txn.code_service);
                              return (
                                <TableRow
                                  key={txn.id}
                                  data-transaction-id={txn.id}
                                  data-state={selectedTransactionId === txn.id ? "selected" : undefined}
                                  className="cursor-pointer transition-all"
                                  onClick={() => onSelectTransaction(txn)}
                                >
                                  <TableCell className="w-8 px-2 sm:px-4">
                                    {direction === "CASH_OUT" ? (
                                      <ArrowDownLeft className="w-4 h-4 text-green-400" />
                                    ) : direction === "CASH_IN" ? (
                                      <ArrowUpRight className="w-4 h-4 text-red-400" />
                                    ) : (
                                      <span className="w-4 h-4 inline-block" />
                                    )}
                                  </TableCell>
                                  <TableCell className="px-2 sm:px-4">
                                    <div className="flex flex-col min-w-0">
                                      <span className="font-medium truncate max-w-[100px] sm:max-w-[150px]">
                                        {txn.user?.display_name || "Inconnu"}
                                      </span>
                                      <span className="text-muted-foreground text-[10px] sm:text-xs truncate max-w-[100px] sm:max-w-[150px]">
                                        {txn.phone || "-"}
                                      </span>
                                      {/* Date visible seulement sur mobile ici */}
                                      <span className="text-[10px] text-muted-foreground md:hidden mt-0.5">
                                        {txn.created_at ? formatDate(txn.created_at) : "-"}
                                      </span>
                                    </div>
                                  </TableCell>
                                  <TableCell className={cn(
                                    "font-semibold text-sm sm:text-base px-2 sm:px-4",
                                    direction === "CASH_OUT" ? "text-green-400" : direction === "CASH_IN" ? "text-red-400" : ""
                                  )}>
                                    {direction === "CASH_OUT" ? "+" : direction === "CASH_IN" ? "-" : ""}
                                    {formatPrice(txn.amount ?? 0)}
                                  </TableCell>
                                  <TableCell className="hidden sm:table-cell">
                                    <span className="text-xs">{txn.type || "-"}</span>
                                  </TableCell>
                                  <TableCell className="px-2 sm:px-4">
                                    <span
                                      className={cn(
                                        "px-2 py-1 rounded-full text-[10px] sm:text-xs font-medium whitespace-nowrap",
                                        statusColors[txn.status || ""] || "bg-gray-500/20 text-gray-400"
                                      )}
                                    >
                                      {txn.status || "-"}
                                    </span>
                                  </TableCell>
                                  <TableCell className="hidden md:table-cell text-sm">
                                    {txn.created_at ? formatDate(txn.created_at) : "-"}
                                  </TableCell>
                                </TableRow>
                              );
                            })
                          )}
                        </TableBody>          </Table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            Page {currentPage} sur {totalPages}
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
