"use client";

import { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronLeft, ChevronRight, Calendar as CalendarIcon, 
  Music, Instagram, Twitter, Mail, 
  FileText, X as XIcon, Plus, Image as ImageIcon,
  GripVertical, MessageSquare
} from "lucide-react";
import { MarketingComm, MarketingMessage } from "@/app/marketing/types";
import { cn } from "@/lib/utils";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, addMonths, subMonths, isToday, isSameMonth, startOfWeek, endOfWeek } from "date-fns";
import { fr } from "date-fns/locale";
import { EventDetailsModal } from "./EventDetailsModal";
import { PlanPostModal } from "./PlanPostModal";
import { toast } from "sonner";
import { updateMarketingCommAction } from "@/app/marketing/actions/communication";

interface CalendarTabProps {
  comms: MarketingComm[];
  emails: MarketingMessage[]; // Prop name remains for compatibility but type is generic
}

type CalendarEvent = (MarketingComm | MarketingMessage) & { 
  eventType: 'COMM' | 'DIRECT_MSG'; 
  date: Date;
};

export function CalendarTab({ comms, emails: messages }: CalendarTabProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState<Date | null>(new Date());
  
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventType, setSelectedEventType] = useState<'COMM' | 'DIRECT_MSG' | null>(null);
  
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [isDraggingOver, setIsDraggingOver] = useState<string | null>(null);

  // Génération des jours — toujours 6 lignes (42 cellules) pour taille fixe
  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 1 });
    const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 1 });
    const interval = eachDayOfInterval({ start, end });
    // Toujours 42 jours (6 lignes) pour éviter le changement de taille
    while (interval.length < 42) {
      const lastDay = interval[interval.length - 1];
      interval.push(new Date(lastDay.getFullYear(), lastDay.getMonth(), lastDay.getDate() + 1));
    }
    return interval;
  }, [currentMonth]);

  const events = useMemo(() => {
    const allEvents: CalendarEvent[] = [];
    comms.forEach(c => {
      if (c.scheduled_at) {
        allEvents.push({ ...c, eventType: 'COMM', date: new Date(c.scheduled_at) } as CalendarEvent);
      }
    });
    messages.forEach(m => {
      if (m.sent_at) {
        allEvents.push({ ...m, eventType: 'DIRECT_MSG', date: new Date(m.sent_at) } as CalendarEvent);
      }
    });
    return allEvents;
  }, [comms, messages]);

  const selectedEvent = useMemo(() => {
    if (!selectedEventId) return null;
    return events.find(e => e.id === selectedEventId && e.eventType === selectedEventType) || null;
  }, [events, selectedEventId, selectedEventType]);

  const drafts = useMemo(() => {
    return comms.filter(c => !c.scheduled_at && (c.status === 'DRAFT' || c.status === 'NEW') && c.type === 'POST');
  }, [comms]);

  const nextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const prevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));

  const handleDragStart = (e: React.DragEvent, commId: string) => {
    e.dataTransfer.setData("commId", commId);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDrop = async (e: React.DragEvent, date: Date) => {
    e.preventDefault();
    setIsDraggingOver(null);
    const commId = e.dataTransfer.getData("commId");
    if (!commId) return;

    const res = await updateMarketingCommAction(commId, {
        scheduled_at: date.toISOString(),
        status: 'DRAFT'
    });

    if (res.success) {
        toast.success(`Post planifié pour le ${format(date, 'dd MMMM', { locale: fr })}`);
    } else {
        toast.error("Erreur de planification");
    }
  };

  return (
    <div className="relative flex flex-col lg:flex-row gap-6 animate-in fade-in duration-700 text-left h-full">

      {/* 1. CALENDAR GRID (Left/Main - 2/3 width) */}
      <div className="flex-1 flex flex-col gap-4 min-h-0 min-w-0">
        <div className="flex items-center justify-between bg-white p-4 rounded-[2rem] border border-slate-200 shadow-sm shrink-0">
          <div className="flex items-center gap-4 pl-4">
            <div className="p-2 bg-purple-50 rounded-xl">
                <CalendarIcon className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-xl font-black uppercase tracking-tight text-slate-900 italic">
              {format(currentMonth, 'MMMM yyyy', { locale: fr })}
            </h2>
          </div>
          <div className="flex items-center gap-2 pr-2">
            <Button variant="ghost" size="icon" onClick={prevMonth} className="hover:bg-slate-100 text-slate-600 rounded-xl"><ChevronLeft className="w-5 h-5" /></Button>
            <Button variant="outline" onClick={() => setCurrentMonth(new Date())} className="text-[10px] font-black uppercase tracking-widest border-slate-200 text-slate-600 h-9 px-4 rounded-xl hover:bg-slate-50">Aujourd&apos;hui</Button>
            <Button variant="ghost" size="icon" onClick={nextMonth} className="hover:bg-slate-100 text-slate-600 rounded-xl"><ChevronRight className="w-5 h-5" /></Button>
          </div>
        </div>

        {/* --- GRID SYSTEM --- */}
        <div className="bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl flex flex-col w-full flex-1 min-h-0">
          {/* Days Header - FORCED GRID */}
          <div
            className="grid grid-cols-7 bg-slate-50/50 border-b border-slate-100 shrink-0"
            style={{ display: 'grid', gridTemplateColumns: 'repeat(7, minmax(0, 1fr))' }}
          >
            {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(d => (
              <div key={d} className="py-3 text-center text-[10px] font-black uppercase tracking-widest text-slate-400 border-r border-slate-100 last:border-r-0">{d}</div>
            ))}
          </div>

          {/* Calendar Body - FIXED HEIGHT ROWS */}
          <div
            className="grid grid-cols-7 flex-1 min-h-0"
            style={{ display: 'grid', gridTemplateColumns: 'repeat(7, minmax(0, 1fr))', gridTemplateRows: 'repeat(6, minmax(0, 1fr))' }}
          >
            {days.map((day, i) => {
              const dayEvents = events.filter(e => isSameDay(e.date, day));
              const isCurrentMonth = isSameMonth(day, currentMonth);
              const dayId = format(day, 'yyyy-MM-dd');
              
              return (
                <div
                  key={i}
                  onClick={() => setSelectedDay(day)}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDraggingOver(dayId);
                  }}
                  onDragLeave={() => setIsDraggingOver(null)}
                  onDrop={(e) => handleDrop(e, day)}
                  className={cn(
                    "relative border-r border-b border-slate-100 p-2 transition-all hover:bg-slate-50/50 cursor-pointer flex flex-col gap-1 overflow-hidden group min-h-0",
                    !isCurrentMonth && "bg-slate-50/20 opacity-30",
                    isToday(day) && "bg-purple-50/40",
                    selectedDay && isSameDay(day, selectedDay) 
                      ? "bg-purple-50/80 ring-2 ring-purple-600 ring-inset shadow-md z-10" 
                      : "hover:shadow-inner",
                    isDraggingOver === dayId && "bg-blue-50 ring-2 ring-blue-400 ring-inset z-10"
                  )}
                >
                  <div className="flex justify-between items-center mb-0.5 shrink-0">
                    <span className={cn(
                      "text-[11px] font-black tabular-nums transition-all px-1.5 py-0.5 rounded-md",
                      isToday(day) 
                        ? "bg-purple-600 text-white shadow-lg shadow-purple-200" 
                        : selectedDay && isSameDay(day, selectedDay)
                          ? "text-purple-600 font-black"
                          : "text-slate-400 group-hover:text-slate-900"
                    )}>
                      {format(day, 'd')}
                    </span>
                    {dayEvents.length > 0 && (
                      <Badge variant="outline" className={cn(
                        "text-[9px] font-black px-1.5 h-5 transition-colors",
                        selectedDay && isSameDay(day, selectedDay) ? "border-purple-200 text-purple-600 bg-white" : "border-slate-200 text-slate-400"
                      )}>
                        {dayEvents.length}
                      </Badge>
                    )}
                  </div>

                  <div className="space-y-1.5 flex-1 overflow-y-auto scrollbar-none pr-0.5">
                    {dayEvents.map((ev, j) => (
                      <div 
                        key={j} 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEventId(ev.id);
                          setSelectedEventType(ev.eventType);
                        }}
                        className={cn(
                          "text-[9px] font-black uppercase p-2 rounded-xl flex flex-col gap-2 border shadow-sm transition-all hover:translate-x-0.5 w-full overflow-hidden",
                          ev.eventType === 'DIRECT_MSG' 
                            ? (('channel' in ev && ev.channel === 'WHATSAPP') ? "bg-green-50 text-green-600 border-green-100" : "bg-purple-50 text-purple-600 border-purple-100") 
                            : "bg-blue-50 text-blue-600 border-blue-100"
                        )}
                      >
                        <div className="flex items-center gap-2">
                          {ev.eventType === 'DIRECT_MSG' ? (
                            ('channel' in ev && ev.channel === 'WHATSAPP') ? <MessageSquare className="w-3 h-3" /> : <Mail className="w-3 h-3" />
                          ) : <ImageIcon className="w-3 h-3" />}
                          <span className="truncate flex-1 min-w-0">
                            {('title' in ev) ? ev.title : (('subject' in ev && ev.subject) ? ev.subject : ev.content.substring(0, 15))}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 2. SIDEBAR (Right - fixed width on desktop, hidden on mobile) */}
      <div className="hidden lg:flex lg:w-[280px] shrink-0 flex-col min-h-0 space-y-4">
        <div className="flex items-center gap-2 px-2 py-2">
            <div className="p-1.5 bg-orange-50 rounded-lg">
                <FileText className="w-4 h-4 text-orange-500" />
            </div>
            <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Brouillons</h3>
        </div>
        
        <div className="flex-1 bg-slate-50 rounded-[2rem] border border-slate-200 overflow-hidden flex flex-col shadow-inner max-h-[500px] lg:max-h-none">
            <div className="p-3 border-b border-slate-200 bg-slate-100/50 text-[9px] font-black uppercase tracking-widest text-slate-400">
                Glisser pour planifier
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
                {drafts.length > 0 ? (
                    drafts.map(c => (
                        <div 
                            key={c.id} 
                            draggable
                            onDragStart={(e) => handleDragStart(e, c.id)}
                            className="bg-white border border-slate-200 rounded-xl p-3 hover:border-purple-400 hover:shadow-sm transition-all cursor-grab active:cursor-grabbing group flex items-center gap-3"
                        >
                            <GripVertical className="w-3.5 h-3.5 text-slate-300 shrink-0" />
                            <div className="flex-1 min-w-0">
                                <p className="text-[10px] font-black text-slate-900 uppercase truncate leading-tight">{c.title}</p>
                                <p className="text-[8px] text-slate-500 truncate mt-0.5">{c.platform}</p>
                            </div>
                            {c.image_url ? (
                                <img src={c.image_url} alt="prev" className="w-8 h-8 rounded-lg object-cover border border-slate-100" />
                            ) : (
                                <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-100">
                                    <ImageIcon className="w-3 h-3 text-slate-300" />
                                </div>
                            )}
                        </div>
                    ))
                ) : (
                    <div className="h-40 flex flex-col items-center justify-center opacity-30 italic text-slate-400">
                        <p className="text-[9px] font-black uppercase text-center">Aucun brouillon</p>
                    </div>
                )}
            </div>
        </div>

        {/* Selected Day Floating Card */}
        {selectedDay && (
            <div className="bg-slate-900 rounded-3xl p-4 shadow-xl border border-white/10 animate-in slide-in-from-bottom-2">
                <div className="flex justify-between items-center mb-2">
                    <p className="text-[10px] font-black uppercase text-white/60">{format(selectedDay, 'EEEE d MMMM', { locale: fr })}</p>
                    <XIcon className="w-3 h-3 text-white/30 cursor-pointer hover:text-white" onClick={() => setSelectedDay(null)} />
                </div>
                <Button 
                    size="sm"
                    onClick={() => setIsPlanModalOpen(true)}
                    className="w-full h-8 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[9px] gap-1.5"
                >
                    <Plus className="w-3 h-3" /> Nouveau Post
                </Button>
            </div>
        )}
      </div>

      <EventDetailsModal 
        event={selectedEvent} 
        onClose={() => {
            setSelectedEventId(null);
            setSelectedEventType(null);
        }} 
      />

      <PlanPostModal 
        date={selectedDay}
        isOpen={isPlanModalOpen}
        onClose={() => setIsPlanModalOpen(false)}
        drafts={drafts}
      />
    </div>
  );
}
