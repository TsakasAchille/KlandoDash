"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export function RefreshButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    startTransition(() => {
      router.refresh();
      // On laisse l'animation un peu plus longtemps pour le feedback visuel
      setTimeout(() => setIsRefreshing(false), 500);
    });
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleRefresh}
      disabled={isRefreshing || isPending}
      className="flex items-center gap-2"
    >
      <RefreshCw 
        className={cn(
          "w-4 h-4", 
          (isRefreshing || isPending) && "animate-spin"
        )} 
      />
      <span>Rafraîchir</span>
    </Button>
  );
}
