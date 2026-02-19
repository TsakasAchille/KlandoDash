"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { 
  Target, TrendingUp, Zap, ShieldAlert, MapPin, 
  ArrowRight, Check, Sparkles, 
  CheckSquare, Trash2
} from "lucide-react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { AIRecommendation } from "@/app/marketing/types";

interface RecommendationCardProps {
  reco: AIRecommendation;
  onApply: (id: string) => void;
  onDismiss: (id: string) => void;
}

interface TripMatch {
  id: string;
  dist: number;
  time: string;
}

interface RecommendationContent {
  request?: {
    origin: string;
    destination: string;
    has_ai_scan?: boolean;
    last_ai_date?: string;
  };
  top_trips?: TripMatch[];
  matches_count?: number;
  alert?: string;
  reason?: string;
}

export function RecommendationCard({ reco, onApply, onDismiss }: RecommendationCardProps) {
  const router = useRouter();
  const isApplied = reco.status === 'APPLIED';
  const isTraction = reco.type === 'TRACTION';
  const content = reco.content as unknown as RecommendationContent;

  const getIcon = () => {
    switch (reco.type) {
      case 'TRACTION': return <Target className="w-5 h-5 text-green-500" />;
      case 'STRATEGIC': return <TrendingUp className="w-5 h-5 text-blue-500" />;
      case 'ENGAGEMENT': return <Zap className="w-5 h-5 text-klando-gold" />;
      case 'QUALITY': return <ShieldAlert className="w-5 h-5 text-red-500" />;
    }
  };

  const getBadgeColor = () => {
    switch (reco.priority) {
      case 3: return "bg-red-500/10 text-red-500 border-red-500/20";
      case 2: return "bg-orange-500/10 text-orange-500 border-orange-500/20";
      default: return "bg-blue-500/10 text-blue-500 border-blue-500/20";
    }
  };

  const handleGoToTool = (tripId?: string) => {
    if (isTraction) {
      const tripParam = tripId ? `&selectedTrip=${tripId}` : '';
      router.push(`/marketing?tab=radar&id=${reco.target_id}${tripParam}`);
    } else {
      router.push(`/users?uid=${reco.target_id}`);
    }
  };

  const formatDate = (date: string | undefined) => {
    if (!date) return "--";
    try {
      return format(new Date(date), 'dd MMM', { locale: fr });
    } catch {
      return "Date invalide";
    }
  };

  const formatTime = (date: string | undefined) => {
    if (!date) return "--:--";
    try {
      return format(new Date(date), 'HH:mm');
    } catch {
      return "--:--";
    }
  };

  return (
    <Card className={cn(
      "bg-card/40 backdrop-blur-md border-white/5 transition-all duration-500 group relative overflow-hidden",
      !isApplied && "hover:border-klando-gold/30",
      isApplied && "opacity-75 border-green-500/20",
      isTraction && !isApplied && "md:col-span-2 lg:col-span-1"
    )}>
      <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
        {getIcon()}
      </div>
      
      <CardContent className="p-5 space-y-4 relative z-10">
        <div className="flex justify-between items-start">
          <div className="flex flex-col gap-1">
            <span className={cn("w-fit text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border", getBadgeColor())}>
              {reco.priority === 3 ? 'Urgent' : reco.priority === 2 ? 'Important' : 'Standard'}
            </span>
            <h4 className={cn(
                "font-black text-sm text-white uppercase tracking-tight transition-colors mt-1",
                !isApplied && "group-hover:text-klando-gold"
            )}>
                {reco.title}
            </h4>
          </div>
          <div className="flex flex-col items-end gap-1">
            {isApplied ? (
                <span className="flex items-center gap-1 text-[8px] font-black text-green-500 uppercase bg-green-500/10 px-2 py-0.5 rounded-md border border-green-500/20">
                    <Check className="w-2 h-2" /> Validé
                </span>
            ) : (
                <span className="text-[9px] font-bold text-muted-foreground/40 uppercase tabular-nums tracking-tighter text-right">
                   Scan: {formatDate(reco.created_at)}
                </span>
            )}
          </div>
        </div>

        {isTraction && content?.top_trips && content?.request && (
          <div className="space-y-3">
             <div className="bg-white/5 border border-white/5 rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <MapPin className="w-3 h-3 text-klando-gold" />
                    <span className="text-[11px] font-bold text-white uppercase tracking-tight">{content.request.origin} ➜ {content.request.destination}</span>
                </div>
                {content.request.has_ai_scan && (
                    <div className="flex items-center gap-1 text-[8px] font-black text-blue-400 uppercase bg-blue-500/10 px-1.5 py-0.5 rounded-md border border-blue-500/20" title={`Dernier scan IA: ${formatDate(content.request.last_ai_date)}`}>
                        <Sparkles className="w-2.5 h-2.5" /> IA OK
                    </div>
                )}
             </div>

             <div className="overflow-hidden rounded-xl border border-white/5 bg-black/20">
                <table className="w-full text-left text-[10px]">
                    <thead className="bg-white/5 text-muted-foreground font-black uppercase tracking-widest">
                        <tr>
                            <th className="px-3 py-2">Match</th>
                            <th className="px-3 py-2">Départ</th>
                            <th className="px-3 py-2 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {content.top_trips.map((trip: TripMatch) => (
                            <tr key={trip.id} className="hover:bg-white/5 transition-colors group/row">
                                <td className="px-3 py-2 font-bold text-white text-left">
                                    <div className="flex flex-col text-left">
                                        <span>{trip.id.split('-').pop()}</span>
                                        <span className="text-[8px] text-green-500">+{trip.dist.toFixed(1)}km</span>
                                    </div>
                                </td>
                                <td className="px-3 py-2 text-muted-foreground text-left">
                                    <div className="flex flex-col text-left">
                                        <span className="font-bold text-white/80">{formatTime(trip.time)}</span>
                                        <span className="text-[8px] uppercase">{formatDate(trip.time)}</span>
                                    </div>
                                </td>
                                <td className="px-3 py-2 text-right">
                                    <Button 
                                        variant="ghost" 
                                        size="icon" 
                                        onClick={() => handleGoToTool(trip.id)}
                                        className="h-6 w-6 rounded-md hover:bg-klando-gold hover:text-klando-dark"
                                    >
                                        <ArrowRight className="w-3 h-3" />
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
             </div>
             <p className="text-[9px] text-center text-muted-foreground font-bold uppercase tracking-widest py-1">
                {content.matches_count} trajet(s) correspondent au total
             </p>
          </div>
        )}

        {!isTraction && (
            <div className="bg-white/5 p-3 rounded-xl border border-white/5 text-left">
                <p className="text-[11px] text-muted-foreground leading-relaxed text-left font-medium">
                    {content?.alert || content?.reason || "Action recommandée par le système."}
                </p>
            </div>
        )}

        {!isApplied && (
          <div className="flex flex-col gap-2 pt-2 border-t border-white/5">
            <div className="flex gap-2">
              <Button 
                size="sm" 
                onClick={() => handleGoToTool()}
                className="flex-1 h-10 rounded-xl bg-slate-950 hover:bg-slate-900 text-white border border-white/10 font-black text-[10px] uppercase tracking-wider gap-2 transition-all shadow-inner"
              >
                <MapPin className="w-3.5 h-3.5 text-klando-gold" /> Voir Radar
              </Button>
              <Button 
                size="sm" 
                onClick={() => onApply(reco.id)}
                className="flex-1 h-10 rounded-xl bg-green-600 hover:bg-green-700 text-white font-black text-[10px] uppercase tracking-wider gap-2 shadow-lg shadow-green-500/20 transition-all"
              >
                <CheckSquare className="w-3.5 h-3.5" /> Valider Bloc
              </Button>
            </div>
            <div className="flex gap-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => onDismiss(reco.id)}
                  className="flex-1 h-8 rounded-xl text-muted-foreground hover:text-red-400 hover:bg-red-400/5 font-black text-[10px] uppercase gap-2 transition-all"
                >
                  <Trash2 className="w-3 h-3" /> Ignorer Opportunité
                </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
