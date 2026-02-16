"use client";

import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface ValidationFiltersProps {
  currentStatus: string;
  currentPage: number;
  totalPages: number;
  onUpdateFilters: (status: string, page?: number) => void;
}

export function ValidationFilters({
  currentStatus,
  currentPage,
  totalPages,
  onUpdateFilters
}: ValidationFiltersProps) {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-muted/30 p-2 rounded-xl border border-border/50">
      <Tabs value={currentStatus} onValueChange={(val) => onUpdateFilters(val)} className="w-full md:w-auto">
        <TabsList className="bg-background/50 grid grid-cols-3 w-full md:w-[400px]">
          <TabsTrigger value="pending" className="data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark">
            En attente
          </TabsTrigger>
          <TabsTrigger value="true" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">
            Validés
          </TabsTrigger>
          <TabsTrigger value="all" className="data-[state=active]:bg-klando-burgundy data-[state=active]:text-white">
            Tous
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {totalPages > 1 && (
        <div className="flex items-center gap-2 px-2">
          <span className="text-[10px] uppercase font-black tracking-widest text-muted-foreground mr-2">
            Page {currentPage} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={currentPage <= 1}
            onClick={() => onUpdateFilters(currentStatus, currentPage - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={currentPage >= totalPages}
            onClick={() => onUpdateFilters(currentStatus, currentPage + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
