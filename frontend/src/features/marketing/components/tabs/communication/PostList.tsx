"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, PlusCircle, Sparkles, Inbox, Music, Instagram, Twitter
} from "lucide-react";
import { cn } from "@/lib/utils";
import { MarketingComm, CommStatus } from "../../../types";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Type, ImagePlus } from "lucide-react";

interface PostListProps {
  comms: MarketingComm[];
  selectedId: string | null;
  searchTerm: string;
  setSearchTerm: (val: string) => void;
  statusFilter: CommStatus | 'ALL';
  setStatusFilter: (val: CommStatus | 'ALL') => void;
  onSelect: (id: string) => void;
  onStartManual: (mode: 'TEXT' | 'IMAGE') => void;
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
    <div className="w-80 flex flex-col gap-4">
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button className="h-12 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[9px] tracking-widest gap-2 shadow-lg shadow-purple-200">
                <PlusCircle className="w-3.5 h-3.5" /> Créer
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-56 p-2 rounded-2xl border-slate-200 shadow-2xl" align="start">
              <div className="space-y-1">
                <button 
                  onClick={() => onStartManual('TEXT')}
                  className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors group text-left"
                >
                  <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                    <Type className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-[10px] font-black uppercase text-slate-900 leading-tight">Post Standard</p>
                    <p className="text-[8px] font-bold text-slate-400 uppercase tracking-tight">Texte prioritaire</p>
                  </div>
                </button>
                <button 
                  onClick={() => onStartManual('IMAGE')}
                  className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors group text-left"
                >
                  <div className="p-2 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
                    <ImagePlus className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-[10px] font-black uppercase text-slate-900 leading-tight">Post Visuel</p>
                    <p className="text-[8px] font-bold text-slate-400 uppercase tracking-tight">Image / PNG Star</p>
                  </div>
                </button>
              </div>
            </PopoverContent>
          </Popover>

          <Button 
            variant="outline"
            onClick={onShowGenerator}
            className={cn(
              "h-12 rounded-2xl font-black uppercase text-[9px] tracking-widest gap-2 border-2",
              isGeneratorActive ? "border-purple-600 bg-purple-50 text-purple-700" : "border-slate-100 text-slate-400 hover:bg-slate-50"
            )}
          >
            <Sparkles className="w-3.5 h-3.5" /> IA Radar
          </Button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <Input 
            placeholder="Rechercher..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-10 bg-white border-slate-200 rounded-xl text-[11px] font-bold uppercase tracking-tight focus:ring-purple-500/20"
          />
        </div>
      </div>

      <div className="flex-1 bg-white border border-slate-200 rounded-[2rem] overflow-hidden flex flex-col shadow-sm">
        <div className="p-2 border-b border-slate-100 bg-slate-50/50">
          <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as any)} className="w-full">
            <TabsList className="grid grid-cols-3 bg-transparent h-8 p-0 gap-1">
              <TabsTrigger value="DRAFT" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Brouillons</TabsTrigger>
              <TabsTrigger value="PUBLISHED" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Publiés</TabsTrigger>
              <TabsTrigger value="TRASH" className="text-[8px] font-black uppercase rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">Corbeille</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
          {comms.length > 0 ? (
            comms.map((comm) => (
              <div 
                key={comm.id}
                onClick={() => onSelect(comm.id)}
                className={cn(
                  "p-3 rounded-2xl border transition-all cursor-pointer group relative overflow-hidden",
                  selectedId === comm.id 
                    ? "bg-purple-50 border-purple-200 ring-1 ring-purple-200" 
                    : "bg-white border-slate-100 hover:border-purple-200 hover:bg-slate-50"
                )}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  {comm.platform === 'TIKTOK' && <Music className="w-3 h-3 text-pink-500" />}
                  {comm.platform === 'INSTAGRAM' && <Instagram className="w-3 h-3 text-purple-500" />}
                  {comm.platform === 'X' && <Twitter className="w-3 h-3 text-blue-400" />}
                  <span className="text-[8px] font-black uppercase text-slate-400">{comm.platform}</span>
                </div>
                <p className="text-[10px] font-black text-slate-900 uppercase truncate">{comm.title}</p>
                <p className="text-[9px] text-slate-500 line-clamp-1 italic mt-0.5">{comm.content || "(Visuel PNG)"}</p>
                
                {comm.image_url && (
                  <div className="absolute right-2 bottom-2">
                    <div className="w-6 h-6 rounded-lg border border-white shadow-sm overflow-hidden">
                      <img src={comm.image_url} alt="mini" className="w-full h-full object-cover" />
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="h-40 flex flex-col items-center justify-center opacity-20 italic">
              <Inbox className="w-8 h-8 mb-2" />
              <p className="text-[9px] font-black uppercase">Aucun post</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
