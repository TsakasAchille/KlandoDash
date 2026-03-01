"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/sidebar";
import { BackNavigation } from "@/components/navigation/BackNavigation";

export function LayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";
  const isIAPage = pathname === "/ia";
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Detection mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  // Page de login ou IA: pas de sidebar
  if (isLoginPage || isIAPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen relative">
      {/* Mobile: Menu burger et sidebar overlay */}
      {isMobile && (
        <>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="fixed top-4 left-4 z-50 p-3 bg-klando-burgundy text-white rounded-lg shadow-lg hover:bg-klando-burgundy/90 transition-colors"
            aria-label="Menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          {/* Overlay sombre */}
          {sidebarOpen && (
            <div 
              className="fixed inset-0 z-40 bg-black/50 transition-opacity"
              onClick={() => setSidebarOpen(false)}
            />
          )}
          
          {/* Sidebar mobile */}
          <div className={`fixed top-0 left-0 z-50 h-full w-72 bg-klando-dark transform transition-transform duration-300 ease-in-out ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}>
            <Sidebar onClose={() => setSidebarOpen(false)} isMobile={true} />
          </div>
        </>
      )}

      {/* Desktop: Sidebar fixe */}
      {!isMobile && <Sidebar />}
      
      {/* Contenu principal avec padding adaptatif */}
      <main className={`flex-1 overflow-auto transition-all duration-300 ${
        isMobile ? 'pt-20 px-4 pb-4' : 'p-6'
      } ${isMobile && sidebarOpen ? 'ml-0' : ''}`}>
        {/* On place le bouton de retour ICI, à l'intérieur du main, pour qu'il soit au-dessus du contenu sans créer de colonne flex */}
        <BackNavigation />
        {children}
      </main>
    </div>
  );
}
