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
import { ChangelogModal } from "@/components/changelog-modal";
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
            "flex items-center justify-between px-4 py-3 rounded-2xl transition-all duration-500 group relative overflow-hidden mb-1.5",
            isActive
              ? "bg-gradient-to-r from-klando-burgundy via-[#9b2c3d] to-klando-burgundy text-white shadow-[0_8px_20px_-4px_rgba(123,31,47,0.4)]"
              : "text-slate-400 hover:bg-white/[0.03] hover:text-white hover:translate-x-1",
            isMobile ? "text-base py-4" : "text-sm py-2.5",
            isLoading && "opacity-70 pointer-events-none bg-white/5"
          )}
        >
          {/* Active Glow Effect */}
          {isActive && (
            <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-50 animate-pulse" />
          )}

          <div className="flex items-center gap-3 relative z-10">
            <div className={cn(
              "w-9 h-9 flex items-center justify-center shrink-0 rounded-xl transition-all duration-500",
              isActive ? "bg-white/20 shadow-inner" : "bg-white/[0.02] group-hover:bg-white/10",
              isMobile && "w-10 h-10"
            )}>
              {isImageIcon ? (
                <div className="w-full h-full relative transition-transform duration-500 group-hover:scale-110 flex items-center justify-center">
                  <Image 
                    src={item.icon as string} 
                    alt={item.label} 
                    fill 
                    className={cn(
                      "object-contain scale-125", 
                      !isActive && "grayscale opacity-70 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-500"
                    )}
                    sizes="36px"
                  />
                </div>
              ) : (
                <Icon className={cn(
                  "w-[18px] h-[18px] transition-all duration-500 group-hover:rotate-[10deg] group-hover:scale-110", 
                  isMobile && "w-5 h-5",
                  isActive ? "text-klando-gold drop-shadow-[0_0_8px_rgba(235,195,63,0.5)]" : "text-slate-500 group-hover:text-white"
                )} />
              )}
            </div>
            <span className={cn(
              "transition-all duration-500 tracking-tight",
              isMobile && "text-lg", 
              isActive ? "font-black text-white" : "font-semibold group-hover:translate-x-0.5"
            )}>{item.label}</span>
          </div>
          
          {isLoading && (
            <Loader2 className="w-4 h-4 animate-spin text-klando-gold relative z-10" />
          )}
          
          {isActive && (
            <div className="absolute right-3 w-1.5 h-1.5 bg-klando-gold rounded-full shadow-[0_0_12px_rgba(235,195,63,1)]" />
          )}
        </Link>
      </li>
    );
  };

  return (
    <aside className={cn(
      "bg-[#061428] border-r border-white/5 flex flex-col shadow-[10px_0_30px_-5px_rgba(0,0,0,0.3)] relative",
      isMobile ? "w-full h-full" : "w-64"
    )}>
      {/* Visual Depth Overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(123,31,47,0.08),transparent_40%)] pointer-events-none" />
      
      {/* Header Area */}
      <div className="p-8 border-b border-white/5 flex justify-center items-center relative bg-black/10 backdrop-blur-md">
        <div className="relative group/logo cursor-pointer">
            <div className="absolute -inset-4 bg-klando-gold/10 rounded-full blur-xl opacity-0 group-hover/logo:opacity-100 transition-opacity duration-700" />
            <Logo size={isMobile ? "large" : "xlarge"} />
        </div>
        {isMobile && onClose && (
          <button
            onClick={onClose}
            className="absolute right-4 p-2 text-white/50 hover:text-klando-gold transition-colors rounded-xl bg-white/5"
            aria-label="Fermer le menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
      
      <nav className={cn("flex-1 overflow-y-auto scrollbar-none relative z-10", isMobile ? "p-4" : "p-4")}>
        <ul className="space-y-1">
          {navItems.map(renderNavItem)}

          {/* --- Section Marketing / Support / Admin --- */}
          {(userRole === "admin" || userRole === "support" || userRole === "marketing") && (
            <>
              <li className={cn("pt-8 pb-3", isMobile && "pt-10 pb-4")}>
                <div className="flex items-center gap-3 px-4">
                  <div className="h-px flex-1 bg-white/5" />
                  <span
                    className={cn(
                      "text-[9px] font-black text-slate-500 uppercase tracking-[0.3em] whitespace-nowrap",
                      isMobile && "text-xs"
                    )}
                  >
                    {userRole === "admin" ? "Espace Admin" : userRole === "marketing" ? "Espace Marketing" : "Espace Support"}
                  </span>
                  <div className="h-px flex-1 bg-white/5" />
                </div>
              </li>

              {(userRole === "admin" || userRole === "marketing") && marketingItems.map(renderNavItem)}
              {(userRole === "admin" || userRole === "support") && supportItems.map(renderNavItem)}
              {userRole === "admin" && adminItems.map(renderNavItem)}
            </>
          )}
        </ul>
      </nav>
      
      {/* User Menu */}
      <div className={cn("border-t border-white/5 bg-klando-dark/40 backdrop-blur-xl relative z-10", isMobile ? "p-6" : "p-4")}>
        <UserMenu />
        <div className="mt-4 px-4 flex justify-between items-center group/version">
          <span className="text-[9px] font-black uppercase tracking-[0.2em] text-slate-500">KlandoDash Core</span>
          <ChangelogModal version={packageInfo.version} />
        </div>
      </div>
    </aside>
  );
}
