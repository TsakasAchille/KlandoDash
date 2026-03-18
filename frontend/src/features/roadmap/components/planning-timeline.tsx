"use client";

import { Milestone, Calendar, ArrowRight } from "lucide-react";
import { RoadmapItem } from "../types";
import { RoadmapCard } from "./roadmap-card";

interface PlanningTimelineProps {
  items: RoadmapItem[];
  localProgress: Record<string, number>;
  updatingId: string | null;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function PlanningTimeline({ 
  items, localProgress, updatingId, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit 
}: PlanningTimelineProps) {
  
  if (items.length === 0) {
    return (
      <div className="text-center py-16 border-2 border-dashed border-white/5 rounded-3xl bg-white/[0.02]">
        <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-slate-400">Planning vide</h3>
        <p className="text-slate-500">Ajoutez des jalons pour structurer le futur de Klando.</p>
      </div>
    );
  }

  // Grouper par Phase pour créer des jalons temporels
  const phases = Array.from(new Set(items.map(i => i.phase_name))).sort();

  return (
    <div className="space-y-12 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
      {phases.map((phase, idx) => (
        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
          {/* Jalon (Milestone) */}
          <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white/10 bg-slate-900 text-klando-gold shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
            <Milestone className="w-5 h-5" />
          </div>
          
          {/* Contenu de la phase */}
          <div className="w-[calc(100%-4rem)] md:w-[45%] p-4 rounded border border-white/5 bg-white/[0.02] backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <time className="font-black text-xs uppercase tracking-widest text-klando-gold">{phase}</time>
            </div>
            <div className="grid grid-cols-1 gap-4">
              {items.filter(i => i.phase_name === phase).map(item => (
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
        </div>
      ))}
    </div>
  );
}
