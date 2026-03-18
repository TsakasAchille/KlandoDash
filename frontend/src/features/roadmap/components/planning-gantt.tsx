"use client";

import { useMemo, useEffect, useState } from "react";
import { Calendar, MoreHorizontal, GripVertical, Plus, ChevronLeft, ChevronRight, Star, Clock, Info, X } from "lucide-react";
import { RoadmapItem, STAGE_CONFIG } from "../types";
import { RoadmapCard } from "./roadmap-card";
import { cn } from "@/lib/utils";
import { useGanttInteraction } from "../use-gantt-interaction";
import { updateRoadmapItem } from "@/app/admin/roadmap/actions";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
  
  const [weekOffset, setWeekOffset] = useState(0);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const weeksToShow = 14;

  const timelineWeeks = useMemo(() => {
    const weeks = [];
    const today = new Date();
    const baseDate = new Date(today.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1)));
    const startOfView = new Date(baseDate.getTime() + weekOffset * 7 * 86400000);
    
    for (let i = 0; i < weeksToShow; i++) {
      const d = new Date(startOfView.getTime() + i * 7 * 86400000);
      weeks.push(d);
    }
    return weeks;
  }, [weekOffset]);

  const timelineStart = timelineWeeks[0].getTime();
  const timelineEnd = new Date(timelineWeeks[weeksToShow - 1].getTime() + 7 * 86400000).getTime();
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

  const selectedItem = useMemo(() => items.find(i => i.id === selectedItemId), [items, selectedItemId]);

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
    
    return { left: `${left}%`, width: `${Math.max(width, 0.5)}%`, isCutStart: start < timelineStart, isCutEnd: end > timelineEnd };
  };

  const scheduledItems = items.filter(i => i.start_date && i.target_date).sort((a, b) => new Date(a.start_date!).getTime() - new Date(b.start_date!).getTime());
  const unscheduledItems = items.filter(i => !i.start_date || !i.target_date);

  const getWeekNumber = (d: Date) => {
    const date = new Date(d.getTime());
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
    const week1 = new Date(date.getFullYear(), 0, 4);
    return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
  };

  return (
    <div className={cn(
      "flex flex-col h-full space-y-6 select-none pb-20 transition-all duration-300",
      interaction?.type === 'move' && "cursor-grabbing",
      (interaction?.type === 'resize-left' || interaction?.type === 'resize-right') && "cursor-ew-resize"
    )}>
      <div className="rounded-2xl border border-white/10 bg-slate-900/50 overflow-hidden flex flex-col shadow-2xl">
        {/* Navigation */}
        <div className="flex items-center justify-between border-b border-white/10 bg-white/5 p-3">
          <div className="flex items-center gap-4">
            <div className="w-40 lg:w-56 shrink-0 font-black text-[11px] uppercase tracking-[0.2em] text-klando-gold px-2">
              Gantt Engine 1.0
            </div>
            <div className="flex items-center bg-black/40 rounded-xl p-1 border border-white/5">
              <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-white" onClick={() => setWeekOffset(prev => prev - 4)}>
                <ChevronLeft className="h-5 w-5" />
              </Button>
              <Button variant="ghost" className="h-8 text-[10px] font-black uppercase px-4 hover:bg-white/10 text-white" onClick={() => setWeekOffset(0)}>
                Aujourd'hui
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-white" onClick={() => setWeekOffset(prev => prev + 4)}>
                <ChevronRight className="h-5 w-5" />
              </Button>
            </div>
          </div>
          <div className="text-[10px] font-black text-slate-400 uppercase tracking-[0.1em] hidden sm:block bg-white/5 px-3 py-1 rounded-full border border-white/5">
            {timelineWeeks[0].toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })} — {timelineWeeks[weeksToShow-1].toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
          </div>
        </div>

        {/* Calendar Header */}
        <div className="flex border-b border-white/10 bg-white/[0.02]">
          <div className="w-48 lg:w-64 shrink-0 border-r border-white/10 p-3 flex items-center justify-center">
             <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">Tâches</span>
          </div>
          <div className="flex-1 flex" ref={containerRef}>
            {timelineWeeks.map((week, i) => {
              const isToday = getWeekNumber(week) === getWeekNumber(new Date()) && week.getFullYear() === new Date().getFullYear();
              return (
                <div key={i} className={cn(
                  "flex-1 py-3 text-center border-l border-white/5 first:border-l-0 transition-colors",
                  isToday && "bg-klando-gold/10"
                )}>
                  <div className={cn("text-[10px] font-black uppercase", isToday ? "text-klando-gold" : "text-slate-400")}>W{getWeekNumber(week)}</div>
                  <div className="text-[8px] font-bold text-slate-500 uppercase opacity-60">{week.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto relative min-h-[500px]">
          {/* Vertical Lines */}
          <div className="absolute inset-0 left-48 lg:left-64 flex pointer-events-none h-full">
            {timelineWeeks.map((week, i) => {
              const isToday = getWeekNumber(week) === getWeekNumber(new Date()) && week.getFullYear() === new Date().getFullYear();
              return (
                <div key={i} className={cn(
                  "flex-1 border-l border-white/[0.08] h-full transition-colors",
                  i % 2 === 0 ? "bg-white/[0.01]" : "bg-transparent",
                  isToday && "border-l-klando-gold/40 bg-klando-gold/[0.03]"
                )} />
              );
            })}
            <div className="border-l border-white/[0.08] h-full" />
          </div>

          <div className="divide-y divide-white/5 relative">
            {scheduledItems.map(item => {
              const pos = getPositionStyles(item.start_date, item.target_date, item.id);
              if (!pos) return null;
              const config = STAGE_CONFIG[item.planning_stage] || STAGE_CONFIG['backlog'];
              const isInteracting = interaction?.itemId === item.id;
              const isSelected = selectedItemId === item.id;

              return (
                <div key={item.id} className={cn(
                  "flex relative transition-all h-20 group", 
                  isInteracting && "bg-white/5",
                  isSelected && "bg-klando-gold/5"
                )}>
                  {/* Left Label */}
                  <div 
                    className="w-48 lg:w-64 shrink-0 p-4 border-r border-white/10 flex items-center gap-3 cursor-pointer z-10 hover:bg-white/5" 
                    onClick={() => {
                      setSelectedItemId(item.id);
                      onEdit(item);
                    }}
                  >
                    <div className={cn("w-3 h-3 rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)] shrink-0", config.color.split(' ')[0])} />
                    <div className={cn(
                      "truncate text-xs font-bold transition-colors",
                      isSelected ? "text-klando-gold" : "text-white group-hover:text-klando-gold"
                    )}>{item.title}</div>
                  </div>
                  
                  {/* Timeline Bar Area */}
                  <div className="flex-1 relative p-3">
                    <div 
                      className={cn(
                        "absolute top-3 bottom-3 rounded-xl shadow-2xl border-2 flex items-center px-4 overflow-hidden backdrop-blur-md cursor-grab active:cursor-grabbing transition-all group/bar",
                        config.color, 
                        isInteracting ? "z-30 scale-y-110 shadow-klando-gold/40 brightness-150 border-klando-gold" : "hover:brightness-110 border-transparent",
                        isSelected ? "border-klando-gold ring-4 ring-klando-gold/20 z-20" : "",
                        pos.isCutStart && "rounded-l-none border-l-0 opacity-70", 
                        pos.isCutEnd && "rounded-r-none border-r-0 opacity-70"
                      )}
                      style={{ left: pos.left, width: pos.width }}
                      onMouseDown={(e) => startInteraction(e, item, 'move')}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedItemId(item.id);
                      }}
                    >
                      {/* Resize Handle Left */}
                      <div 
                        className={cn(
                          "absolute left-0 top-0 bottom-0 w-10 cursor-ew-resize flex items-center justify-center z-40 transition-all group/handle-left",
                          interaction?.itemId === item.id ? "opacity-100" : "opacity-0 group-hover/bar:opacity-70 hover:!opacity-100"
                        )}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-left');
                        }}
                      >
                        <div className={cn(
                          "w-2.5 h-10 rounded-full transition-all shadow-[0_0_15px_rgba(0,0,0,0.5)] border-2 bg-klando-gold/80 border-black/20",
                          "group-hover/handle-left:bg-klando-gold group-hover/handle-left:border-white group-hover/handle-left:h-14 group-hover/handle-left:scale-x-110",
                          interaction?.type === 'resize-left' && interaction.itemId === item.id && "bg-klando-gold border-white scale-x-125 h-16 shadow-klando-gold/50"
                        )} />
                      </div>

                      <div className="flex items-center gap-2 w-full px-8">
                        <GripVertical className="w-4 h-4 opacity-40 shrink-0" />
                        <div className="flex flex-col min-w-0">
                          <span className="text-[11px] font-black truncate drop-shadow-md">{item.title}</span>
                          <span className="text-[9px] font-bold opacity-70">{localProgress[item.id] ?? item.progress}% complété</span>
                        </div>
                      </div>
                      
                      {/* Resize Handle Right */}
                      <div 
                        className={cn(
                          "absolute right-0 top-0 bottom-0 w-10 cursor-ew-resize flex items-center justify-center z-40 transition-all group/handle-right",
                          interaction?.itemId === item.id ? "opacity-100" : "opacity-0 group-hover/bar:opacity-70 hover:!opacity-100"
                        )}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-right');
                        }}
                      >
                        <div className={cn(
                          "w-2.5 h-10 rounded-full transition-all shadow-[0_0_15px_rgba(0,0,0,0.5)] border-2 bg-klando-gold/80 border-black/20",
                          "group-hover/handle-right:bg-klando-gold group-hover/handle-right:border-white group-hover/handle-right:h-14 group-hover/handle-right:scale-x-110",
                          interaction?.type === 'resize-right' && interaction.itemId === item.id && "bg-klando-gold border-white scale-x-125 h-16 shadow-klando-gold/50"
                        )} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Détails de la tâche sélectionnée */}
      {selectedItem && (
        <Card className="border-klando-gold/30 bg-slate-900/80 backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-[0_-20px_50px_-12px_rgba(0,0,0,0.5)]">
          <CardHeader className="p-4 flex flex-row items-center justify-between space-y-0">
            <div className="flex items-center gap-3">
              <div className={cn("p-2 rounded-xl bg-klando-gold/10 text-klando-gold")}>
                <Info className="w-5 h-5" />
              </div>
              <div>
                <CardTitle className="text-lg font-black text-white">{selectedItem.title}</CardTitle>
                <div className="flex items-center gap-4 mt-1">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                    <Clock className="w-3 h-3" />
                    Du {new Date(selectedItem.start_date!).toLocaleDateString()} au {new Date(selectedItem.target_date!).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest text-klando-gold">
                    <Star className="w-3 h-3" />
                    Progression: {localProgress[selectedItem.id] ?? selectedItem.progress}%
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="h-8 border-white/10 hover:bg-white/5" onClick={() => onEdit(selectedItem)}>
                Modifier
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400" onClick={() => setSelectedItemId(null)}>
                <X className="w-5 h-5" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/5 text-sm text-slate-300 leading-relaxed italic">
              {selectedItem.description || "Aucune description détaillée fournie."}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Backlog */}
      <div className="space-y-4">
        <h3 className="font-black text-[11px] text-slate-400 uppercase tracking-[0.3em] flex items-center gap-2 px-2">
          <MoreHorizontal className="w-4 h-4 text-klando-gold" /> Tâches sans dates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {unscheduledItems.map(item => (
            <div key={item.id} className="relative group">
              <RoadmapCard item={item} currentProgress={localProgress[item.id] ?? item.progress} isUpdating={updatingId === item.id}
                onProgressChange={onProgressChange} onSetLocalProgress={onSetLocalProgress} onTogglePlanning={onTogglePlanning} onDelete={onDelete} onEdit={onEdit} />
              
              <Button 
                size="sm" 
                className="absolute -top-2 -right-2 rounded-full w-8 h-8 p-0 bg-klando-gold text-black shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-30"
                onClick={async () => {
                  const today = new Date();
                  await updateRoadmapItem(item.id, {
                    start_date: today.toISOString().split('T')[0],
                    target_date: new Date(today.getTime() + 7 * 86400000).toISOString().split('T')[0]
                  });
                  setSelectedItemId(item.id);
                }}
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
