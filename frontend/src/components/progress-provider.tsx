"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import NProgress from "nprogress";
import "nprogress/nprogress.css";
import { Suspense } from "react";

// Configuration de NProgress
NProgress.configure({ 
  showSpinner: false,
  trickleSpeed: 200,
  minimum: 0.3
});

function ProgressHandler() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // On arrête la barre dès que le chemin change
    NProgress.done();
  }, [pathname, searchParams]);

  return null;
}

export function ProgressProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Intercepter tous les clics sur les liens Link de Next.js
    const handleAnchorClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const anchor = target.closest("a");

      if (
        anchor &&
        anchor.href &&
        anchor.target !== "_blank" &&
        !event.ctrlKey &&
        !event.metaKey &&
        !event.shiftKey &&
        !event.altKey &&
        anchor.origin === window.location.origin
      ) {
        // Si c'est un lien interne vers une URL différente
        if (anchor.href !== window.location.href) {
          NProgress.start();
        }
      }
    };

    document.addEventListener("click", handleAnchorClick);
    return () => document.removeEventListener("click", handleAnchorClick);
  }, []);

  return (
    <>
      <Suspense fallback={null}>
        <ProgressHandler />
      </Suspense>
      {children}
    </>
  );
}
