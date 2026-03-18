"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { RoadmapItem } from "../types";
import { RoadmapCard } from "./roadmap-card";

interface RoadmapGridProps {
  items: RoadmapItem[];
  localProgress: Record<string, number>;
  updatingId: string | null;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function RoadmapGrid({ 
  items, localProgress, updatingId, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit 
}: RoadmapGridProps) {
  
  const phaseNames = Array.from(new Set(items.map(i => i.phase_name))).sort();
  const phases = phaseNames.map(name => {
    const phaseItems = items.filter(i => i.phase_name === name);
    return {
      name,
      timeline: phaseItems[0]?.timeline || "TBD",
      status: phaseItems.every(i => i.status === "done") ? "done" : 
              phaseItems.some(i => i.status === "in-progress") ? "in-progress" : "todo",
      items: phaseItems
    };
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {phases.map((phase, idx) => (
        <div key={idx} className="space-y-4">
          <div className="flex items-center justify-between px-2">
            <div>
              <h3 className="font-bold text-sm text-white">{phase.name}</h3>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest">{phase.timeline}</p>
            </div>
            <Badge variant="outline" className={cn(
              "text-[9px] uppercase",
              phase.status === "done" && "text-green-400 border-green-400/20 bg-green-400/5",
              phase.status === "in-progress" && "text-klando-gold border-klando-gold/20 bg-klando-gold/5"
            )}>
              {phase.status}
            </Badge>
          </div>
          <div className="space-y-4">
            {phase.items.map(item => (
              <RoadmapCard 
                key={item.id} 
                item={item} 
                currentProgress={localProgress[item.id] ?? item.progress}
                isUpdating={updatingId === item.id}
                onProgressChange={onProgressChange}
                onSetLocalProgress={onSetLocalProgress}
                onTogglePlanning={onTogglePlanning}
                onDelete={onDelete}
                onEdit={onEdit}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
