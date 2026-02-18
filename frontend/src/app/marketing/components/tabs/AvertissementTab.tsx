"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ShieldAlert, Info, FileText, AlertTriangle } from "lucide-react";

export function AvertissementTab() {
  return (
    <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <Card className="bg-slate-900/50 border-klando-gold/20 backdrop-blur-xl rounded-[2.5rem] overflow-hidden shadow-2xl">
        <div className="bg-klando-gold/10 p-8 border-b border-klando-gold/10 flex items-center gap-4">
          <div className="p-3 bg-klando-gold/20 rounded-2xl">
            <ShieldAlert className="w-6 h-6 text-klando-gold" />
          </div>
          <div>
            <h2 className="text-xl font-black text-white uppercase tracking-tight">Avertissement Légal</h2>
            <p className="text-[10px] font-bold text-klando-gold uppercase tracking-[0.2em]">Lucky Oldstone PSI - Information Confidentielle</p>
          </div>
        </div>
        
        <CardContent className="p-10 space-y-6 text-sm leading-relaxed text-slate-300 font-medium text-left">
          <div className="bg-white/5 p-6 rounded-2xl border border-white/5 mb-8">
            <p className="font-bold text-white mb-4">
              Ce document à caractère promotionnel est établi par LUCKY OLDSTONE PSI pour information seulement.
            </p>
            <p>
              Sa remise à tout investisseur relève de la responsabilité de chaque commercialisateur, distributeur ou conseil. L’investisseur potentiel est invité à consulter un prestataire de services d’investissements, une société de gestion de portefeuilles/fortunes ou un conseiller en investissement avant d’investir dans les Actions non-cotés émises par la SAS en cours de constitution.
            </p>
          </div>

          <p>
            L’information contenue dans ce document n’est pas constitutive d’une recommandation d’investissement personnalisée, une offre ou une sollicitation d’acquérir les Actions non-cotés émises par la SAS en cours de constitution ni d’une offre de services d’investissement. 
            <span className="text-klando-gold/80 font-bold ml-1">
              Ce document n’est pas destiné aux citoyens ou résidents des Etats-Unis d’Amérique ou à des US Persons tel que ce terme est défini dans le Regulation S de la loi américaine de 1933 sur les valeurs mobilières.
            </span>
          </p>

          <p>
            L’information obtenue de la part de tierces parties est réputée être fiable et à jour, mais la précision de celle-ci ne peut être garantie. Ni la SAS en cours de constitution ni LUCKY OLDSTONE PSI ne peuvent s’engager au-delà de l’information qui leur a été remise, non plus qu’à actualiser l’information contenue dans ce document.
          </p>

          <div className="border-l-4 border-red-500/50 pl-6 my-8 italic text-slate-400">
            L’investisseur potentiel est informé que les Actions non cotées émises par la SAS en cours de constitution présentent des risques de pertes en capital, de concentration et de marché immobilier. Il lui appartient de lire leurs documents juridiques afin de les analyser et se forger sa propre opinion.
          </div>

          <p className="text-xs text-slate-400 border-t border-white/5 pt-6">
            Ce document est confidentiel et personnel, il ne doit pas être reproduit et/ou transmis en tout ou en partie, par quelque moyen que ce soit, électronique, mécanique ou autre... sans l’autorisation préalable de la SAS en cours de constitution et/ou de LUCKY OLDSTONE PSI.
          </p>

          <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-muted-foreground mt-4">
            <Info className="w-3 h-3" /> Source d’information : SAS en cours de constitution / Lucky Oldstone PSI
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
