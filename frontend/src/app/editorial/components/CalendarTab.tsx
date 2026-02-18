"use client";

import { useState, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  ChevronLeft, ChevronRight, Calendar as CalendarIcon, 
  Music, Instagram, Twitter, Mail, 
  FileText, Upload, X as XIcon, Plus
} from "lucide-react";
import { MarketingComm, MarketingEmail } from "@/app/marketing/types";
import { cn } from "@/lib/utils";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, addMonths, subMonths, isToday, isSameMonth } from "date-fns";
import { fr } from "date-fns/locale";
import { EventDetailsModal } from "./EventDetailsModal";
import { PlanPostModal } from "./PlanPostModal";
import { toast } from "sonner";

interface CalendarTabProps {
  comms: MarketingComm[];
  emails: MarketingEmail[];
}

type CalendarEvent = (MarketingComm | MarketingEmail) & { 
  eventType: 'COMM' | 'EMAIL'; 
  date: Date;
};

export function CalendarTab({ comms, emails }: CalendarTabProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  
  // Selection stable par ID
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventType, setSelectedEventType] = useState<'COMM' | 'EMAIL' | null>(null);
  
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const events = useMemo(() => {
    const allEvents: CalendarEvent[] = [];
    
    comms.forEach(c => {
      if (c.scheduled_at) {
        allEvents.push({ ...c, eventType: 'COMM', date: new Date(c.scheduled_at) } as CalendarEvent);
      }
    });

    emails.forEach(e => {
      if (e.sent_at) {
        allEvents.push({ ...e, eventType: 'EMAIL', date: new Date(e.sent_at) } as CalendarEvent);
      }
    });

    return allEvents;
  }, [comms, emails]);

  // Retrouver l'objet sélectionné de manière stable
  const selectedEvent = useMemo(() => {
    if (!selectedEventId) return null;
    return events.find(e => e.id === selectedEventId && e.eventType === selectedEventType) || null;
  }, [events, selectedEventId, selectedEventType]);

  const drafts = useMemo(() => {
    return comms.filter(c => !c.scheduled_at && (c.status === 'DRAFT' || c.status === 'NEW') && c.type === 'POST');
  }, [comms]);

  const nextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const prevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));

  return (
    <div className="grid lg:grid-cols-12 gap-8 animate-in fade-in duration-700 h-[800px] text-left">
      
      <div className="lg:col-span-9 flex flex-col space-y-6">
        <div className="flex items-center justify-between bg-white p-4 rounded-[2rem] border border-slate-200 shadow-sm">
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

        <div className="flex-1 bg-white border border-slate-200 rounded-[2.5rem] overflow-hidden shadow-xl flex flex-col">
          <div className="grid grid-cols-7 border-b border-slate-100 bg-slate-50/50">
            {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(d => (
              <div key={d} className="py-4 text-center text-[10px] font-black uppercase tracking-widest text-slate-400">{d}</div>
            ))}
          </div>
          
          <div className="grid grid-cols-7 flex-1">
            {days.map((day, i) => {
              const dayEvents = events.filter(e => isSameDay(e.date, day));
              const isCurrentMonth = isSameMonth(day, currentMonth);
              
              return (
                <div 
                  key={i}
                  onClick={() => setSelectedDay(day)}
                  className={cn(
                    "min-h-[120px] border-r border-b border-slate-100 p-3 transition-all hover:bg-slate-50/50 cursor-pointer group flex flex-col gap-2 relative",
                    !isCurrentMonth && "bg-slate-50/30 opacity-40",
                    isToday(day) && "bg-purple-50/50",
                    selectedDay && isSameDay(day, selectedDay) && "ring-2 ring-purple-600 ring-inset bg-purple-50/30"
                  )}
                >
                  <div className="flex justify-between items-start">
                    <span className={cn(
                      "text-[11px] font-black tabular-nums transition-colors",
                      isToday(day) ? "bg-purple-600 text-white w-6 h-6 rounded-lg flex items-center justify-center -mt-1 -ml-1 shadow-md shadow-purple-200" : "text-slate-400 group-hover:text-slate-900"
                    )}>
                      {format(day, 'd')}
                    </span>
                    {dayEvents.length > 0 && <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />}
                  </div>

                  <div className="space-y-1 overflow-y-auto max-h-[80px] custom-scrollbar pr-1">
                    {dayEvents.map((ev, j) => (
                      <div 
                        key={j} 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEventId(ev.id);
                          setSelectedEventType(ev.eventType);
                        }}
                        className={cn(
                          "text-[8px] font-black uppercase px-1.5 py-1 rounded-md truncate flex items-center gap-1.5 border shadow-sm transition-all hover:scale-105 active:scale-95",
                          ev.eventType === 'EMAIL' ? "bg-green-50 text-green-600 border-green-100" : "bg-blue-50 text-blue-600 border-blue-100"
                        )}
                      >
                        {('platform' in ev) && ev.platform === 'TIKTOK' && <Music className="w-2.5 h-2.5" />}
                        {('platform' in ev) && ev.platform === 'INSTAGRAM' && <Instagram className="w-2.5 h-2.5" />}
                        {('platform' in ev) && ev.platform === 'X' && <Twitter className="w-2.5 h-2.5" />}
                        {ev.eventType === 'EMAIL' && <Mail className="w-2.5 h-2.5" />}
                        {('title' in ev) ? ev.title : ('subject' in ev ? ev.subject : '')}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="lg:col-span-3 space-y-6 flex flex-col h-full">
        <Card className="bg-white border-2 border-dashed border-purple-200 rounded-3xl p-8 text-center group hover:bg-purple-50 hover:border-purple-400 transition-all cursor-pointer shadow-sm">
            <div className="flex flex-col items-center gap-3">
                <div className="p-3 bg-purple-100 rounded-full group-hover:scale-110 transition-transform"><Upload className="w-6 h-6 text-purple-600" /></div>
                <div className="space-y-1">
                    <p className="text-[10px] font-black uppercase tracking-widest text-slate-900">Médiathèque</p>
                    <p className="text-[9px] text-slate-400 font-medium">Déposez vos fichiers ici</p>
                </div>
            </div>
        </Card>

        <div className="flex-1 flex flex-col space-y-4 min-h-0">
            <div className="flex items-center gap-2 px-2">
                <div className="p-1.5 bg-orange-50 rounded-lg">
                    <FileText className="w-4 h-4 text-orange-500" />
                </div>
                <h3 className="text-[10px] font-black uppercase tracking-widest text-slate-500">Contenus à planifier</h3>
            </div>
            
            <div className="flex-1 bg-slate-50 rounded-3xl border border-slate-200 overflow-y-auto custom-scrollbar p-4 space-y-3">
                {drafts.length > 0 ? (
                    drafts.map(c => (
                        <div 
                            key={c.id} 
                            onClick={() => {
                                setSelectedEventId(c.id);
                                setSelectedEventType('COMM');
                            }}
                            className="bg-white border border-slate-200 rounded-2xl p-4 hover:border-purple-400 hover:shadow-md transition-all cursor-pointer group"
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-[8px] font-black text-purple-600 uppercase bg-purple-50 px-1.5 py-0.5 rounded border border-purple-100">{c.platform}</span>
                            </div>
                            <p className="text-[10px] font-black text-slate-900 uppercase truncate">{c.title}</p>
                            <p className="text-[9px] text-slate-500 line-clamp-2 mt-1 italic">&quot;{c.content}&quot;</p>
                        </div>
                    ))
                ) : (
                    <div className="h-40 flex flex-col items-center justify-center opacity-30 italic text-slate-400">
                        <Plus className="w-8 h-8 mb-2" />
                        <p className="text-[9px] font-black uppercase text-center">Aucun brouillon</p>
                    </div>
                )}
            </div>
        </div>

        {selectedDay && (
            <Card className="bg-slate-900 border-none rounded-3xl p-6 shadow-2xl animate-in slide-in-from-right-4 duration-500 text-left">
                <div className="flex justify-between items-center mb-4">
                    <h4 className="text-xs font-black uppercase text-white">{format(selectedDay, 'dd MMMM', { locale: fr })}</h4>
                    <Button variant="ghost" size="icon" onClick={() => setSelectedDay(null)} className="h-6 w-6 text-white hover:bg-white/10"><XIcon className="w-4 h-4" /></Button>
                </div>
                <div className="space-y-3">
                    <Button 
                        onClick={() => {
                            console.log("Planifier post clicked for date:", selectedDay);
                            toast.info(`Ouverture du planificateur pour le ${selectedDay ? format(selectedDay, 'dd MMMM', { locale: fr }) : ''}`);
                            setIsPlanModalOpen(true);
                        }}
                        className="w-full h-10 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-black uppercase text-[10px] gap-2"
                    >
                        <Plus className="w-3.5 h-3.5" /> Planifier un post
                    </Button>
                    <p className="text-[9px] text-center text-white/40 font-medium italic">Glissez un brouillon ici.</p>
                </div>
            </Card>
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
