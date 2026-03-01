"use client";

import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export function BackNavigation() {
  const router = useRouter();
  const [canGoBack, setCanGoBack] = useState(false);

  useEffect(() => {
    // Dans une SPA Next.js, on peut vérifier si l'historique a plus d'une entrée
    // pour ne pas afficher le bouton sur la page d'entrée directe.
    if (typeof window !== "undefined" && window.history.length > 1) {
      setCanGoBack(true);
    }
  }, []);

  if (!canGoBack) return null;

  return (
    <div className="fixed top-4 left-[280px] z-[100] animate-in fade-in slide-in-from-left-4 duration-500 hidden lg:block">
      <Button
        variant="outline"
        size="sm"
        onClick={() => router.back()}
        className="bg-white/80 backdrop-blur-md border-slate-200 shadow-xl rounded-xl gap-2 font-black uppercase text-[10px] tracking-widest hover:bg-white hover:border-klando-gold transition-all group"
      >
        <div className="p-1 bg-slate-100 rounded-lg group-hover:bg-klando-gold/20 transition-colors">
            <ChevronLeft className="w-3.5 h-3.5 text-slate-600 group-hover:text-klando-dark" />
        </div>
        Retour
      </Button>
    </div>
  );
}
