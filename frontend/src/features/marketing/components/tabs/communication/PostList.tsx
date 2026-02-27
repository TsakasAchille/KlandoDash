"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, Sparkles, Inbox, Music, Instagram, Twitter, ChevronRight, PenLine, ImagePlus, Linkedin, MoreHorizontal
} from "lucide-react";
import { cn } from "@/lib/utils";
import { MarketingComm, CommStatus } from "@/app/marketing/types";

interface PostListProps {
  comms: MarketingComm[];
  selectedId: string | null;
  searchTerm: string;
  setSearchTerm: (val: string) => void;
  statusFilter: CommStatus | 'ALL';
  setStatusFilter: (val: CommStatus | 'ALL') => void;
  onSelect: (id: string) => void;
  onStartManual: () => void;
  onShowGenerator: () => void;
  isGeneratorActive: boolean;
}

export function PostList({
  comms,
  selectedId,
  searchTerm,
  setSearchTerm,
  statusFilter,
  setStatusFilter,
  onSelect,
  onStartManual,
  onShowGenerator,
  isGeneratorActive
}: PostListProps) {
  return (
    <div className="w-80 flex-none flex flex-col gap-4">
      <div className="space-y-3">
        <div className="flex flex-col gap-2">
          <Button 
            onClick={onStartManual}
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
              isGeneratorActive 
                ? "border-purple-600 bg-purple-50 text-purple-700 shadow-inner" 
                : "border-slate-100 text-slate-400 hover:bg-slate-50 hover:border-slate-200"
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
      </div>

      <div className="flex-1 bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden flex flex-col shadow-sm">
        <div className="p-2 border-b border-slate-100 bg-slate-50/50">
          <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)} className="w-full">
            <TabsList className="grid grid-cols-3 bg-transparent h-10 p-0 gap-1">
              <TabsTrigger value="DRAFT" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Brouillons</TabsTrigger>
              <TabsTrigger value="PUBLISHED" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Publiés</TabsTrigger>
              <TabsTrigger value="TRASH" className="text-[9px] font-black uppercase rounded-xl data-[state=active]:bg-white data-[state=active]:shadow-md">Corbeille</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
          {comms.length > 0 ? (
            comms.map((comm) => (
              <div 
                key={comm.id}
                onClick={() => onSelect(comm.id)}
                className={cn(
                  "p-4 rounded-[1.5rem] border transition-all cursor-pointer group relative overflow-hidden",
                  selectedId === comm.id 
                    ? "bg-purple-50 border-purple-200 ring-1 ring-purple-200" 
                    : "bg-white border-slate-100 hover:border-purple-200 hover:bg-slate-50 shadow-sm hover:shadow-md"
                )}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className={cn(
                    "p-1.5 rounded-lg",
                    comm.platform === 'TIKTOK' ? "bg-pink-50 text-pink-500" :
                    comm.platform === 'INSTAGRAM' ? "bg-purple-50 text-purple-500" :
                    comm.platform === 'LINKEDIN' ? "bg-blue-50 text-blue-700" :
                    comm.platform === 'OTHER' ? "bg-slate-100 text-slate-600" :
                    "bg-blue-50 text-blue-400"
                  )}>
                    {comm.platform === 'TIKTOK' && <Music className="w-3 h-3" />}
                    {comm.platform === 'INSTAGRAM' && <Instagram className="w-3 h-3" />}
                    {comm.platform === 'LINKEDIN' && <Linkedin className="w-3 h-3" />}
                    {comm.platform === 'X' && <Twitter className="w-3 h-3" />}
                    {comm.platform === 'OTHER' && <MoreHorizontal className="w-3 h-3" />}
                  </div>
                  <span className="text-[9px] font-black uppercase text-slate-400 tracking-tighter">{comm.platform}</span>
                </div>
                <p className="text-[11px] font-black text-slate-900 uppercase truncate pr-8">{comm.title}</p>
                <p className="text-[10px] text-slate-500 line-clamp-1 italic mt-1">{comm.content || "(Média uniquement)"}</p>
                
                {comm.image_url && (
                  <div className="absolute right-3 bottom-3">
                    <div className="w-8 h-8 rounded-xl border-2 border-white shadow-lg overflow-hidden">
                      <img src={comm.image_url} alt="mini" className="w-full h-full object-cover" />
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="h-60 flex flex-col items-center justify-center opacity-30 italic">
              <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                <Inbox className="w-6 h-6 text-slate-400" />
              </div>
              <p className="text-[10px] font-black uppercase tracking-widest">Aucun post trouvé</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M5 12h14"/><path d="M12 5v14"/></svg>
  )
}
