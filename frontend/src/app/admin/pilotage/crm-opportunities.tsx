"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Users, 
  MapPin, 
  Clock, 
  MessageSquare, 
  TrendingUp, 
  AlertCircle,
  Sparkles,
  ArrowRight,
  UserCheck
} from "lucide-react";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

interface CRMOpportunitiesProps {
  data: {
    unmatched_demand: any[];
    empty_trips: any[];
    retention_alerts: any[];
  } | null;
}

export function CRMOpportunities({ data }: CRMOpportunitiesProps) {
  if (!data) return null;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-600 rounded-xl text-white shadow-lg shadow-indigo-200">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-black uppercase tracking-tight italic text-slate-900">Moteur d&apos;Actions CRM</h2>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Opportunités de croissance détectées par l&apos;IA</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* COLONNE 1: BESOIN D'OFFRE (Demande orpheline) */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-600 flex items-center gap-2 px-2">
            <UserCheck className="w-3.5 h-3.5" /> Demandes sans Match
          </h3>
          <div className="space-y-3">
            {data.unmatched_demand.length > 0 ? data.unmatched_demand.map((item, idx) => (
              <Card key={idx} className="border-none shadow-sm hover:shadow-md transition-all bg-white overflow-hidden group">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-1.5 text-xs font-black uppercase italic">
                        <span>{item.origin_city}</span>
                        <ArrowRight className="w-3 h-3 text-slate-300" />
                        <span>{item.destination_city}</span>
                      </div>
                      <span className="text-[9px] font-bold text-slate-400 mt-0.5">Premier départ le {format(new Date(item.earliest_date), 'dd/MM', { locale: fr })}</span>
                    </div>
                    <Badge className="bg-indigo-100 text-indigo-700 hover:bg-indigo-100 border-none font-black text-[10px]">{item.request_count} pers.</Badge>
                  </div>
                  <Button 
                    variant="outline" 
                    className="w-full h-8 rounded-lg text-[9px] font-black uppercase gap-2 border-indigo-100 text-indigo-600 hover:bg-indigo-50 hover:border-indigo-200"
                    onClick={() => window.open(`https://wa.me/?text=${encodeURIComponent(`Bonjour, nous avons une forte demande sur le trajet ${item.origin_city} -> ${item.destination_city}. Êtes-vous disponible pour publier un trajet ?`)}`, '_blank')}
                  >
                    <MessageSquare className="w-3 h-3" /> Trouver un conducteur
                  </Button>
                </CardContent>
              </Card>
            )) : (
              <p className="text-[10px] italic text-slate-400 text-center py-8">Aucune demande orpheline détectée.</p>
            )}
          </div>
        </div>

        {/* COLONNE 2: TRAJETS À REMPLIR (Offre à vide) */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-orange-600 flex items-center gap-2 px-2">
            <AlertCircle className="w-3.5 h-3.5" /> Urgence Remplissage
          </h3>
          <div className="space-y-3">
            {data.empty_trips.length > 0 ? data.empty_trips.map((item, idx) => (
              <Card key={idx} className="border-none shadow-sm hover:shadow-md transition-all bg-white overflow-hidden group border-l-4 border-l-orange-500">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-black text-orange-600 uppercase">Départ dans {Math.ceil((new Date(item.departure_schedule).getTime() - new Date().getTime()) / (1000 * 60 * 60))}h</span>
                      <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 truncate max-w-[180px]">
                        {item.departure_name.split(',')[0]} → {item.destination_name.split(',')[0]}
                      </div>
                    </div>
                    <Badge variant="outline" className="text-slate-400 border-slate-200 font-bold text-[9px]">{item.seats_available} places</Badge>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-slate-500 font-medium">
                    <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-[8px] font-black">{item.driver_name.substring(0, 2).toUpperCase()}</div>
                    <span>Cond: {item.driver_name}</span>
                  </div>
                  <Button 
                    className="w-full h-8 rounded-lg text-[9px] font-black uppercase gap-2 bg-orange-600 hover:bg-orange-700 text-white shadow-lg shadow-orange-100"
                    onClick={() => window.open(`https://wa.me/?text=${encodeURIComponent(`Bonjour ${item.driver_name}, nous allons pousser votre trajet de demain vers nos passagers pour vous aider à le remplir !`)}`, '_blank')}
                  >
                    <Sparkles className="w-3 h-3" /> Pousser aux passagers
                  </Button>
                </CardContent>
              </Card>
            )) : (
              <p className="text-[10px] italic text-slate-400 text-center py-8">Tous les trajets proches sont remplis.</p>
            )}
          </div>
        </div>

        {/* COLONNE 3: FIDÉLISATION (Rétention) */}
        <div className="space-y-4">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-600 flex items-center gap-2 px-2">
            <TrendingUp className="w-3.5 h-3.5" /> Rétention VIP
          </h3>
          <div className="space-y-3">
            {data.retention_alerts.length > 0 ? data.retention_alerts.map((item, idx) => (
              <Card key={idx} className="border-none shadow-sm hover:shadow-md transition-all bg-white overflow-hidden group border-l-4 border-l-emerald-500">
                <CardContent className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <span className="text-xs font-black text-slate-900 uppercase tracking-tight">{item.display_name}</span>
                      <span className="text-[9px] font-bold text-slate-400 mt-0.5 italic">Inactif depuis 14 jours</span>
                    </div>
                    <Badge className="bg-emerald-100 text-emerald-700 border-none font-black text-[9px] italic">{item.total_lifetime_trips} trajets total</Badge>
                  </div>
                  <Button 
                    variant="ghost"
                    className="w-full h-8 rounded-lg text-[9px] font-black uppercase gap-2 text-emerald-600 hover:bg-emerald-50"
                    onClick={() => window.open(`https://wa.me/${item.phone_number.replace(/\D/g, '')}?text=${encodeURIComponent(`Bonjour ${item.display_name}, vous nous manquez sur Klando ! Vos passagers habituels attendent vos prochains trajets.`)}`, '_blank')}
                  >
                    <MessageSquare className="w-3 h-3" /> Relance personnalisée
                  </Button>
                </CardContent>
              </Card>
            )) : (
              <p className="text-[10px] italic text-slate-400 text-center py-8">Tes top conducteurs sont tous actifs !</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
