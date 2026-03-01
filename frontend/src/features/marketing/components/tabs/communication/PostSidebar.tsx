"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { CommStatus } from "@/app/marketing/types";

interface PostSidebarProps {
  statusFilter: CommStatus | 'ALL';
  setStatusFilter: (val: CommStatus | 'ALL') => void;
  onCompose: () => void;
  onShowGenerator: () => void;
  searchTerm: string;
  setSearchTerm: (val: string) => void;
}

export function PostSidebar({
  statusFilter,
  setStatusFilter,
  onCompose,
  onShowGenerator,
  searchTerm,
  setSearchTerm
}: PostSidebarProps) {
  return (
    <div className="w-full flex flex-col gap-3 shrink-0">
      <div className="flex flex-col gap-2">
        <Button
          onClick={onCompose}
          className="w-full h-14 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[10px] tracking-widest gap-3 shadow-xl shadow-purple-200 group"
        >
          <PlusIcon className="w-4 h-4 transition-transform group-hover:rotate-90" />
          Nouveau Post
        </Button>

        <Button
          variant="outline"
          onClick={onShowGenerator}
          className={cn(
            "w-full h-12 rounded-2xl font-black uppercase text-[10px] tracking-widest gap-3 border-2 transition-all",
            "border-slate-100 text-slate-400 hover:bg-slate-50 hover:border-slate-200"
          )}
        >
          <Sparkles className="w-4 h-4" /> IA Radar Inspiration
        </Button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
        <Input
          placeholder="Rechercher un post..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9 h-11 bg-white border-slate-200 rounded-xl text-[11px] font-bold uppercase tracking-tight focus:ring-purple-500/20"
        />
      </div>

      <div className="p-2 bg-white border border-slate-200 rounded-2xl">
        <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as CommStatus | 'ALL')} className="w-full">
          <TabsList className="grid grid-cols-3 bg-transparent h-10 p-0 gap-1">
            <TabsTrigger value="DRAFT" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Brouillons</TabsTrigger>
            <TabsTrigger value="PUBLISHED" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Publiés</TabsTrigger>
            <TabsTrigger value="TRASH" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Corbeille</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
    </div>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12h14"/><path d="M12 5v14"/></svg>
  );
}
