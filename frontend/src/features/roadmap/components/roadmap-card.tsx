"use client";

import { 
  CheckCircle2, Circle, Timer, Loader2, Trash2, ArrowRightLeft, Pencil, Target
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { RoadmapItem, ICON_MAP } from "../types";

interface RoadmapCardProps {
  item: RoadmapItem;
  currentProgress: number;
  isUpdating: boolean;
  onProgressChange: (id: string, val: number) => void;
  onSetLocalProgress: (id: string, val: number) => void;
  onTogglePlanning: (id: string, isPlanning: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (item: RoadmapItem) => void;
}

export function RoadmapCard({ 
  item, currentProgress, isUpdating, onProgressChange, onSetLocalProgress,
  onTogglePlanning, onDelete, onEdit 
}: RoadmapCardProps) {
  const IconComp = ICON_MAP[item.icon_name] || Target;

  return (
    <Card className={cn(
      "bg-slate-900/50 border-white/5 transition-all duration-300 group relative flex flex-col h-full",
      item.status === "done" ? "opacity-80" : "hover:border-klando-gold/30"
    )}>
      <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-20">
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onEdit(item)}>
          <Pencil className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="icon" className="h-7 w-7 text-indigo-200" onClick={() => onTogglePlanning(item.id, !item.is_planning)}>
          <ArrowRightLeft className="h-3.5 w-3.5" />
        </Button>
        <Button variant="ghost" size="icon" className="h-7 w-7 text-red-400" onClick={() => onDelete(item.id)}>
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>

      <CardHeader className="p-4 pb-2">
        <div className="flex items-start justify-between">
          <div className={cn("p-2 rounded-lg", item.status === "done" ? "bg-green-500/10 text-green-400" : "bg-klando-gold/10 text-klando-gold")}>
            <IconComp className="w-4 h-4" />
          </div>
          {isUpdating ? <Loader2 className="w-4 h-4 animate-spin text-klando-gold" /> : 
           item.status === "done" ? <CheckCircle2 className="w-4 h-4 text-green-400" /> :
           item.status === "in-progress" ? <Timer className="w-4 h-4 text-klando-gold animate-pulse" /> : <Circle className="w-4 h-4 text-slate-600" />}
        </div>
        <CardTitle className="text-sm mt-3 group-hover:text-klando-gold transition-colors">{item.title}</CardTitle>
        <CardDescription className="text-[11px] line-clamp-2 mt-1">{item.description}</CardDescription>
      </CardHeader>

      <CardContent className="p-4 pt-2 mt-auto">
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between text-[9px] uppercase tracking-wider font-bold text-slate-500">
            <span>{item.status === "done" ? "Terminé" : "Progrès"}</span>
            <span>{currentProgress}%</span>
          </div>
          <input
            type="range" min="0" max="100" step="5" value={currentProgress}
            onChange={(e) => onSetLocalProgress(item.id, parseInt(e.target.value))}
            onMouseUp={() => onProgressChange(item.id, currentProgress)}
            className="flex-1 h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-klando-gold"
            disabled={isUpdating}
          />
          <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
            <div className={cn("h-full transition-all duration-1000", item.status === "done" ? "bg-green-500" : "bg-klando-gold")} style={{ width: `${item.progress}%` }} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
