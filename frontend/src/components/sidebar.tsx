"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import { cn } from "@/lib/utils";
import { 
  Home, Car, Users, BarChart3, Map, LifeBuoy, 
  Shield, X, Banknote, Globe, CheckSquare, 
  Sparkles, Loader2, TrendingUp, PenTool 
} from "lucide-react";
import { UserMenu } from "@/components/user-menu";
import { Logo } from "@/components/logo";
import { useState, useEffect } from "react";
import Image from "next/image";
import packageInfo from "../../package.json";

const navItems = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/trips", label: "Trajets", icon: Car },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/map", label: "Carte", icon: Map },
];

const supportItems = [
  { href: "/support", label: "Support", icon: LifeBuoy },
];

const marketingItems = [
  { href: "/marketing", label: "Marketing & Radar", icon: TrendingUp },
  { href: "/editorial", label: "Centre Éditorial", icon: PenTool },
];

const adminItems = [
  { href: "/admin/validation", label: "Validation", icon: CheckSquare },
  { href: "/transactions", label: "Transactions", icon: Banknote },
  { href: "/stats", label: "Statistiques", icon: BarChart3 },
  { href: "/admin", label: "Administration", icon: Shield },
];

interface SidebarProps {
  onClose?: () => void;
  isMobile?: boolean;
}

export function Sidebar({ onClose, isMobile = false }: SidebarProps) {
  const pathname = usePathname();
  const { data: session } = useSession();
  const userRole = session?.user?.role;
  const [loadingHref, setLoadingHref] = useState<string | null>(null);

  // Reset loading state when pathname changes
  useEffect(() => {
    setLoadingHref(null);
  }, [pathname]);

  const handleLinkClick = (href: string) => {
    if (href !== pathname) {
      setLoadingHref(href);
    }
    if (isMobile && onClose) {
      onClose();
    }
  };

  const renderNavItem = (item: { href: string, label: string, icon: React.ElementType | string }) => {
    const isActive = pathname === item.href;
    const isLoading = loadingHref === item.href;
    const isImageIcon = typeof item.icon === "string";
    const Icon = item.icon as React.ElementType;

    return (
      <li key={item.href}>
        <Link
          href={item.href}
          onClick={() => handleLinkClick(item.href)}
          className={cn(
            "flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-200 group relative overflow-hidden",
            isActive
              ? "bg-klando-burgundy text-white shadow-md shadow-klando-burgundy/20"
              : "text-muted-foreground hover:bg-white/5 hover:text-white",
            isMobile ? "text-base py-4" : "text-sm py-3",
            isLoading && "opacity-70 pointer-events-none bg-white/5"
          )}
        >
          <div className="flex items-center gap-3 relative z-10">
            <div className={cn(
              "w-8 h-8 flex items-center justify-center shrink-0",
              isMobile && "w-10 h-10"
            )}>
              {isImageIcon ? (
                <div className="w-full h-full relative transition-transform duration-300 group-hover:scale-110 flex items-center justify-center">
                  <Image 
                    src={item.icon as string} 
                    alt={item.label} 
                    fill 
                    className={cn(
                      "object-contain scale-125", 
                      !isActive && "grayscale opacity-70 group-hover:grayscale-0 group-hover:opacity-100 transition-all"
                    )}
                  />
                </div>
              ) : (
                <Icon className={cn(
                  "w-5 h-5 transition-transform duration-300 group-hover:scale-110", 
                  isMobile && "w-6 h-6",
                  isActive && "text-klando-gold"
                )} />
              )}
            </div>
            <span className={cn(isMobile && "text-lg", isActive && "font-bold")}>{item.label}</span>
          </div>
          
          {isLoading && (
            <Loader2 className="w-4 h-4 animate-spin text-klando-gold relative z-10" />
          )}
          
          {isActive && (
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-klando-gold rounded-full my-2" />
          )}
        </Link>
      </li>
    );
  };

  return (
    <aside className={cn(
      "bg-klando-dark border-r border-border flex flex-col",
      isMobile ? "w-full h-full" : "w-64"
    )}>
      {/* Header avec bouton close sur mobile */}
      <div className="p-2 border-b border-border flex justify-center items-center relative">
        <Logo size={isMobile ? "large" : "xlarge"} />
        {isMobile && onClose && (
          <button
            onClick={onClose}
            className="absolute right-2 p-2 text-white hover:text-klando-gold transition-colors rounded-lg hover:bg-klando-burgundy/20"
            aria-label="Fermer le menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
      
      <nav className={cn("flex-1 overflow-y-auto scrollbar-none", isMobile ? "p-2" : "p-4")}>
        <ul className="space-y-1">
          {navItems.map(renderNavItem)}

          {/* --- Section Marketing / Support / Admin --- */}
          {(userRole === "admin" || userRole === "support" || userRole === "marketing") && (
            <>
              <li className={cn("pt-6 pb-2", isMobile && "pt-8 pb-3")}>
                <span
                  className={cn(
                    "px-4 text-[10px] font-black text-muted-foreground/50 uppercase tracking-[0.2em]",
                    isMobile && "text-xs px-4"
                  )}
                >
                  {userRole === "admin" ? "Administration" : userRole === "marketing" ? "Marketing" : "Support"}
                </span>
              </li>

              {(userRole === "admin" || userRole === "marketing") && marketingItems.map(renderNavItem)}
              {(userRole === "admin" || userRole === "support") && supportItems.map(renderNavItem)}
              {userRole === "admin" && adminItems.map(renderNavItem)}
            </>
          )}
        </ul>
      </nav>
      
      {/* User Menu */}
      <div className={cn("border-t border-border bg-klando-dark/50 backdrop-blur-sm", isMobile ? "p-4" : "p-4")}>
        <UserMenu />
        <div className="mt-4 px-4 flex justify-between items-center opacity-30">
          <span className="text-[10px] font-black uppercase tracking-widest text-white">Version</span>
          <span className="text-[10px] font-mono text-white">v{packageInfo.version}</span>
        </div>
      </div>
    </aside>
  );
}
