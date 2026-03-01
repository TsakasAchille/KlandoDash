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
        <TabsList className="bg-background/50 flex w-full md:w-auto overflow-x-auto no-scrollbar justify-start p-1 gap-1">
          <TabsTrigger value="pending" className="flex-shrink-0 data-[state=active]:bg-slate-600 data-[state=active]:text-white text-[9px] font-black uppercase px-3">
            En attente
          </TabsTrigger>
          <TabsTrigger value="ai_verified" className="flex-shrink-0 data-[state=active]:bg-klando-gold data-[state=active]:text-klando-dark text-[9px] font-black uppercase px-3">
            IA Vérifiés
          </TabsTrigger>
          <TabsTrigger value="ai_alert" className="flex-shrink-0 data-[state=active]:bg-red-600 data-[state=active]:text-white text-[9px] font-black uppercase px-3">
            Alertes IA
          </TabsTrigger>
          <TabsTrigger value="true" className="flex-shrink-0 data-[state=active]:bg-green-600 data-[state=active]:text-white text-[9px] font-black uppercase px-3">
            Validés
          </TabsTrigger>
          <TabsTrigger value="all" className="flex-shrink-0 data-[state=active]:bg-klando-burgundy data-[state=active]:text-white text-[9px] font-black uppercase px-3">
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
