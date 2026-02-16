import { useState, useEffect, useTransition, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function useUserFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [searchTerm, setSearchTerm] = useState(searchParams.get("search") || "");
  const roleFilter = searchParams.get("role") || "all";
  const verifiedFilter = searchParams.get("verified") || "all";
  const genderFilter = searchParams.get("gender") || "all";
  const minRatingFilter = searchParams.get("minRating") || "0";
  const isNewFilter = searchParams.get("isNew") === "true";

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
      router.push(`/users?${params.toString()}`);
    });
  }, [router, searchParams]);

  const clearFilters = () => {
    setSearchTerm("");
    startTransition(() => {
      router.push("/users");
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
    roleFilter,
    verifiedFilter,
    genderFilter,
    minRatingFilter,
    isNewFilter,
    showAdvanced,
    setShowAdvanced,
    isPending,
    updateFilters,
    clearFilters,
    hasActiveFilters
  };
}
