"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession } from "next-auth/react";
import { cn } from "@/lib/utils";
import { Home, Car, Users, BarChart3, MessageSquare, Map, LifeBuoy, Shield, X } from "lucide-react";
import { UserMenu } from "@/components/user-menu";
import { Logo } from "@/components/logo";

const navItems = [
  { href: "/", label: "Accueil", icon: Home },
  { href: "/trips", label: "Trajets", icon: Car },
  { href: "/users", label: "Utilisateurs", icon: Users },
  { href: "/map", label: "Carte", icon: Map },
  { href: "/stats", label: "Statistiques", icon: BarChart3 },
  { href: "/chats", label: "Messages", icon: MessageSquare },
];

const adminItems = [
  { href: "/support", label: "Support", icon: LifeBuoy },
  { href: "/admin", label: "Administration", icon: Shield },
];

interface SidebarProps {
  onClose?: () => void;
  isMobile?: boolean;
}

export function Sidebar({ onClose, isMobile = false }: SidebarProps) {
  const pathname = usePathname();
  const { data: session } = useSession();
  const isAdmin = session?.user?.role === "admin";

  const handleLinkClick = () => {
    if (isMobile && onClose) {
      onClose();
    }
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
      
      <nav className={cn("flex-1", isMobile ? "p-2" : "p-4")}>
        <ul className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  onClick={handleLinkClick}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                    isActive
                      ? "bg-klando-burgundy text-white"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                    isMobile ? "text-base py-4" : "text-sm py-3"
                  )}
                >
                  <Icon className={cn("w-5 h-5", isMobile && "w-6 h-6")} />
                  <span className={cn(isMobile && "text-lg")}>{item.label}</span>
                </Link>
              </li>
            );
          })}

          {/* Section Admin - visible uniquement pour les admins */}
          {isAdmin && (
            <>
              <li className={cn("pt-4 pb-2", isMobile && "pt-6 pb-3")}>
                <span className={cn(
                  "px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider",
                  isMobile && "text-sm px-4"
                )}>
                  Admin
                </span>
              </li>
              {adminItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={handleLinkClick}
                      className={cn(
                        "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                        isActive
                          ? "bg-klando-burgundy text-white"
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                        isMobile ? "text-base py-4" : "text-sm py-3"
                      )}
                    >
                      <Icon className={cn("w-5 h-5", isMobile && "w-6 h-6")} />
                      <span className={cn(isMobile && "text-lg")}>{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </>
          )}
        </ul>
      </nav>
      
      {/* User Menu - adapté pour mobile */}
      <div className={cn("border-t border-border", isMobile ? "p-4" : "p-4")}>
        <UserMenu />
      </div>
    </aside>
  );
}
