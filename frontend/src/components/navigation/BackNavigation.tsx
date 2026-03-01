"use client";

import { useRouter, usePathname } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export function BackNavigation() {
  const router = useRouter();
  const pathname = usePathname();
  const [canGoBack, setCanGoBack] = useState(false);

  useEffect(() => {
    // Dans une SPA Next.js, on peut vérifier si l'historique a plus d'une entrée
    // pour ne pas afficher le bouton sur la page d'entrée directe.
    if (typeof window !== "undefined" && window.history.length > 1) {
      // On évite d'afficher le bouton sur les pages "racines" du dashboard
      const rootPages = ['/', '/map', '/users', '/trips', '/support', '/transactions', '/marketing', '/editorial', '/admin/logs', '/chats'];
      
      if (!rootPages.includes(pathname)) {
        setCanGoBack(true);
      } else {
        // Optionnel: On peut aussi vérifier si on a des query params (ex: ?selected=123)
        // Si oui, on est dans un "détail" même sur une page racine
        // SAUF pour l'éditorial où les query params servent juste aux onglets
        if (window.location.search && pathname !== '/editorial') {
            setCanGoBack(true);
        } else {
            setCanGoBack(false);
        }
      }
    }
  }, [pathname]);

  if (!canGoBack) return null;

  return (
    <div className="mb-2 animate-in fade-in slide-in-from-left-4 duration-500 hidden lg:block">
      <Button
        variant="outline"
        size="sm"
        onClick={() => router.back()}
        className="bg-white/50 backdrop-blur-sm border-slate-200 shadow-sm rounded-xl gap-2 font-black uppercase text-[10px] tracking-widest hover:bg-white hover:border-klando-gold transition-all group h-8"
      >
        <div className="p-0.5 bg-slate-100 rounded-md group-hover:bg-klando-gold/20 transition-colors">
            <ChevronLeft className="w-3.5 h-3.5 text-slate-600 group-hover:text-klando-dark" />
        </div>
        Retour
      </Button>
    </div>
  );
}
