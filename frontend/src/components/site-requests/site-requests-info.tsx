"use client";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { HelpCircle, Info } from "lucide-react";

export function SiteRequestsInfo() {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="text-klando-grizzly hover:text-klando-gold transition-colors">
          <HelpCircle className="w-5 h-5" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80 bg-klando-dark border-white/10 text-white p-4">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-klando-gold font-bold">
            <Info className="w-4 h-4" />
            <span>À quoi sert cette page ?</span>
          </div>
          <p className="text-sm text-klando-grizzly leading-relaxed">
            Cette page centralise les <strong>intentions de voyage</strong> soumises par les visiteurs du site vitrine Klando.
          </p>
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase text-white/50">Comment l&apos;utiliser :</h4>
            <ul className="text-xs space-y-2 list-disc pl-4 text-klando-grizzly">
              <li>
                <span className="text-white">Analyser :</span> Regardez les trajets les plus demandés.
              </li>
              <li>
                <span className="text-white">Contacter :</span> Utilisez les infos de contact pour appeler/écrire au client.
              </li>
              <li>
                <span className="text-white">Convertir :</span> Si vous avez un chauffeur disponible, proposez-lui le trajet.
              </li>
              <li>
                <span className="text-white">Statut :</span> Changez le statut pour suivre votre progression (Nouveau ➜ Examiné ➜ Contacté).
              </li>
            </ul>
          </div>
          <p className="text-[10px] text-white/30 italic border-t border-white/5 pt-2">
            Les données marquées &quot;site_&quot; proviennent du formulaire public.
          </p>
        </div>
      </PopoverContent>
    </Popover>
  );
}
