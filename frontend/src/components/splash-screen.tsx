"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export function SplashScreen() {
  const [isVisible, setIsVisible] = useState(true);
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    // On simule un chargement de 2 secondes pour l'effet visuel
    const timer = setTimeout(() => {
      setIsFadingOut(true);
      setTimeout(() => setIsVisible(false), 500); // Durée du fade out
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  if (!isVisible) return null;

  return (
    <div 
      className={cn(
        "fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#081C36] transition-opacity duration-500 ease-in-out",
        isFadingOut ? "opacity-0 pointer-events-none" : "opacity-100"
      )}
    >
      <div className="relative w-64 h-32 md:w-80 md:h-40">
        {/* Logo Gris (Fond) */}
        <div className="absolute inset-0 opacity-20 grayscale brightness-200">
          <Image
            src="/logo-klando-sans-fond.png"
            alt="Klando"
            fill
            className="object-contain"
            priority
            unoptimized
            sizes="(max-width: 768px) 256px, 320px"
          />
        </div>

        {/* Logo qui se remplit (Animation définie dans globals.css) */}
        <div className="absolute inset-0 animate-fill-logo overflow-hidden">
          <Image
            src="/logo-klando-sans-fond.png"
            alt="Klando"
            fill
            className="object-contain"
            priority
            unoptimized
            sizes="(max-width: 768px) 256px, 320px"
          />
        </div>
      </div>

      <div className="mt-8 flex flex-col items-center space-y-3">
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-klando-gold animate-pulse">
          Chargement de KlandoDash
        </p>
        <div className="w-40 h-1 bg-white/5 rounded-full overflow-hidden">
            <div className="h-full bg-klando-gold animate-progress-bar" />
        </div>
      </div>
    </div>
  );
}
