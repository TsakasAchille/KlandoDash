"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Target, TrendingUp, Zap, ShieldAlert, MapPin, ArrowRight, CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";

export type RecommendationType = 'TRACTION' | 'STRATEGIC' | 'ENGAGEMENT' | 'QUALITY';

export interface AIRecommendation {
  id: string;
  type: RecommendationType;
  priority: number;
  title: string;
  content: any;
  target_id: string;
  status: 'PENDING' | 'APPLIED' | 'DISMISSED';
  created_at: string;
}

interface RecommendationCardProps {
  reco: AIRecommendation;
  onApply: (id: string) => void;
  onDismiss: (id: string) => void;
}

export function RecommendationCard({ reco, onApply, onDismiss }: RecommendationCardProps) {
  const router = useRouter();

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

  // Logique de redirection intelligente
  const handleAction = () => {
    onApply(reco.id); // Marque comme appliqué en DB

    switch (reco.type) {
      case 'TRACTION':
        // Redirige vers la carte avec la demande et le trajet pré-sélectionnés
        const tripParam = reco.content.best_trip_id ? `&selectedTrip=${reco.content.best_trip_id}` : '';
        router.push(`/site-requests?tab=map&id=${reco.target_id}${tripParam}`);
        break;
      case 'QUALITY':
        // Redirige vers la fiche de l'utilisateur pour validation
        router.push(`/users?uid=${reco.target_id}`);
        break;
      case 'ENGAGEMENT':
        // On pourrait imaginer une page de messagerie ou de notifications
        router.push(`/users?uid=${reco.target_id}`);
        break;
      default:
        // Par défaut, on reste sur la page
        break;
    }
  };

  return (
    <Card className="bg-card/40 backdrop-blur-md border-white/5 hover:border-klando-gold/30 transition-all duration-500 group relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
        {getIcon()}
      </div>
      
      <CardContent className="p-6 space-y-4 relative z-10">
        <div className="flex justify-between items-start">
          <span className={cn("text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest border", getBadgeColor())}>
            {reco.priority === 3 ? 'Priorité Haute' : reco.priority === 2 ? 'Priorité Moyenne' : 'Standard'}
          </span>
          <span className="text-[10px] font-bold text-muted-foreground/40 uppercase tabular-nums">
            {new Date(reco.created_at).toLocaleDateString('fr-FR')}
          </span>
        </div>

        <div className="min-h-[80px]">
          <h4 className="font-black text-sm text-white uppercase tracking-tight group-hover:text-klando-gold transition-colors">{reco.title}</h4>
          
          <div className="mt-3 space-y-2">
            {reco.type === 'TRACTION' && (
              <>
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                  <MapPin className="w-3 h-3 text-klando-gold" /> {reco.content.route}
                </div>
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                  <CheckCircle2 className="w-3 h-3 text-green-500" /> {reco.content.match_count} match(es) trouvés
                </div>
              </>
            )}
            
            {reco.type === 'ENGAGEMENT' && (
              <div className="text-[11px] text-muted-foreground italic leading-relaxed bg-white/5 p-2 rounded-lg">
                "{reco.content.reason}"
              </div>
            )}

            {reco.type === 'QUALITY' && (
              <div className="text-[11px] text-red-400 bg-red-500/5 p-2 rounded-lg border border-red-500/10">
                {reco.content.alert}
              </div>
            )}

            {reco.type === 'STRATEGIC' && (
              <div className="text-[11px] text-blue-400 bg-blue-500/5 p-2 rounded-lg border border-blue-500/10">
                {reco.content.reason}
              </div>
            )}
          </div>
        </div>

        <div className="flex gap-2 pt-2">
          <Button 
            size="sm" 
            onClick={handleAction}
            className="flex-1 h-9 rounded-xl bg-klando-gold hover:bg-klando-gold/90 text-klando-dark font-black text-[10px] uppercase tracking-wider"
          >
            Agir Maintenant <ArrowRight className="w-3 h-3 ml-2" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => onDismiss(reco.id)}
            className="h-9 px-3 rounded-xl text-muted-foreground hover:text-white hover:bg-white/5 font-black text-[10px] uppercase"
          >
            Ignorer
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
