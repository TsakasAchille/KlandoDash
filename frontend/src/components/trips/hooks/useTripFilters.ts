import { useState, useEffect, useTransition, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function useTripFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");
  const statusFilter = searchParams.get("status") || "all";
  const maxPriceFilter = searchParams.get("maxPrice") || "";

  const updateFilters = useCallback((newParams: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString());
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === "all" || value === "" || value === "0" || value === "false") {
        params.delete(key);
      } else {
        params.set(key, value);
      }
    });

    if (!newParams.page && newParams.page !== undefined) {
      params.delete("page");
    }

    startTransition(() => {
      router.push(`/trips?${params.toString()}`);
    });
  }, [router, searchParams]);

  const clearFilters = () => {
    setSearchTerm("");
    startTransition(() => {
      router.push("/trips");
    });
  };

  const hasActiveFilters = searchParams.toString().length > 0 && !searchParams.has("selected");

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== (searchParams.get("search") || "")) {
        updateFilters({ search: searchTerm, page: "1" });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, updateFilters, searchParams]);

  return {
    searchTerm,
    setSearchTerm,
    statusFilter,
    maxPriceFilter,
    showAdvanced,
    setShowAdvanced,
    isPending,
    updateFilters,
    clearFilters,
    hasActiveFilters
  };
}
