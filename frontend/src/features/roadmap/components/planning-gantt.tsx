"use client";

import { useMemo, useEffect } from "react";
import { Calendar, MoreHorizontal, GripVertical, Plus } from "lucide-react";
import { RoadmapItem, STAGE_CONFIG } from "../types";
import { RoadmapCard } from "./roadmap-card";
import { cn } from "@/lib/utils";
import { useGanttInteraction } from "../use-gantt-interaction";
import { updateRoadmapItem } from "@/app/admin/roadmap/actions";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

interface PlanningGanttProps {
  items: RoadmapItem[];
  localProgress: Record<string, number>;
  updatingId: string | null;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function PlanningGantt({ 
  items, localProgress, updatingId, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit 
}: PlanningGanttProps) {
  
  // Générer les 12 prochaines semaines
  const timelineWeeks = useMemo(() => {
    const weeks = [];
    const today = new Date();
    // On commence au début de la semaine actuelle (Lundi)
    const startOfWeek = new Date(today.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1)));
    
    for (let i = 0; i < 12; i++) {
      const d = new Date(startOfWeek.getTime() + i * 7 * 86400000);
      weeks.push(d);
    }
    return weeks;
  }, []);

  const timelineStart = timelineWeeks[0].getTime();
  const timelineEnd = new Date(timelineWeeks[11].getTime() + 7 * 86400000).getTime();
  const timelineDuration = timelineEnd - timelineStart;

  const { containerRef, interaction, startInteraction, handleMouseMove, handleMouseUp, calculateNewDates } = useGanttInteraction(
    timelineStart,
    timelineDuration,
    async (id, data) => {
      const result = await updateRoadmapItem(id, data);
      if (result.success) toast.success("Planification mise à jour");
      else toast.error("Erreur de mise à jour");
    }
  );

  useEffect(() => {
    if (interaction) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [interaction, handleMouseMove, handleMouseUp]);

  const getPositionStyles = (startDateStr: string | null, endDateStr: string | null, itemId?: string) => {
    let startStr = startDateStr;
    let endStr = endDateStr;

    if (interaction && interaction.itemId === itemId) {
      const newDates = calculateNewDates(interaction);
      if (newDates) {
        startStr = newDates.start_date;
        endStr = newDates.target_date;
      }
    }

    if (!startStr || !endStr) return null;
    const start = new Date(startStr).getTime();
    const end = new Date(endStr).getTime();
    
    if (end < timelineStart || start > timelineEnd) return null;
    
    const visibleStart = Math.max(start, timelineStart);
    const visibleEnd = Math.min(end, timelineEnd);
    const left = ((visibleStart - timelineStart) / timelineDuration) * 100;
    const width = ((visibleEnd - visibleStart) / timelineDuration) * 100;
    
    return { left: `${left}%`, width: `${Math.max(width, 1)}%`, isCutStart: start < timelineStart, isCutEnd: end > timelineEnd };
  };

  const scheduledItems = items.filter(i => i.start_date && i.target_date).sort((a, b) => new Date(a.start_date!).getTime() - new Date(b.start_date!).getTime());
  const unscheduledItems = items.filter(i => !i.start_date || !i.target_date);

  const handleQuickPlan = async (item: RoadmapItem) => {
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 86400000);
    const result = await updateRoadmapItem(item.id, {
      start_date: today.toISOString().split('T')[0],
      target_date: nextWeek.toISOString().split('T')[0]
    });
    if (result.success) toast.success("Tâche ajoutée au planning");
  };

  // Calcul du numéro de semaine ISO
  const getWeekNumber = (d: Date) => {
    const date = new Date(d.getTime());
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
    const week1 = new Date(date.getFullYear(), 0, 4);
    return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
  };

  return (
    <div className="flex flex-col h-full space-y-6 select-none">
      <div className="rounded-2xl border border-white/10 bg-slate-900/50 overflow-hidden flex flex-col shadow-2xl">
        {/* En-tête des semaines */}
        <div className="flex border-b border-white/10 bg-white/5">
          <div className="w-48 lg:w-64 shrink-0 p-3 border-r border-white/10 font-black text-[10px] uppercase tracking-widest text-slate-400">
            Chronologie (12w)
          </div>
          <div className="flex-1 flex" ref={containerRef}>
            {timelineWeeks.map((week, i) => (
              <div key={i} className="flex-1 p-2 text-center border-l border-white/5 first:border-l-0">
                <div className="text-[9px] font-black text-klando-gold uppercase">W{getWeekNumber(week)}</div>
                <div className="text-[7px] font-bold text-slate-500 uppercase">{week.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto relative min-h-[400px]">
          {/* Traits verticaux pour chaque semaine avec Zebra striping */}
          <div className="absolute inset-0 left-48 lg:left-64 flex pointer-events-none h-full">
            {timelineWeeks.map((_, i) => (
              <div 
                key={i} 
                className={cn(
                  "flex-1 border-l border-white/[0.08] h-full",
                  i % 2 === 0 ? "bg-white/[0.01]" : "bg-transparent"
                )} 
              />
            ))}
            {/* Ligne de fin pour fermer la dernière semaine */}
            <div className="border-l border-white/[0.08] h-full" />
          </div>

          {scheduledItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-60 opacity-50"><Calendar className="w-12 h-12 mb-4 text-slate-600" /><p className="text-sm font-medium">Aucune tâche planifiée.</p></div>
          ) : (
            <div className="divide-y divide-white/5">
              {scheduledItems.map(item => {
                const pos = getPositionStyles(item.start_date, item.target_date, item.id);
                if (!pos) return null;
                const config = STAGE_CONFIG[item.planning_stage] || STAGE_CONFIG['backlog'];
                const isInteracting = interaction?.itemId === item.id;

                return (
                  <div key={item.id} className={cn("flex relative hover:bg-white/[0.02] transition-colors h-14", isInteracting && "bg-white/5")}>
                    <div className="w-48 lg:w-64 shrink-0 p-3 border-r border-white/10 flex items-center gap-2 cursor-pointer z-10" onClick={() => onEdit(item)}>
                      <div className={cn("w-2 h-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)]", config.color.split(' ')[0])} />
                      <div className="truncate text-xs font-bold text-white group-hover:text-klando-gold">{item.title}</div>
                    </div>
                    
                    <div className="flex-1 relative p-2">
                      <div 
                        className={cn(
                          "absolute top-2 bottom-2 rounded-lg shadow-xl border flex items-center px-3 overflow-hidden backdrop-blur-md cursor-grab active:cursor-grabbing transition-all",
                          config.color, 
                          isInteracting ? "z-30 scale-y-105 shadow-klando-gold/20 brightness-125" : "hover:brightness-110",
                          pos.isCutStart && "rounded-l-none border-l-0", pos.isCutEnd && "rounded-r-none border-r-0"
                        )}
                        style={{ left: pos.left, width: pos.width }}
                        onMouseDown={(e) => startInteraction(e, item, 'move')}
                      >
                        <GripVertical className="w-3 h-3 opacity-40 shrink-0" />
                        <span className="text-[10px] font-black truncate ml-2 drop-shadow-md">
                          {localProgress[item.id] ?? item.progress}%
                        </span>
                        
                        <div 
                          className="absolute right-0 top-0 bottom-0 w-3 cursor-ew-resize hover:bg-white/20 active:bg-white/40 group/resize flex items-center justify-center"
                          onMouseDown={(e) => startInteraction(e, item, 'resize')}
                        >
                          <div className="w-0.5 h-4 bg-white/20 rounded-full group-hover/resize:bg-white/50" />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-black text-[11px] text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
          <Plus className="w-4 h-4 text-klando-gold" /> Backlog
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {unscheduledItems.map(item => (
            <div key={item.id} className="relative group">
              <RoadmapCard item={item} currentProgress={localProgress[item.id] ?? item.progress} isUpdating={updatingId === item.id}
                onProgressChange={onProgressChange} onSetLocalProgress={onSetLocalProgress} onTogglePlanning={onTogglePlanning} onDelete={onDelete} onEdit={onEdit} />
              
              <Button 
                size="sm" 
                className="absolute -top-2 -right-2 rounded-full w-8 h-8 p-0 bg-klando-gold text-black shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-30"
                onClick={() => handleQuickPlan(item)}
                title="Planifier"
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
