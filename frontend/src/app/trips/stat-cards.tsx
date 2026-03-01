"use client";

import { useState, useTransition } from "react";
import { MiniStatCard } from "@/components/mini-stat-card";
import { TripStats } from "@/types/trip";
import { Car, Clock, Play, CheckCircle2, XCircle, Banknote, Globe } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";

interface StatCardsProps {
  stats: TripStats;
  publicPendingCount: number;
}

export function StatCards({ stats, publicPendingCount }: StatCardsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const currentStatus = searchParams.get("status") || "all";
  const onlyPaid = searchParams.get("onlyPaid") === "true";

  const toggleFilter = (status: string | null, onlyPaid: boolean) => {
    const params = new URLSearchParams(window.location.search);
    
    if (status && status !== "all") {
        params.set("status", status);
        params.delete("onlyPaid");
    } else if (onlyPaid) {
        params.set("onlyPaid", "true");
        params.delete("status");
    } else {
        params.delete("status");
        params.delete("onlyPaid");
    }

    params.set("page", "1");
    
    startTransition(() => {
        router.push(`?${params.toString()}`, { scroll: false });
    });
  };

  return (
    <div className={cn(
        "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 transition-opacity duration-300",
        isPending ? "opacity-70 cursor-wait" : "opacity-100"
    )}>
      <MiniStatCard 
        title="Total" 
        value={stats.total_trips} 
        icon={Car} 
        color="gold"
        onClick={() => toggleFilter("all", false)}
        active={currentStatus === "all" && !onlyPaid}
      />
      <MiniStatCard 
        title="En attente" 
        value={stats.pending_trips} 
        icon={Clock} 
        color="blue"
        onClick={() => toggleFilter("PENDING", false)}
        active={currentStatus === "PENDING"}
      />
      <MiniStatCard 
        title="Actifs" 
        value={stats.active_trips} 
        icon={Play} 
        color="gold"
        onClick={() => toggleFilter("ACTIVE", false)}
        active={currentStatus === "ACTIVE"}
      />
      <MiniStatCard 
        title="Payés" 
        value={stats.paid_trips} 
        icon={Banknote} 
        color="green"
        description="Avec transactions"
        onClick={() => toggleFilter(null, true)}
        active={onlyPaid}
      />
      <MiniStatCard 
        title="Terminés" 
        value={stats.completed_trips} 
        icon={CheckCircle2} 
        color="green"
        onClick={() => toggleFilter("COMPLETED", false)}
        active={currentStatus === "COMPLETED"}
      />
      <MiniStatCard 
        title="Annulés" 
        value={stats.cancelled_trips} 
        icon={XCircle} 
        color="red"
        onClick={() => toggleFilter("CANCELLED", false)}
        active={currentStatus === "CANCELLED"}
      />
      <MiniStatCard 
        title="Visibles (Site)" 
        value={publicPendingCount} 
        icon={Globe} 
        color="blue" 
        description="En attente sur le site"
      />
    </div>
  );
}
