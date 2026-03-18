"use client";

import { useMemo, useState } from "react";
import { Calendar, MoreHorizontal, GripHorizontal, Plus, ChevronLeft, ChevronRight, Star, Clock, Info, X, ArrowRight } from "lucide-react";
import { RoadmapItem, STAGE_CONFIG, ICON_MAP, PlanningBoard } from "../types";
import type { DashMember } from "@/lib/queries/admin";
import { RoadmapCard } from "./roadmap-card";
import { BoardSelector } from "./board-selector";
import { cn } from "@/lib/utils";
import { useGanttInteraction } from "../use-gantt-interaction";
import { updateRoadmapItem } from "@/app/admin/roadmap/actions";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface PlanningGanttProps {
  items: RoadmapItem[];
  members: DashMember[];
  boards: PlanningBoard[];
  selectedBoardId: string | null;
  onBoardChange: (boardId: string | null) => void;
  localProgress: Record<string, number>;
  updatingId: string | null;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function PlanningGantt({
  items, members, boards, selectedBoardId, onBoardChange,
  localProgress, updatingId, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit
}: PlanningGanttProps) {

  const membersMap = useMemo(() => {
    const map: Record<string, DashMember> = {};
    members.forEach(m => { map[m.email] = m; });
    return map;
  }, [members]);

  const boardsMap = useMemo(() => {
    const map: Record<string, PlanningBoard> = {};
    boards.forEach(b => { map[b.id] = b; });
    return map;
  }, [boards]);
  
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

  // Optimistic state: keeps visual position while server action is in-flight
  const [pendingUpdates, setPendingUpdates] = useState<Record<string, { start_date: string; target_date: string }>>({});

  const { containerRef, interaction, startInteraction, calculateNewDates } = useGanttInteraction(
    timelineStart,
    timelineDuration,
    async (id, data) => {
      const { start_date, target_date } = data;
      // Apply optimistic update immediately so bar doesn't snap back
      setPendingUpdates(prev => ({ ...prev, [id]: { start_date, target_date } }));
      const result = await updateRoadmapItem(id, { start_date, target_date });
      if (result.success) toast.success("Planification mise à jour");
      else toast.error("Erreur de mise à jour");
      // Clear optimistic state — server props will have the real data now
      setPendingUpdates(prev => {
        const next = { ...prev };
        delete next[id];
        return next;
      });
    }
  );

  const selectedItem = useMemo(() => items.find(i => i.id === selectedItemId), [items, selectedItemId]);

  const getPositionStyles = (startDateStr: string | null, endDateStr: string | null, itemId?: string) => {
    let startStr = startDateStr;
    let endStr = endDateStr;

    // Priority 1: live drag/resize in progress
    if (interaction && interaction.itemId === itemId) {
      const newDates = calculateNewDates(interaction);
      if (newDates) {
        startStr = newDates.start_date;
        endStr = newDates.target_date;
      }
    }
    // Priority 2: optimistic update waiting for server
    else if (itemId && pendingUpdates[itemId]) {
      startStr = pendingUpdates[itemId].start_date;
      endStr = pendingUpdates[itemId].target_date;
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

  const scheduledItems = items.filter(i => i.start_date && i.target_date).sort((a, b) => a.order_index - b.order_index);
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
      {/* Board selector */}
      <BoardSelector boards={boards} selectedBoardId={selectedBoardId} onBoardChange={onBoardChange} />

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
          {/* Vertical Lines & Weekends */}
          <div className="absolute inset-0 left-48 lg:left-64 flex pointer-events-none h-full">
            {timelineWeeks.map((week, i) => {
              const isToday = getWeekNumber(week) === getWeekNumber(new Date()) && week.getFullYear() === new Date().getFullYear();
              
              // Générer les sous-colonnes pour les jours (optionnel mais aide pour les week-ends)
              const days = [];
              for(let d=0; d<7; d++) {
                const dayDate = new Date(week.getTime() + d * 86400000);
                const isWE = dayDate.getDay() === 0 || dayDate.getDay() === 6;
                days.push(isWE);
              }

              return (
                <div key={i} className={cn(
                  "flex-1 border-l border-white/[0.01] h-full transition-colors flex",
                  i % 2 === 0 ? "bg-white/[0.002]" : "bg-transparent",
                  isToday && "border-l-klando-gold/20 bg-klando-gold/[0.005]"
                )}>
                  {days.map((isWE, j) => (
                    <div key={j} className={cn(
                      "flex-1 h-full border-l border-white/[0.005] first:border-l-0",
                      isWE && "bg-black/10"
                    )} />
                  ))}
                </div>
                );
                })}
                <div className="border-l border-white/[0.01] h-full" />
                </div>

          {/* Today line */}
          {(() => {
            const now = new Date();
            now.setHours(0, 0, 0, 0);
            const nowTs = now.getTime();
            if (nowTs >= timelineStart && nowTs <= timelineEnd) {
              const pct = ((nowTs - timelineStart) / timelineDuration) * 100;
              return (
                <div className="absolute top-0 bottom-0 z-20 pointer-events-none" style={{ left: `calc(${pct}% + 12rem)` }}>
                  <div className="w-px h-full bg-klando-gold/60" />
                  <div className="absolute -top-0 left-1/2 -translate-x-1/2 px-1.5 py-0.5 bg-klando-gold rounded-b text-[8px] font-black text-black uppercase">
                    Auj.
                  </div>
                </div>
              );
            }
            return null;
          })()}

          <div className="divide-y divide-white/5 relative">
            {scheduledItems.map(item => {
              const interactionData = interaction && interaction.itemId === item.id ? calculateNewDates(interaction) : null;
              const pos = getPositionStyles(item.start_date, item.target_date, item.id);
              if (!pos) return null;
              
              const config = STAGE_CONFIG[item.planning_stage] || STAGE_CONFIG['backlog'];
              const hasCustomColor = !!item.custom_color;
              const ItemIcon = ICON_MAP[item.icon_name] || null;
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
                    <div
                      className={cn("w-3 h-3 rounded-full shadow-[0_0_10px_rgba(0,0,0,0.5)] shrink-0", !hasCustomColor && config.color.split(' ')[0])}
                      style={hasCustomColor ? { backgroundColor: item.custom_color! } : undefined}
                    />
                    <div className={cn(
                      "truncate text-xs font-bold transition-colors",
                      isSelected ? "text-klando-gold" : "text-slate-200 group-hover:text-klando-gold"
                    )}>{item.title}</div>
                  </div>
                  
                  {/* Timeline Bar Area */}
                  <div className="flex-1 relative p-3">
                    {/* Tooltip flottant pendant interaction */}
                    {isInteracting && interactionData && (
                      <div 
                        className="absolute -top-6 z-50 px-3 py-1 bg-black border border-klando-gold rounded-lg shadow-[0_0_20px_rgba(235,195,63,0.3)] pointer-events-none animate-in fade-in zoom-in duration-200"
                        style={{ 
                          left: `calc(${pos.left} + ${parseFloat(pos.width)/2}%)`,
                          transform: 'translateX(-50%)'
                        }}
                      >
                        <div className="flex items-center gap-3 whitespace-nowrap">
                          <span className="text-[10px] font-black text-white uppercase tracking-tighter">
                            {new Date(interactionData.start_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                          </span>
                          <ArrowRight className="w-3 h-3 text-klando-gold" />
                          <span className="text-[10px] font-black text-white uppercase tracking-tighter">
                            {new Date(interactionData.target_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
                          </span>
                          <div className="h-3 w-px bg-white/20 mx-1" />
                          <span className="text-[10px] font-black text-klando-gold">{interactionData.diffDays}j</span>
                        </div>
                      </div>
                    )}

                      <div
                        className={cn(
                          "absolute top-3 bottom-3 rounded-xl shadow-2xl border-2 flex items-center overflow-hidden transition-all group/bar",
                          !hasCustomColor && config.color,
                          hasCustomColor && "text-white border-white/20",
                          isInteracting ? "z-30 scale-y-110 shadow-klando-gold/40 brightness-110" : "hover:brightness-105",
                          isSelected ? "ring-4 ring-klando-gold/30 z-20" : "",
                          pos.isCutStart && "rounded-l-none border-l-0 opacity-70",
                          pos.isCutEnd && "rounded-r-none border-r-0 opacity-70"
                        )}
                        style={{ left: pos.left, width: pos.width, ...(hasCustomColor ? { backgroundColor: item.custom_color! } : {}) }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedItemId(item.id);
                        }}
                      >
                        {/* Progress bar */}
                        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
                          <div
                            className="absolute inset-y-0 left-0 bg-black/20 transition-all duration-300"
                            style={{ width: `${localProgress[item.id] ?? item.progress}%` }}
                          />
                        </div>

                      {/* Drag Handle — centré en bas du bloc */}
                      <div
                        className={cn(
                          "absolute bottom-0 left-1/2 -translate-x-1/2 h-4 w-10 flex items-center justify-center cursor-grab active:cursor-grabbing z-10 rounded-t-md transition-all",
                          "bg-black/20 hover:bg-white/20 active:bg-white/30",
                          isInteracting && interaction?.type === 'move' ? "bg-white/30 opacity-100 w-14" : isSelected ? "opacity-80" : "opacity-0 group-hover/bar:opacity-80"
                        )}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'move');
                        }}
                        onTouchStart={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'move');
                        }}
                        title="Glisser pour déplacer"
                      >
                        <GripHorizontal className="w-4 h-3 opacity-80" />
                      </div>

                      {/* Resize Handle Left */}
                      <div
                        className={cn(
                          "absolute left-0 top-0 bottom-0 w-3 cursor-ew-resize flex items-center justify-center z-40 transition-all group/handle-left",
                          interaction?.itemId === item.id ? "opacity-100" : isSelected ? "opacity-80" : "opacity-0 group-hover/bar:opacity-70 hover:!opacity-100"
                        )}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-left');
                        }}
                        onTouchStart={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-left');
                        }}
                      >
                        <div className={cn(
                          "w-1.5 h-8 rounded-full transition-all bg-klando-gold/80 border border-black/20",
                          "group-hover/handle-left:bg-klando-gold group-hover/handle-left:h-10",
                          interaction?.type === 'resize-left' && interaction.itemId === item.id && "bg-klando-gold h-12 shadow-klando-gold/50"
                        )} />
                      </div>

                      <div className="flex items-center gap-2 flex-1 min-w-0 px-3">
                        {ItemIcon && <ItemIcon className="w-4 h-4 shrink-0 opacity-70" />}
                        <div className="flex flex-col min-w-0">
                          <span className="text-[11px] font-black truncate">{item.title}</span>
                          <span className="text-[9px] font-bold opacity-80">{localProgress[item.id] ?? item.progress}%</span>
                        </div>
                        {/* Assignee avatars */}
                        {item.assigned_to?.length > 0 && (
                          <div className="flex -space-x-1.5 shrink-0 ml-auto mr-1">
                            {item.assigned_to.slice(0, 3).map(email => {
                              const member = membersMap[email];
                              const initials = (member?.display_name || email).split(' ').map(w => w[0]?.toUpperCase()).slice(0, 2).join('');
                              return (
                                <div
                                  key={email}
                                  title={member?.display_name || email}
                                  className="w-5 h-5 rounded-full border border-black/30 bg-white/20 flex items-center justify-center text-[7px] font-black"
                                >
                                  {initials}
                                </div>
                              );
                            })}
                            {item.assigned_to.length > 3 && (
                              <div className="w-5 h-5 rounded-full border border-black/30 bg-black/30 flex items-center justify-center text-[8px] font-bold">
                                +{item.assigned_to.length - 3}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {/* Resize Handle Right */}
                      <div
                        className={cn(
                          "absolute right-0 top-0 bottom-0 w-3 cursor-ew-resize flex items-center justify-center z-40 transition-all group/handle-right",
                          interaction?.itemId === item.id ? "opacity-100" : isSelected ? "opacity-80" : "opacity-0 group-hover/bar:opacity-70 hover:!opacity-100"
                        )}
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-right');
                        }}
                        onTouchStart={(e) => {
                          e.stopPropagation();
                          startInteraction(e, item, 'resize-right');
                        }}
                      >
                        <div className={cn(
                          "w-1.5 h-8 rounded-full transition-all bg-klando-gold/80 border border-black/20",
                          "group-hover/handle-right:bg-klando-gold group-hover/handle-right:h-10",
                          interaction?.type === 'resize-right' && interaction.itemId === item.id && "bg-klando-gold h-12 shadow-klando-gold/50"
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
        <Card className="border-klando-gold/30 !bg-slate-900 !text-white backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-500 shadow-[0_-20px_50px_-12px_rgba(0,0,0,0.5)]">
          <CardHeader className="p-4 flex flex-row items-center justify-between space-y-0">
            <div className="flex items-center gap-3">
              <div className={cn("p-2 rounded-xl bg-klando-gold/10 text-klando-gold")}>
                <Info className="w-5 h-5" />
              </div>
              <div>
                <CardTitle className="text-lg font-black !text-klando-gold">{selectedItem.title}</CardTitle>
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
                  // Si un board est sélectionné, on planifie direct dessus
                  if (selectedBoardId) {
                    const today = new Date();
                    const start_date = today.toISOString().split('T')[0];
                    const target_date = new Date(today.getTime() + 7 * 86400000).toISOString().split('T')[0];
                    await updateRoadmapItem(item.id, { 
                      start_date, 
                      target_date, 
                      planning_board_id: selectedBoardId,
                      is_planning: true 
                    });
                    setSelectedItemId(item.id);
                    toast.success(`Planifié sur le board actuel`);
                  } else {
                    // Sinon on ouvre la modale pour laisser choisir le board
                    onEdit(item);
                    toast.info("Choisissez un board pour planifier cette tâche");
                  }
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
