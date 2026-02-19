import { useState, useEffect, useTransition, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export function useUserFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const isInternalUpdate = useRef(false);

  // Initialiser searchTerm depuis l'URL une seule fois au montage
  const [searchTerm, setSearchTerm] = useState(() => searchParams.get("search") || "");
  
  const roleFilter = searchParams.get("role") || "all";
  const verifiedFilter = searchParams.get("verified") || "all";
  const genderFilter = searchParams.get("gender") || "all";
  const minRatingFilter = searchParams.get("minRating") || "0";
  const isNewFilter = searchParams.get("isNew") === "true";

  // Sync local search term with URL only if changed externally (e.g. Back button)
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    if (urlSearch !== searchTerm && !isPending && !isInternalUpdate.current) {
      setSearchTerm(urlSearch);
    }
    
    // Reset internal flag after sync or if pending is finished
    if (!isPending) {
      isInternalUpdate.current = false;
    }
  }, [searchParams, isPending, searchTerm]);

  const updateFilters = useCallback((newParams: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString());
    
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === "all" || value === "" || value === "0" || value === "false") {
        params.delete(key);
      } else {
        params.set(key, value);
      }
    });

    // If we are changing filters (not just page), reset to page 1
    if (newParams.page === undefined && !newParams.hasOwnProperty('page')) {
      params.delete("page");
    }

    const newUrl = `/users?${params.toString()}`;
    if (`/users?${searchParams.toString()}` === newUrl) return;

    isInternalUpdate.current = true;
    startTransition(() => {
      router.push(newUrl);
    });
  }, [router, searchParams]);

  const clearFilters = () => {
    setSearchTerm("");
    isInternalUpdate.current = true;
    startTransition(() => {
      router.push("/users");
    });
  };

  const hasActiveFilters = searchParams.toString().length > 0 && !searchParams.has("selected");

  // Debounced search update
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    if (searchTerm === urlSearch) return;

    const timer = setTimeout(() => {
      updateFilters({ search: searchTerm, page: "1" });
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, updateFilters, searchParams]);

  return {
    searchTerm,
    setSearchTerm: (val: string) => {
      isInternalUpdate.current = true;
      setSearchTerm(val);
    },
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
