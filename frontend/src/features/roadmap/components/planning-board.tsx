"use client";

import { Calendar, MoreHorizontal, ArrowRight, Star } from "lucide-react";
import { RoadmapItem, STAGE_CONFIG, PlanningStage } from "../types";
import { RoadmapCard } from "./roadmap-card";
import { cn } from "@/lib/utils";

interface PlanningBoardProps {
  items: RoadmapItem[];
  localProgress: Record<string, number>;
  updatingId: string | null;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function PlanningBoard({ 
  items, localProgress, updatingId, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit 
}: PlanningBoardProps) {
  
  const stages: PlanningStage[] = ['now', 'next', 'later', 'backlog'];

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent snap-x">
        {stages.map((stage) => {
          const stageItems = items.filter(i => i.planning_stage === stage);
          const config = STAGE_CONFIG[stage];

          return (
            <div key={stage} className="flex-none w-80 min-h-[500px] flex flex-col snap-start">
              {/* Board Header */}
              <div className={cn(
                "p-4 rounded-2xl border mb-4 flex flex-col gap-1 backdrop-blur-md",
                config.color
              )}>
                <div className="flex items-center justify-between">
                  <span className="font-black text-xs uppercase tracking-[0.2em]">{config.label}</span>
                  <Badge className="bg-white/10 hover:bg-white/20 text-[10px] h-5 min-w-[20px] justify-center">
                    {stageItems.length}
                  </Badge>
                </div>
                <p className="text-[10px] font-medium opacity-70 italic">{config.desc}</p>
              </div>

              {/* Column Content */}
              <div className="flex-1 space-y-4 rounded-2xl bg-white/[0.02] border border-white/5 p-3 min-h-[100px]">
                {stageItems.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-40 opacity-20 border-2 border-dashed border-white/10 rounded-xl m-2">
                    <MoreHorizontal className="w-8 h-8" />
                  </div>
                ) : (
                  stageItems.map(item => (
                    <div key={item.id} className="relative group">
                      {/* Milestone visual link if has date */}
                      {item.target_date && (
                        <div className="absolute -left-1 top-4 w-2 h-2 rounded-full bg-klando-gold animate-pulse z-10 shadow-[0_0_10px_rgba(235,195,63,0.5)]" title="Jalon fixé" />
                      )}
                      
                      <RoadmapCard 
                        item={item} 
                        currentProgress={localProgress[item.id] ?? item.progress}
                        isUpdating={updatingId === item.id}
                        onProgressChange={onProgressChange}
                        onSetLocalProgress={onSetLocalProgress}
                        onTogglePlanning={onTogglePlanning}
                        onDelete={onDelete}
                        onEdit={onEdit}
                      />

                      {item.target_date && (
                        <div className="mt-1 px-3 py-1 bg-klando-gold/10 rounded-lg flex items-center gap-2 text-[9px] font-black text-klando-gold uppercase tracking-widest border border-klando-gold/5">
                          <Star className="w-3 h-3" />
                          Jalon: {new Date(item.target_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Badge({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={cn("inline-flex items-center rounded-full border px-2 py-0.5 font-bold transition-colors", className)}>
      {children}
    </div>
  );
}
