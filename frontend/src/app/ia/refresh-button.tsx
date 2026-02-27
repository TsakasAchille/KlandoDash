"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { RefreshCw } from "lucide-react";

export function RefreshButton() {
  const router = useRouter();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    router.refresh();
    // Simulate some delay to show the animation
    setTimeout(() => {
      setIsRefreshing(false);
    }, 1000);
  };

  return (
    <button
      onClick={handleRefresh}
      disabled={isRefreshing}
      className={`p-2 rounded-lg bg-klando-burgundy text-white hover:bg-klando-burgundy/90 transition-all flex items-center gap-2 ${
        isRefreshing ? "opacity-50 cursor-not-allowed" : ""
      }`}
    >
      <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
      <span>Actualiser les données</span>
    </button>
  );
}
