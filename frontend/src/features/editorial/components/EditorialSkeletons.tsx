"use client";

import { Skeleton } from "@/components/ui/skeleton";

export function DualPaneSkeleton() {
  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-250px)] min-h-[600px] w-full animate-in fade-in duration-500">
      {/* SIDEBAR SKELETON */}
      <div className="w-full lg:w-[320px] shrink-0 flex flex-col gap-4">
        <div className="space-y-2">
          <Skeleton className="h-14 w-full rounded-2xl" />
          <Skeleton className="h-11 w-full rounded-xl" />
        </div>
        <div className="flex-1 bg-white/50 border border-slate-100 rounded-[2.5rem] p-4 space-y-4">
          <Skeleton className="h-8 w-1/2 rounded-lg mx-auto" />
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-[110px] w-full rounded-[1.5rem]" />
          ))}
        </div>
      </div>

      {/* WORKSPACE SKELETON */}
      <div className="flex-1 bg-white/30 border border-slate-100 rounded-[2.5rem] p-8 space-y-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Skeleton className="h-12 w-12 rounded-xl" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>
          <Skeleton className="h-9 w-24 rounded-full" />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-[300px] w-full rounded-2xl" />
            <Skeleton className="h-20 w-full rounded-xl" />
          </div>
          <div className="space-y-4">
            <Skeleton className="aspect-square w-full rounded-[2rem]" />
            <Skeleton className="h-20 w-full rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function CalendarSkeleton() {
  return (
    <div className="w-full h-[calc(100vh-250px)] min-h-[600px] bg-white/50 border border-slate-100 rounded-[2.5rem] p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <Skeleton className="h-10 w-48 rounded-xl" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-10 rounded-lg" />
          <Skeleton className="h-10 w-10 rounded-lg" />
        </div>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-full rounded-md" />
        ))}
      </div>
      <div className="grid grid-cols-7 grid-rows-5 gap-2 flex-1">
        {Array.from({ length: 35 }).map((_, i) => (
          <Skeleton key={i} className="min-h-[100px] w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}
